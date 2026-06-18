from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.services.sync_sheets_service import (
    SyncSheetsService
)

router = APIRouter()

service = SyncSheetsService()


@router.post("/sync-sheets")
def sync_sheets(
    db: Session = Depends(get_db)
):

    service.sync(db)

    return {
        "message": (
            "Google Sheets sincronizado"
        )
    }