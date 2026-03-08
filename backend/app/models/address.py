from sqlalchemy import Column, Integer, ForeignKey, Text
from geoalchemy2 import Geography
from app.db.base import Base

class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    city_id = Column(Integer, ForeignKey("cities.id"))
    location = Column(Geography(geometry_type="POINT", srid=4326))
    address_text = Column(Text)
