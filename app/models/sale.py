from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    sale_code: Mapped[str] = mapped_column(
        String(50),
        unique=True
    )

    customer_name: Mapped[str] = mapped_column(
        String(255)
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    brand: Mapped[str] = mapped_column(
        String(100)
    )

    product: Mapped[str] = mapped_column(
        String(255)
    )

    quantity: Mapped[int]

    sale_value: Mapped[float] = mapped_column(
        Float
    )

    cost_value: Mapped[float] = mapped_column(
        Float
    )

    profit_value: Mapped[float] = mapped_column(
        Float
    )

    installments: Mapped[int]

    status: Mapped[str] = mapped_column(
        String(50),
        default="ACTIVE"
    )

    sale_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )