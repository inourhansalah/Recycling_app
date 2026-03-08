# app/models/activity_log.py

from sqlalchemy import Column, Integer, Text, DateTime, JSON
from datetime import datetime
from app.db.base import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    user_role = Column(Text, nullable=False)

    entity_type = Column(Text, nullable=False)
    entity_id = Column(Integer, nullable=False)

    action = Column(Text, nullable=False)
    description = Column(Text, nullable=False)

    details = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
