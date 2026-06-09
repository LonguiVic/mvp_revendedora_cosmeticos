import requests
import logging
from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.whatsapp_message import (
    WhatsappMessage
)
from app.services.message_processor import (
    MessageProcessorService
)
from app.services.pending_confirmation_service import (
    PendingConfirmationService
)
from app.services.sale_confirmation_service import SaleConfirmationService
from app.models.pending_confirmation import PendingConfirmation
from app.config.settings import settings


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

router = APIRouter()
pending_service = (
    PendingConfirmationService()
)

def enviar_mensagem_whatsapp(numero_destino: str, texto: str):
    url = "http://localhost:8081/message/sendText/revendedora-jheni"
    
    payload = {
        "number": numero_destino,
        "text": texto
    }
    
    headers = {
        "apikey": settings.evolution_api_key, 
        "Authorization": f"Bearer {settings.evolution_api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem para {numero_destino}: {e}")
        if hasattr(e, 'response') and e.response is not None:
             logger.error(e.response.text)


def enviar_confirmacao_whatsapp(numero_destino: str, pending_id: int, sale):
    url = "http://localhost:8081/message/sendText/revendedora-jheni"
    
    marca = sale.marca.value if hasattr(sale.marca, 'value') else sale.marca
    
    texto_venda = (
        f"✅ *Venda Identificada!*\n\n"
        f"👤 *Cliente:* {sale.cliente}\n"
        f"📦 *Produto:* {sale.quantidade}x {sale.produto} ({marca})\n"
        f"💰 *Valor:* R$ {sale.valor_total:.2f}\n"
        f"📉 *Custo:* R$ {sale.custo_total:.2f}\n\n"
        f"Confirma o registro do pedido #{pending_id}?\n"
        f"Responda *SIM* ou *NÃO*"
    )

    payload = {
        "number": numero_destino,
        "text": texto_venda
    }

    headers = {
        "apikey": settings.evolution_api_key, 
        "Authorization": f"Bearer {settings.evolution_api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logger.info("Mensagem de confirmação enviada com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao enviar confirmação: {e}")
        if hasattr(e, 'response') and e.response is not None:
             logger.error(e.response.text)


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(
    payload: dict,
    db: Session = Depends(get_db)
):
    if payload.get("event") != "messages.upsert":
        return {"success": True}

    data = payload.get("data", {})
    key = data.get("key", {})
    remote_jid = key.get("remoteJid", "")

    if remote_jid != settings.grupo_vendas_id:
        return {"success": True}

    message_data = data.get("message", {})
    texto_mensagem = message_data.get("conversation")

    if not texto_mensagem and "extendedTextMessage" in message_data:
        texto_mensagem = message_data["extendedTextMessage"].get("text")

    if not texto_mensagem:
        return {"success": True}
    
    texto_limpo = texto_mensagem.strip().upper()

    if texto_limpo in ["SIM", "NAO", "NÃO"]:
        
        pending = db.query(PendingConfirmation).filter(
            PendingConfirmation.customer_phone == remote_jid,
            PendingConfirmation.confirmed == False
        ).order_by(PendingConfirmation.created_at.desc()).first()

        if not pending:
            enviar_mensagem_whatsapp(
                numero_destino=remote_jid, 
                texto="⚠️ Não encontrei nenhuma venda pendente para confirmar no momento."
            )
            return {"success": True}

        if texto_limpo == "SIM":
            try:
                confirmation_service = SaleConfirmationService()
                sale = confirmation_service.confirm(
                    db=db, 
                    confirmation_id=pending.id
                )
                
                msg_sucesso = (
                    f"🎉 *Venda Registrada com Sucesso!*\n\n"
                    f"🔖 *Código:* {sale.sale_code}\n"
                    f"As parcelas e o lucro já foram calculados e salvos no banco de dados."
                )
                enviar_mensagem_whatsapp(numero_destino=remote_jid, texto=msg_sucesso)
                logger.info(f"Venda {sale.sale_code} confirmada no banco!")
                
            except Exception as e:
                logger.error(f"Erro ao confirmar venda no banco: {e}")
                enviar_mensagem_whatsapp(
                    numero_destino=remote_jid, 
                    texto="❌ Ocorreu um erro interno ao salvar a venda."
                )
                
        else:
            db.delete(pending)
            db.commit()
            enviar_mensagem_whatsapp(
                numero_destino=remote_jid, 
                texto="Venda cancelada. Os dados foram descartados."
            )

        return {"success": True}

    message = WhatsappMessage(
        phone=remote_jid,
        message_text=texto_mensagem
    )

    db.add(message)
    db.commit()

    processor = MessageProcessorService()

    try:

        sale = processor.process(
            texto_mensagem
        )

        if sale:

            pending = (
                pending_service.create(
                    db=db,
                    payload=sale.model_dump(),
                    customer_phone=remote_jid
                )
            )

            logger.info(
                f"VENDA IDENTIFICADA - Confirmation ID: {pending.id}"
            )

            logger.info(
                sale.model_dump()
            )

            enviar_confirmacao_whatsapp(
                numero_destino=remote_jid, 
                pending_id=pending.id, 
                sale=sale
            )

        else:

            logger.warning(
                "Mensagem comum."
            )

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        
        mensagem_erro = (f"Erro ao processar mensagem: {e}")
        enviar_mensagem_whatsapp(
            numero_destino=remote_jid,
            texto=mensagem_erro
        )


    logger.info("=" * 80)
    logger.info(f"Cliente: {remote_jid}")
    logger.info(f"Mensagem: {texto_mensagem}")
    logger.info("=" * 80)

    return {"success": True}