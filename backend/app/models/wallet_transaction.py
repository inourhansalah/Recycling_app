from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, DateTime
from datetime import datetime
from app.db.base import Base

class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))

    amount = Column(Numeric, nullable=False)
    direction = Column(Text)  # earn | spend | adjust
    reason = Column(Text)

    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
