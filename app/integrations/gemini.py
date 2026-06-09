from google import genai
import time
import logging
from app.config.settings import settings
from app.schemas.sale_extraction import SaleExtraction


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class GeminiService:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    def extract_sale(
        self,
        text: str
    ) -> SaleExtraction:

        max_tentativas = 3

        for tentativa in range(max_tentativas):
            try:
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

            except Exception as e:
                erro_str = str(e)
                
                if "503" in erro_str or "UNAVAILABLE" in erro_str:
                    if tentativa < max_tentativas - 1:
                        tempo_espera = 2 ** tentativa 
                        logger.warning(f"API do Google ocupada. Retentando em {tempo_espera}s...")
                        time.sleep(tempo_espera)
                    else:
                        logger.error("Falha no Google após múltiplas tentativas.")
                        raise e
                else:
                    raise e