from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base


class Installment(Base):
    __tablename__ = "installments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    sale_id: Mapped[int] = mapped_column(
        ForeignKey("sales.id")
    )

    installment_number: Mapped[int]

    total_installments: Mapped[int]

    amount: Mapped[float] = mapped_column(
        Float
    )

    due_month: Mapped[int]

    due_year: Mapped[int]

    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING"
    )

    payment_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )