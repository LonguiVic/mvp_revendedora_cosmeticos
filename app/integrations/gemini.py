from google import genai

from app.config.settings import settings
from app.schemas.sale_extraction import SaleExtraction


class GeminiService:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    def extract_sale(
        self,
        text: str
    ) -> SaleExtraction:

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
Extraia os dados da venda:

{text}
""",
            config={
                "response_mime_type": "application/json",
                "response_schema": SaleExtraction,
            },
        )

        return response.parsed