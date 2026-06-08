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

router = APIRouter()
pending_service = (
    PendingConfirmationService()
)


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

    GRUPO_VENDAS_ID = "120363163180636909@g.us"

    if remote_jid != GRUPO_VENDAS_ID:
        return {"success": True}

    message_data = data.get("message", {})
    texto_mensagem = message_data.get("conversation")

    if not texto_mensagem and "extendedTextMessage" in message_data:
        texto_mensagem = message_data["extendedTextMessage"].get("text")

    if not texto_mensagem:
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

            print(
                f"VENDA IDENTIFICADA - Confirmation ID: {pending.id}"
            )

            print(
                sale.model_dump()
            )

        else:

            print(
                "Mensagem comum."
            )

    except Exception as e:

        print(
            f"Erro ao processar mensagem: {e}"
        )


    print("=" * 80)
    print(f"Cliente: {remote_jid}")
    print(f"Mensagem: {texto_mensagem}")
    print("=" * 80)

    return {"success": True}