from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from geoalchemy2 import Geography
from datetime import datetime

from app.db.base import Base


class AreaRequest(Base):
    __tablename__ = "area_requests"

    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey("cities.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    location = Column(Geography(geometry_type="POINT", srid=4326))
    address_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
