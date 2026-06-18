from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.sale_parser_service import (
    SaleParserService
)

router = APIRouter()

service = SaleParserService()

@router.post("/parse-sale")
def parse_sale(
    payload: dict,
    db: Session = Depends(get_db)
):

    pending, sale = service.parse_and_store(
        db=db,
        text=payload["message"]
    )

    return {
        "confirmation_id": pending.id,
        "sale": sale
    }