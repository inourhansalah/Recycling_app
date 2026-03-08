from sqlalchemy import Column, Integer, ForeignKey, Text, Boolean, DateTime
from datetime import datetime
from app.db.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(Text, nullable=False)
    message = Column(Text, nullable=False)

    entity_type = Column(Text, nullable=True)
    entity_id = Column(Integer, nullable=True)

    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)  # ✅ NEW

    created_at = Column(DateTime, default=datetime.utcnow)