from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base

class WhatsappMessage(Base):
    __tablename__ = "whatsapp_messages"

    id = mapped_column(Integer, primary_key=True)

    phone = mapped_column(String(50))

    customer_name = mapped_column(
        String(255),
        nullable=True
    )

    message_text = mapped_column(Text)

    processed = mapped_column(
        Boolean,
        default=False
    )

    created_at = mapped_column(
        DateTime,
        default=datetime.utcnow
    )