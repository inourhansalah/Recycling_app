from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from geoalchemy2 import Geography
from app.db.base import Base


class ServiceZone(Base):
    __tablename__ = "service_zones"

    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey("cities.id"))
    name = Column(String, nullable=False)
    area = Column(Geography(geometry_type="POLYGON", srid=4326))
    is_active = Column(Boolean, default=True)
