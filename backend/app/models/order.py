# app/models/order.py

from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Boolean, Numeric
from datetime import datetime
from app.db.base import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))     # buyer
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    address_id = Column(Integer, ForeignKey("addresses.id"))

    status = Column(Text, default="pending")

    source = Column(Text)  # marketplace | recycling
    delivery_requested = Column(Boolean, default=False)

    payment_type = Column(Text, nullable=True)             # cash | points | cash_points
    delivery_price = Column(Numeric, nullable=True)

    admin_reviewed = Column(Boolean, default=False)
    seller_approved = Column(Boolean, default=False)

    buyer_confirmed = Column(Boolean, default=False)
    seller_confirmed = Column(Boolean, default=False)

    assigned_delivery_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    admin_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    system_reward_value = Column(Numeric, nullable=True)
    final_reward_value = Column(Numeric, nullable=True)

    reward_overridden = Column(Boolean, default=False)
    reward_notes = Column(Text, nullable=True)

    cash_paid = Column(Numeric, default=0)
    points_paid = Column(Numeric, default=0)

    seller_payment_confirmed = Column(Boolean, default=False)
    buyer_confirmed = Column(Boolean, default=False)
    seller_confirmed = Column(Boolean, default=False)
