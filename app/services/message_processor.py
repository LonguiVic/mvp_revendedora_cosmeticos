from app.integrations.gemini import GeminiService

from app.utils.sale_detector import (
    may_be_sale,
    is_valid_sale
)


class MessageProcessorService:

    def __init__(self):
        self.gemini = GeminiService()

    def process(
        self,
        text: str
    ):

        if not may_be_sale(text):
            return None

        sale = self.gemini.extract_sale(
            text
        )

        if not is_valid_sale(sale):
            return None

        return sale