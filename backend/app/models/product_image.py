from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, DateTime
from datetime import datetime
from app.db.base import Base

class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True)
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE")
    )
    image_url = Column(Text, nullable=False)
    is_cover = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
