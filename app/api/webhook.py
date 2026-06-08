from fastapi import APIRouter

router = APIRouter()


@router.post("/webhook/whatsapp")
def whatsapp_webhook(
    payload: dict
):

    print("=" * 100)
    print(payload)
    print("=" * 100)

    return {
        "success": True
    }