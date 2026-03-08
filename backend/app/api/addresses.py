from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from app.db.database import get_db
from app.models.address import Address
from app.schemas.address import AddressCreate, AddressOut

from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/addresses", tags=["Addresses"])


# =====================================================
# ✅ Create Address (Logged User Only)
# =====================================================
@router.post("/", response_model=AddressOut)
def create_address(
    data: AddressCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    point = from_shape(
        Point(data.longitude, data.latitude),
        srid=4326
    )

    address = Address(
        user_id=user.id,          # ✅ from token
        city_id=data.city_id,
        location=point,
        address_text=data.address_text
    )

    db.add(address)
    db.commit()
    db.refresh(address)

    return address


# =====================================================
# ✅ Get My Addresses ONLY
# =====================================================
@router.get("/me", response_model=list[AddressOut])
def get_my_addresses(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(Address).filter(
        Address.user_id == user.id
    ).all()


# =====================================================
# ✅ Delete My Address
# =====================================================
@router.delete("/{address_id}")
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == user.id
    ).first()

    if not address:
        raise HTTPException(404, "Address not found")

    db.delete(address)
    db.commit()

    return {"status": "deleted"}
