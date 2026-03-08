# app/models/product.py

from sqlalchemy import Column, Integer, Text, Numeric, Boolean, ForeignKey
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)

    name = Column(Text, nullable=False)
    price = Column(Numeric, nullable=False)
    is_active = Column(Boolean, default=True)

    type = Column(Text)  # recycling | marketplace
    status = Column(Text, default="approved")
    admin_notes = Column(Text, nullable=True)

    image_url = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))

    seller_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_sold = Column(Boolean, default=False)              # ✅ NEW

    # recycling
    unit = Column(Text, nullable=True)

    # marketplace
    description = Column(Text, nullable=True)
    pickup_address = Column(Text, nullable=True)
