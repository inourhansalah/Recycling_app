from sqlalchemy import Column, Integer, ForeignKey, Numeric, Text, DateTime
from datetime import datetime
from app.db.base import Base

class MoneyTransaction(Base):
    __tablename__ = "money_transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))

    amount = Column(Numeric, nullable=False)
    currency = Column(Text, default="EGP")
    direction = Column(Text)  # pay | receive

    reason = Column(Text)
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime, default=datetime.utcnow)
