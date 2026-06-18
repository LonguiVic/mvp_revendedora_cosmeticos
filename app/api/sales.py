from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.sale_service import SaleService

router = APIRouter()

service = SaleService()


@router.get("/sales")
def get_sales(
    status: str | None = None,
    customer_name: str | None = None,
    db: Session = Depends(get_db)
):

    return service.list_sales(
        db=db,
        status=status,
        customer_name=customer_name
    )