import requests
import logging
from datetime import datetime
from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.session import get_db
from app.models.whatsapp_message import WhatsappMessage
from app.services.message_processor import MessageProcessorService
from app.services.pending_confirmation_service import PendingConfirmationService
from app.services.sale_confirmation_service import SaleConfirmationService
from app.services.query_service import QueryService
from app.services.payment_service import PaymentService
from app.services.cancel_sale_service import CancelSaleService
from app.services.sale_service import SaleService
from app.services.edit_sale_service import EditSaleService
from app.models.pending_confirmation import PendingConfirmation
from app.models.installment import Installment
from app.models.sale import Sale
from app.config.settings import settings
from app.schemas.intent_extraction import Intent

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

router = APIRouter()
pending_service = PendingConfirmationService()
query_service = QueryService()
payment_service = PaymentService()
cancel_service = CancelSaleService()
sale_service = SaleService()
edit_sale_service = EditSaleService()

MONTH_MAP = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
    "este mes": datetime.now().month, "esse mes": datetime.now().month, "mes atual": datetime.now().month
}

def parse_month(mes_str):
    if not mes_str: return None
    mes_str = mes_str.lower().strip()
    if mes_str in MONTH_MAP: return MONTH_MAP[mes_str]
    try: return int(mes_str)
    except: return None

def enviar_mensagem_whatsapp(numero_destino: str, texto: str):
    url = "http://localhost:8081/message/sendText/revendedora-jheni"
    payload = {"number": numero_destino, "text": texto}
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
    itens_str = ""
    for item in sale.itens:
        marca = item.marca.value if hasattr(item.marca, 'value') else item.marca
        itens_str += f"\n- {item.quantidade}x {item.produto} ({marca})"

    texto_venda = (
        f"✅ *Venda Identificada!*\n\n"
        f"👤 *Cliente:* {sale.cliente}"
        f"{itens_str}\n\n"
        f"💰 *Valor:* R$ {sale.valor_total:.2f}\n"
        f"📈 *Custo:* R$ {sale.custo_total:.2f}\n\n"
        f"Confirma o registro do pedido #{pending_id}?\n"
        f"Responda *SIM* ou *NÃO*"
    )
    enviar_mensagem_whatsapp(numero_destino, texto_venda)

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(payload: dict, db: Session = Depends(get_db)):
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

    # Fluxo de Confirmação (SIM/NÃO)
    if texto_limpo in ["SIM", "NAO", "NÃO"]:
        pending = db.query(PendingConfirmation).filter(
            PendingConfirmation.customer_phone == remote_jid,
            PendingConfirmation.confirmed == False
        ).order_by(PendingConfirmation.created_at.desc()).first()

        if not pending:
            enviar_mensagem_whatsapp(remote_jid, "⚠️ Não encontrei nenhuma ação pendente para confirmar no momento.")
            return {"success": True}

        action = pending.payload.get("action", "SALE")

        if texto_limpo == "SIM":
            try:
                if action == "SALE":
                    confirmation_service = SaleConfirmationService()
                    sale = confirmation_service.confirm(db=db, confirmation_id=pending.id)
                    msg_sucesso = (
                        f"🎉 *Venda Registrada com Sucesso!*\n\n"
                        f"🔖 *Código:* {sale.sale_code}\n"
                        f"As parcelas e o lucro já foram calculados."
                    )
                    enviar_mensagem_whatsapp(remote_jid, msg_sucesso)
                elif action == "CANCEL":
                    sale_code = pending.payload.get("sale_code")
                    sale = db.query(Sale).filter(Sale.sale_code == sale_code).first()
                    cancel_service.cancel(db, sale.id)
                    enviar_mensagem_whatsapp(remote_jid, f"✅ Venda {sale_code} e suas parcelas foram canceladas.")
                    pending.confirmed = True
                    db.commit()
                elif action == "REMOVE_ITEM":
                    sale_id = pending.payload.get("sale_id")
                    produto = pending.payload.get("produto")
                    edit_sale_service.remove_item(db, sale_id, produto)
                    enviar_mensagem_whatsapp(remote_jid, f"✅ Item '{produto}' removido com sucesso da venda e parcelas recalculadas.")
                    pending.confirmed = True
                    db.commit()
            except Exception as e:
                logger.error(f"Erro ao confirmar ação: {e}")
                enviar_mensagem_whatsapp(remote_jid, f"❌ Ocorreu um erro interno: {e}")
        else:
            db.delete(pending)
            db.commit()
            enviar_mensagem_whatsapp(remote_jid, "Ação cancelada. Os dados foram descartados.")

        return {"success": True}

    # Registro da Mensagem
    message = WhatsappMessage(phone=remote_jid, message_text=texto_mensagem)
    db.add(message)
    db.commit()

    # Processamento de Intenções
    processor = MessageProcessorService()
    try:
        result = processor.process(texto_mensagem)
        intent = result["intent"]
        intent_data = result["data"]

        if intent == Intent.REGISTRAR_VENDA and result["sale"]:
            sale = result["sale"]
            payload_data = sale.model_dump()
            payload_data["action"] = "SALE"
            pending = pending_service.create(db=db, payload=payload_data, customer_phone=remote_jid)
            enviar_confirmacao_whatsapp(remote_jid, pending.id, sale)

        elif intent == Intent.CONSULTAR_RECEBIMENTOS:
            month = datetime.now().month
            year = datetime.now().year
            res = query_service.get_receivables(db, month, year)
            msg = f"Você possui R$ {res['total']:.2f} para receber este mês.\n\n"
            for c in res['clients']:
                msg += f"{c['cliente']} — R$ {c['valor']:.2f}\n"
            enviar_mensagem_whatsapp(remote_jid, msg.strip())

        elif intent == Intent.CONSULTAR_DIVIDA:
            if intent_data.cliente:
                res = query_service.get_customer_debts(db, intent_data.cliente)
                if not res["parcelas"]:
                    msg = f"{intent_data.cliente} não possui parcelas pendentes."
                else:
                    msg = f"{intent_data.cliente} possui as seguintes parcelas pendentes:\n\n"
                    for p in res["parcelas"]:
                        msg += f"Mês {p['mes']}/{p['ano']} — R$ {p['valor']:.2f}\n"
                enviar_mensagem_whatsapp(remote_jid, msg.strip())
            else:
                enviar_mensagem_whatsapp(remote_jid, "Por favor, especifique o nome do cliente.")

        elif intent == Intent.CONSULTAR_PROXIMAS_COBRANCAS:
            month = datetime.now().month
            year = datetime.now().year
            res = query_service.get_receivables(db, month, year)
            msg = "Clientes pendentes neste mês:\n\n"
            for c in res['clients']:
                msg += f"{c['cliente']} — R$ {c['valor']:.2f}\n"
            enviar_mensagem_whatsapp(remote_jid, msg.strip())

        elif intent == Intent.CONSULTAR_LUCRO:
            month = datetime.now().month
            year = datetime.now().year
            res = query_service.get_monthly_profit(db, month, year)
            msg = (f"Receita: R$ {res['revenue']:.2f}\n"
                   f"Custos: R$ {res['cost']:.2f}\n"
                   f"Lucro: R$ {res['profit']:.2f}")
            enviar_mensagem_whatsapp(remote_jid, msg)

        elif intent == Intent.REGISTRAR_PAGAMENTO:
            if intent_data.cliente:
                installments = db.query(Installment).join(Sale).filter(
                    Sale.customer_name.ilike(f"%{intent_data.cliente}%"),
                    Installment.status == "PENDING"
                ).order_by(Installment.due_year, Installment.due_month).all()

                if not installments:
                    enviar_mensagem_whatsapp(remote_jid, f"Não encontrei parcelas pendentes para {intent_data.cliente}.")
                else:
                    payment_service.register_payment(db, installments[0].id)
                    enviar_mensagem_whatsapp(remote_jid, f"Pagamento de {intent_data.cliente} registrado com sucesso!")
            else:
                 enviar_mensagem_whatsapp(remote_jid, "Por favor, especifique o nome do cliente que pagou.")

        elif intent == Intent.CANCELAR_VENDA:
            sale_code = intent_data.sale_code
            sale_obj = None

            if sale_code:
                sale_obj = db.query(Sale).filter(Sale.sale_code == sale_code, Sale.status == 'ACTIVE').first()
            elif intent_data.cliente:
                sale_obj = db.query(Sale).filter(Sale.customer_name.ilike(f"%{intent_data.cliente}%"), Sale.status == 'ACTIVE').order_by(desc(Sale.created_at)).first()

            if sale_obj:
                payload_data = {"action": "CANCEL", "sale_code": sale_obj.sale_code}
                pending_service.create(db=db, payload=payload_data, customer_phone=remote_jid)
                msg = (f"Encontrei a venda {sale_obj.sale_code} de {sale_obj.customer_name} no valor de R$ {sale_obj.sale_value:.2f}.\n\n"
                       f"Isso irá cancelar todas as parcelas associadas e remover a venda dos cálculos de lucro.\n\n"
                       f"Deseja continuar?\n\nResponda *SIM* ou *NÃO*")
                enviar_mensagem_whatsapp(remote_jid, msg)
            else:
                enviar_mensagem_whatsapp(remote_jid, "Não encontrei nenhuma venda ativa com esses dados.")

        elif intent == Intent.CONSULTAR_VENDAS:
            month = parse_month(intent_data.mes)
            sales = sale_service.list_sales(db, status="ACTIVE", customer_name=intent_data.cliente, month=month, forma_pagamento=intent_data.forma_pagamento)
            if not sales:
                enviar_mensagem_whatsapp(remote_jid, "Não encontrei vendas com esses critérios.")
            else:
                msg = f"Encontrei {len(sales)} venda(s):\n\n"
                for s in sales:
                    msg += f"👤 {s['cliente']} - R$ {s['valor_venda']:.2f} ({s['parcelas']}x)\n"
                enviar_mensagem_whatsapp(remote_jid, msg.strip())

        elif intent == Intent.REMOVER_ITEM_VENDA:
            if not intent_data.cliente or not intent_data.produto:
                enviar_mensagem_whatsapp(remote_jid, "Por favor, informe o nome do cliente e o produto que deseja remover.")
            else:
                sale_obj = db.query(Sale).filter(Sale.customer_name.ilike(f"%{intent_data.cliente}%"), Sale.status == 'ACTIVE').order_by(desc(Sale.created_at)).first()
                if not sale_obj:
                    enviar_mensagem_whatsapp(remote_jid, f"Não encontrei vendas ativas para {intent_data.cliente}.")
                else:
                    payload_data = {"action": "REMOVE_ITEM", "sale_id": sale_obj.id, "produto": intent_data.produto}
                    pending_service.create(db=db, payload=payload_data, customer_phone=remote_jid)
                    msg = (f"Encontrei a venda {sale_obj.sale_code} de {sale_obj.customer_name}.\n"
                           f"Você deseja remover '{intent_data.produto}' dessa venda e recalcular as parcelas?\n\n"
                           f"Responda *SIM* ou *NÃO*")
                    enviar_mensagem_whatsapp(remote_jid, msg)

        else:
            enviar_mensagem_whatsapp(remote_jid, "Desculpe, não entendi o comando. Pode reformular?")

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        enviar_mensagem_whatsapp(remote_jid, f"Erro ao processar mensagem: {e}")

    return {"success": True}
