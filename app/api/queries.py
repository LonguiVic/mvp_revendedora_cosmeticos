from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.query_service import QueryService

router = APIRouter()

service = QueryService()


@router.get("/receivables")
def receivables(
    month: int,
    year: int,
    db: Session = Depends(get_db)
):

    return service.get_receivables(
        db=db,
        month=month,
        year=year
    )


@router.get("/customer-debts")
def customer_debts(
    customer_name: str,
    db: Session = Depends(get_db)
):

    return service.get_customer_debts(
        db=db,
        customer_name=customer_name
    )


@router.get("/profits")
def profits(
    month: int,
    year: int,
    db: Session = Depends(get_db)
):

    return service.get_monthly_profit(
        db=db,
        month=month,
        year=year
    )