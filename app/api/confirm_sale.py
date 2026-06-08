from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.sale_confirmation_service import (
    SaleConfirmationService
)

router = APIRouter()

service = SaleConfirmationService()


@router.post("/confirm-sale")
def confirm_sale(
    payload: dict,
    db: Session = Depends(get_db)
):

    sale = service.confirm(
        db=db,
        confirmation_id=payload["confirmation_id"]
    )

    return {
        "sale_code": sale.sale_code,
        "message": "Venda registrada com sucesso."
    }