from datetime import datetime

from sqlalchemy.orm import Session

from app.models.audit import Audit
from app.models.installment import Installment
from app.models.pending_confirmation import PendingConfirmation
from app.models.profit import Profit
from app.models.sale import Sale


class SaleConfirmationService:

    def confirm(
        self,
        db: Session,
        confirmation_id: int
    ):

        pending = db.get(
            PendingConfirmation,
            confirmation_id
        )

        if not pending:
            raise ValueError(
                "Confirmation not found"
            )

        if pending.confirmed:
            raise ValueError(
                "Already confirmed"
            )

        payload = pending.payload

        profit_value = (
            payload["valor_total"]
            - payload["custo_total"]
        )

        sale = Sale(
            sale_code=f"VEN-{datetime.now().strftime('%Y%m%d')}-{pending.id}",
            customer_name=payload["cliente"],
            phone=payload["telefone"],
            brand=payload["marca"],
            product=payload["produto"],
            quantity=payload["quantidade"],
            sale_value=payload["valor_total"],
            cost_value=payload["custo_total"],
            profit_value=profit_value,
            installments=payload["quantidade_parcelas"]
        )

        db.add(sale)

        db.flush()

        installment_amount = (
            payload["valor_total"]
            / payload["quantidade_parcelas"]
        )

        current_month = datetime.now().month
        current_year = datetime.now().year

        for number in range(
            1,
            payload["quantidade_parcelas"] + 1
        ):

            due_month = current_month + number

            due_year = current_year

            while due_month > 12:
                due_month -= 12
                due_year += 1

            installment = Installment(
                sale_id=sale.id,
                installment_number=number,
                total_installments=payload["quantidade_parcelas"],
                amount=installment_amount,
                due_month=due_month,
                due_year=due_year
            )

            db.add(installment)

        profit = Profit(
            sale_id=sale.id,
            revenue=payload["valor_total"],
            cost=payload["custo_total"],
            profit=profit_value
        )

        db.add(profit)

        audit = Audit(
            event_type="SALE_CREATED",
            sale_id=sale.id,
            description=f"Sale {sale.sale_code} created"
        )

        db.add(audit)

        pending.confirmed = True
        pending.confirmed_at = datetime.utcnow()

        db.commit()

        db.refresh(sale)

        return sale