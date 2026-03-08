from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime
from datetime import datetime
from app.db.base import Base

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    points_balance = Column(Numeric, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
