from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.payment_service import PaymentService

router = APIRouter()

service = PaymentService()


@router.post("/payments")
def register_payment(
    payload: dict,
    db: Session = Depends(get_db)
):

    try:

        installment = service.register_payment(
            db=db,
            installment_id=payload["installment_id"]
        )

        return {
            "message": (
                "Pagamento registrado com sucesso"
            ),
            "installment_id": installment.id
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )