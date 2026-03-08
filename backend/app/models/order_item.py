from sqlalchemy import Column, Integer, ForeignKey, Numeric
from app.db.base import Base

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    estimated_quantity = Column(Numeric)
    actual_quantity = Column(Numeric, nullable=True)
