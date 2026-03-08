from sqlalchemy import Column, Integer, Text, Boolean
from app.db.base import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    image_url = Column(Text, nullable=False)
    type = Column(Text)  # recycling / marketplace
    is_active = Column(Boolean, default=True)
