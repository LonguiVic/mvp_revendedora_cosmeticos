from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.cancel_sale_service import (
    CancelSaleService
)

router = APIRouter()

service = CancelSaleService()


@router.post("/cancel-sale")
def cancel_sale(
    payload: dict,
    db: Session = Depends(get_db)
):

    try:

        sale = service.cancel(
            db=db,
            sale_id=payload["sale_id"]
        )

        return {
            "message": "Venda cancelada com sucesso",
            "sale_id": sale.id,
            "sale_code": sale.sale_code
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )