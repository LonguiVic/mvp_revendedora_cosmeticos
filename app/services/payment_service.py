from datetime import datetime

from sqlalchemy.orm import Session

from app.models.audit import Audit
from app.models.installment import Installment


class PaymentService:

    def register_payment(
        self,
        db: Session,
        installment_id: int
    ):

        installment = db.get(
            Installment,
            installment_id
        )

        if not installment:
            raise ValueError(
                "Installment not found"
            )

        if installment.status == "PAID":
            raise ValueError(
                "Installment already paid"
            )

        installment.status = "PAID"
        installment.payment_date = datetime.utcnow()

        audit = Audit(
            event_type="PAYMENT_RECEIVED",
            sale_id=installment.sale_id,
            description=(
                f"Installment "
                f"{installment.installment_number}/"
                f"{installment.total_installments} paid"
            )
        )

        db.add(audit)

        db.commit()

        db.refresh(installment)

        return installment