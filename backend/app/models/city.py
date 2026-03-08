from sqlalchemy import Column, Integer, String, Boolean
from geoalchemy2 import Geography
from app.db.base import Base

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    center = Column(Geography(geometry_type="POINT", srid=4326))
    is_active = Column(Boolean, default=True)

