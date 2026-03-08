from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db

router = APIRouter(prefix="/zone-check", tags=["Zone Check"])


@router.get("/address/{address_id}")
def check_address_zone(address_id: int, db: Session = Depends(get_db)):
    # Make sure address exists
    address_exists = db.execute(
        text("SELECT 1 FROM addresses WHERE id = :id"),
        {"id": address_id}
    ).fetchone()

    if not address_exists:
        raise HTTPException(status_code=404, detail="Address not found")

    # Check if address is inside any active service zone
    query = text("""
        SELECT EXISTS (
            SELECT 1
            FROM service_zones z
            JOIN addresses a ON a.id = :address_id
            WHERE z.is_active = TRUE
            AND ST_Contains(
                z.area::geometry,
                a.location::geometry
            )
        ) AS service_available;
    """)

    result = db.execute(query, {"address_id": address_id}).fetchone()

    service_available = result.service_available

    return {
        "service_available": service_available,
        "can_request_service": not service_available
    }
