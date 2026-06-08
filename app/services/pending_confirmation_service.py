from sqlalchemy.orm import Session

from app.models.pending_confirmation import PendingConfirmation


class PendingConfirmationService:

    def create(
        self,
        db: Session,
        payload: dict,
        customer_phone: str | None = None
    ) -> PendingConfirmation:

        pending = PendingConfirmation(
            payload=payload,
            customer_phone=customer_phone
        )

        db.add(pending)

        db.commit()

        db.refresh(pending)

        return pending