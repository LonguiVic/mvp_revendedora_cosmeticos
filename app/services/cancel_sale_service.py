from sqlalchemy.orm import Session

from app.models.audit import Audit
from app.models.installment import Installment
from app.models.profit import Profit
from app.models.sale import Sale


class CancelSaleService:

    def cancel(
        self,
        db: Session,
        sale_id: int
    ):

        sale = db.get(
            Sale,
            sale_id
        )

        if not sale:
            raise ValueError(
                "Sale not found"
            )

        if sale.status == "CANCELLED":
            raise ValueError(
                "Sale already cancelled"
            )

        sale.status = "CANCELLED"

        installments = (
            db.query(Installment)
            .filter(
                Installment.sale_id == sale.id
            )
            .all()
        )

        for installment in installments:

            if installment.status != "PAID":
                installment.status = "CANCELLED"

        profits = (
            db.query(Profit)
            .filter(
                Profit.sale_id == sale.id
            )
            .all()
        )

        for profit in profits:

            if hasattr(profit, "status"):
                profit.status = "CANCELLED"

        audit = Audit(
            event_type="SALE_CANCELLED",
            sale_id=sale.id,
            description=f"Sale {sale.sale_code} cancelled"
        )

        db.add(audit)

        db.commit()

        return sale