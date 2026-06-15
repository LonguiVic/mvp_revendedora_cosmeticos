from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base

class SaleItemModel(Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"))
    product: Mapped[str] = mapped_column(String(255))
    brand: Mapped[str] = mapped_column(String(100))
    quantity: Mapped[int]


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_code: Mapped[str] = mapped_column(String(50), unique=True)
    customer_name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    
    # Relationships
    items = relationship("SaleItemModel", cascade="all, delete-orphan")

    sale_value: Mapped[float] = mapped_column(Float)
    cost_value: Mapped[float] = mapped_column(Float)
    profit_value: Mapped[float] = mapped_column(Float)
    installments: Mapped[int]
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")
    sale_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
