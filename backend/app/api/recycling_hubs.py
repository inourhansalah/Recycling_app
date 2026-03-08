from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shapely.geometry import Point
from geoalchemy2.shape import from_shape

from app.db.database import get_db
from app.models.recycling_hub import RecyclingHub
from app.schemas.recycling_hub import RecyclingHubCreate, RecyclingHubOut

from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/recycling-hubs", tags=["Recycling Hubs"])


# =====================================================
# ✅ Admin Create Hub
# =====================================================
@router.post("/", response_model=RecyclingHubOut)
def create_recycling_hub(
    data: RecyclingHubCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin only")

    point = from_shape(Point(data.longitude, data.latitude), srid=4326)

    hub = RecyclingHub(
        city_id=data.city_id,
        name=data.name,
        location=point,
        is_active=True
    )

    db.add(hub)
    db.commit()
    db.refresh(hub)

    return hub


# =====================================================
# ✅ Public View Hubs
# =====================================================
@router.get("/", response_model=list[RecyclingHubOut])
def get_all_hubs(db: Session = Depends(get_db)):
    return db.query(RecyclingHub).filter(
        RecyclingHub.is_active == True
    ).all()
