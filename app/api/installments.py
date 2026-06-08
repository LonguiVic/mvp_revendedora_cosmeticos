from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.installment_service import (
    InstallmentService
)

router = APIRouter()

service = InstallmentService()


@router.get("/installments")
def get_installments(
    status: str | None = None,
    db: Session = Depends(get_db)
):

    return service.list_installments(
        db=db,
        status=status
    )