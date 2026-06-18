from sqlalchemy.orm import Session

from app.integrations.gemini import GeminiService
from app.services.pending_confirmation_service import (
    PendingConfirmationService
)


class SaleParserService:

    def __init__(self):
        self.gemini = GeminiService()
        self.pending_service = PendingConfirmationService()

    def parse_and_store(
        self,
        db: Session,
        text: str
    ):

        sale = self.gemini.extract_sale(text)

        pending = self.pending_service.create(
            db=db,
            payload=sale.model_dump(),
            customer_phone=sale.telefone
        )

        return pending, sale