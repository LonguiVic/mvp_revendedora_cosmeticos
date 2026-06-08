from fastapi import FastAPI

from app.api.parse_sale import router as parse_router
from app.api.confirm_sale import (
    router as confirm_sale_router
)
from app.api.queries import (
    router as query_router
)
from app.database.base import Base
from app.database.session import engine

from app.models.pending_confirmation import PendingConfirmation
from app.models.sale import Sale
from app.models.installment import Installment
from app.models.profit import Profit
from app.models.audit import Audit

app = FastAPI()

Base.metadata.create_all(
    bind=engine
)

app.include_router(parse_router)
app.include_router(confirm_sale_router)
app.include_router(query_router)

@app.get("/")
def health():
    return {
        "status": "ok"
    }