from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base


class PendingConfirmation(Base):
    __tablename__ = "pending_confirmations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    customer_phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    payload: Mapped[dict] = mapped_column(
        JSON
    )

    confirmed: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )