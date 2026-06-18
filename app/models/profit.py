from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base


class Profit(Base):
    __tablename__ = "profits"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    sale_id: Mapped[int] = mapped_column(
        ForeignKey("sales.id")
    )

    revenue: Mapped[float] = mapped_column(
        Float
    )

    cost: Mapped[float] = mapped_column(
        Float
    )

    profit: Mapped[float] = mapped_column(
        Float
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="ACTIVE"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )