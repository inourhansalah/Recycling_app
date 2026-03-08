from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.order import Order

from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/delivery-dashboard",
    tags=["Delivery Dashboard"]
)


# =====================================================
# ✅ Delivery View Assigned Orders
# =====================================================
@router.get("/me/orders")
def my_delivery_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "delivery":
        raise HTTPException(403, "Delivery only")

    orders = db.query(Order).filter(
        Order.assigned_delivery_id == current_user.id
    ).order_by(Order.created_at.desc()).all()

    return {
        "delivery_id": current_user.id,
        "count": len(orders),
        "orders": orders
    }
