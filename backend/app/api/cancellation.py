# app/api/cancellation.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.order import Order
from app.services.activity_service import log_activity
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/cancel", tags=["Cancellation"])


ALLOWED_CANCEL_STATUSES = ["pending", "seller_approved", "delivery_priced"]


# =====================================================
# ✅ Customer Cancel Own Order
# =====================================================
@router.post("/order/{order_id}")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    # Only buyer can cancel
    if order.user_id != current_user.id:
        raise HTTPException(403, "Not your order")

    if order.status not in ALLOWED_CANCEL_STATUSES:
        raise HTTPException(400, "Cannot cancel now")

    order.status = "cancelled"
    db.commit()

    log_activity(
        db=db,
        user_id=current_user.id,
        user_role=current_user.role,
        entity_type="order",
        entity_id=order.id,
        action="cancel",
        description="Customer cancelled order"
    )

    return {"status": "cancelled"}
