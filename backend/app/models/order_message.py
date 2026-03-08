from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from datetime import datetime
from app.db.base import Base


class OrderMessage(Base):
    __tablename__ = "order_messages"

    id = Column(Integer, primary_key=True)

    order_id = Column(Integer, ForeignKey("orders.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))

    message = Column(Text, nullable=True)

    attachment_url = Column(Text, nullable=True)
    attachment_type = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
