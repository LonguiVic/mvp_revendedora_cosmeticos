from sqlalchemy.orm import Session

from app.models.installment import Installment
from app.models.sale import Sale


class InstallmentService:

    def list_installments(
        self,
        db: Session,
        status: str | None = None
    ):

        query = (
            db.query(
                Installment,
                Sale
            )
            .join(
                Sale,
                Installment.sale_id == Sale.id
            )
        )

        if status:
            query = query.filter(
                Installment.status == status.upper()
            )

        rows = query.order_by(
            Installment.due_year,
            Installment.due_month,
            Installment.installment_number
        ).all()

        return [
            {
                "installment_id": installment.id,
                "sale_id": installment.sale_id,
                "cliente": sale.customer_name,
                "produto": ", ".join([i.product for i in sale.items]),
                "parcela": (
                    f"{installment.installment_number}/"
                    f"{installment.total_installments}"
                ),
                "valor": installment.amount,
                "mes": installment.due_month,
                "ano": installment.due_year,
                "status": installment.status,
                "payment_date": (
                    installment.payment_date.isoformat()
                    if installment.payment_date
                    else None
                )
            }
            for installment, sale in rows
        ]