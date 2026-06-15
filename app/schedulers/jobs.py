import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import SessionLocal
from app.models.sale import Sale
from app.models.installment import Installment
from app.api.webhook import enviar_mensagem_whatsapp
from app.config.settings import settings

logger = logging.getLogger(__name__)

MONTH_NAMES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

def send_monthly_reminder():
    logger.info("Executing monthly reminder for reseller.")
    db: Session = SessionLocal()
    try:
        month = datetime.now().month
        year = datetime.now().year

        rows = (
            db.query(Sale.customer_name, func.sum(Installment.amount))
            .join(Installment, Sale.id == Installment.sale_id)
            .filter(
                Installment.due_month == month,
                Installment.due_year == year,
                Installment.status == "PENDING"
            )
            .group_by(Sale.customer_name)
            .all()
        )

        if not rows:
            logger.info("No receivables for this month.")
            return

        total = sum(float(row[1]) for row in rows)
        month_name = MONTH_NAMES[month - 1]
        
        msg = f"Resumo de {month_name}:\n\nVocê possui R$ {total:.2f} para receber.\n\n"
        for row in rows:
            msg += f"{row[0]} — R$ {float(row[1]):.2f}\n"

        enviar_mensagem_whatsapp(settings.grupo_vendas_id, msg.strip())
        logger.info("Monthly reminder sent.")

    except Exception as e:
        logger.error(f"Error in send_monthly_reminder: {e}")
    finally:
        db.close()


def send_auto_charges():
    logger.info("Executing auto charges for customers.")
    db: Session = SessionLocal()
    try:
        month = datetime.now().month
        year = datetime.now().year

        installments = (
            db.query(Installment, Sale)
            .join(Sale, Installment.sale_id == Sale.id)
            .filter(
                Installment.due_month == month,
                Installment.due_year == year,
                Installment.status == "PENDING"
            )
            .all()
        )

        for inst, sale in installments:
            if sale.phone:
                products_str = ", ".join([i.product for i in sale.items])
                msg = (
                    f"Olá, {sale.customer_name}! Tudo bem?\n\n"
                    f"Passando para lembrar que neste mês há uma parcela referente a "
                    f"{products_str} no valor de R$ {inst.amount:.2f}.\n\n"
                    f"Quando puder, me avise sobre o pagamento.\n\n"
                    f"Muito obrigada!"
                )
                enviar_mensagem_whatsapp(sale.phone, msg)
        logger.info("Auto charges sent.")
    except Exception as e:
        logger.error(f"Error in send_auto_charges: {e}")
    finally:
        db.close()
