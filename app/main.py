from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from app.api.parse_sale import router as parse_router
from app.api.confirm_sale import router as confirm_sale_router
from app.api.queries import router as query_router
from app.api.payments import router as payments_router
from app.api.installments import router as installments_router
from app.api.cancel_sale import router as cancel_sale_router
from app.api.sales import router as sales_router
from app.api.sync_sheets import router as sync_sheets_router
from app.api.webhook import router as webhook_router
from app.database.base import Base
from app.database.session import engine

from app.models.pending_confirmation import PendingConfirmation
from app.models.sale import Sale, SaleItemModel
from app.models.installment import Installment
from app.models.profit import Profit
from app.models.audit import Audit
from app.models.whatsapp_message import WhatsappMessage

from app.schedulers.jobs import send_monthly_reminder, send_auto_charges

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(send_monthly_reminder, 'cron', day=1, hour=9, minute=0)
    scheduler.add_job(send_auto_charges, 'cron', day=5, hour=10, minute=0)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

Base.metadata.create_all(
    bind=engine
)

app.include_router(parse_router)
app.include_router(confirm_sale_router)
app.include_router(query_router)
app.include_router(payments_router)
app.include_router(installments_router)
app.include_router(cancel_sale_router)
app.include_router(sales_router)
app.include_router(sync_sheets_router)
app.include_router(webhook_router)

@app.get("/")
def health():
    return {
        "status": "ok"
    }