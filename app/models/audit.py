from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base


class Audit(Base):
    __tablename__ = "audits"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    event_type: Mapped[str] = mapped_column(
        String(100)
    )

    sale_id: Mapped[int]

    description: Mapped[str] = mapped_column(
        String(1000)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )