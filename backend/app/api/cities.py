from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.city import City
from app.schemas.city import CityOut
from app.db.database import get_db

router = APIRouter(prefix="/cities", tags=["Cities"])

@router.get("/", response_model=list[CityOut])
def get_cities(db: Session = Depends(get_db)):
    return db.query(City).filter(City.is_active == True).all()
