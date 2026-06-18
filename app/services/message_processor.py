from app.integrations.gemini import GeminiService
from app.utils.sale_detector import may_be_sale, is_valid_sale
from app.schemas.intent_extraction import Intent

class MessageProcessorService:

    def __init__(self):
        self.gemini = GeminiService()

    def process(
        self,
        text: str
    ):
        intent_data = self.gemini.extract_intent(text)
        
        result = {
            "intent": intent_data.intent,
            "data": intent_data,
            "sale": None
        }

        if intent_data.intent == Intent.REGISTRAR_VENDA:
            sale = self.gemini.extract_sale(text)
            if is_valid_sale(sale):
                result["sale"] = sale
            else:
                result["intent"] = Intent.OUTROS
                
        return result