from sqlalchemy import Column, Integer, ForeignKey, Text, Boolean, DateTime
from geoalchemy2 import Geography
from datetime import datetime

from app.db.base import Base


class RecyclingHub(Base):
    __tablename__ = "recycling_hubs"

    id = Column(Integer, primary_key=True)

    city_id = Column(
        Integer,
        ForeignKey("cities.id", ondelete="CASCADE"),
        nullable=False
    )


    name = Column(Text, nullable=False)

    location = Column(
        Geography(geometry_type="POINT", srid=4326)
    )

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
