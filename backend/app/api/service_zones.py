# app/api/service_zones.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from shapely.geometry import Polygon
from geoalchemy2.shape import from_shape

from app.db.database import get_db
from app.models.service_zone import ServiceZone
from app.schemas.service_zone import ServiceZoneCreate, ServiceZoneOut

from app.utils.dependencies import require_role

router = APIRouter(prefix="/service-zones", tags=["Service Zones"])


# =====================================================
# ✅ Admin Creates Zones Only
# =====================================================
@router.post("/", response_model=ServiceZoneOut)
def create_service_zone(
    data: ServiceZoneCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    polygon = from_shape(
        Polygon(data.coordinates),
        srid=4326
    )

    zone = ServiceZone(
        city_id=data.city_id,
        name=data.name,
        area=polygon,
        is_active=True
    )

    db.add(zone)
    db.commit()
    db.refresh(zone)

    return zone
