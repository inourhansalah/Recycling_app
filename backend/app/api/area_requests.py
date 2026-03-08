from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from shapely.geometry import Point
from geoalchemy2.shape import from_shape

from app.db.database import get_db
from app.models.area_request import AreaRequest
from app.schemas.area_request import AreaRequestCreate, AreaRequestOut

from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/area-requests", tags=["Area Requests"])


# =====================================================
# ✅ Logged User Creates Area Request
# =====================================================
@router.post("/", response_model=AreaRequestOut)
def create_area_request(
    data: AreaRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    point = from_shape(
        Point(data.longitude, data.latitude),
        srid=4326
    )

    request = AreaRequest(
        user_id=current_user.id,   # ✅ TOKEN ONLY
        city_id=data.city_id,
        location=point,
        address_text=data.address_text
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    return request
