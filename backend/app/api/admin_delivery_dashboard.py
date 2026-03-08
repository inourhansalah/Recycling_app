from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.order import Order

from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/admin-delivery",
    tags=["Admin Delivery Dashboard"]
)


# =====================================================
# Helper → Admin Only
# =====================================================
def admin_only(current_user: User):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin only access")


# =====================================================
# 1️⃣ Orders Needing Delivery Pricing
# =====================================================
@router.get("/needs-pricing")
def orders_needing_pricing(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Orders where delivery requested
    but admin has not priced delivery yet.
    """

    admin_only(current_user)

    orders = db.query(Order).filter(
        Order.delivery_requested == True,
        Order.status == "seller_approved"
    ).all()

    return {
        "count": len(orders),
        "orders": orders
    }


# =====================================================
# 2️⃣ Orders Waiting Buyer Approval
# =====================================================
@router.get("/waiting-buyer")
def orders_waiting_buyer(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Orders where admin priced delivery
    but buyer has not accepted yet.
    """

    admin_only(current_user)

    orders = db.query(Order).filter(
        Order.delivery_requested == True,
        Order.status == "delivery_priced"
    ).all()

    return {
        "count": len(orders),
        "orders": orders
    }


# =====================================================
# 3️⃣ Orders Ready for Delivery Assignment
# =====================================================
@router.get("/ready-assignment")
def orders_ready_assignment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Orders where buyer accepted delivery pricing
    and admin must assign a delivery person.
    """

    admin_only(current_user)

    orders = db.query(Order).filter(
        Order.delivery_requested == True,
        Order.status == "approved",
        Order.assigned_delivery_id == None
    ).all()

    return {
        "count": len(orders),
        "orders": orders
    }


# =====================================================
# 4️⃣ Active Delivery Orders
# =====================================================
@router.get("/active")
def active_delivery_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Orders currently assigned to delivery and running.
    """

    admin_only(current_user)

    orders = db.query(Order).filter(
        Order.delivery_requested == True,
        Order.status.in_(["assigned", "on_the_way", "collected"])
    ).all()

    return {
        "count": len(orders),
        "orders": orders
    }


# =====================================================
# 5️⃣ Completed Delivery Orders
# =====================================================
@router.get("/completed")
def completed_delivery_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Orders completed successfully with delivery.
    """

    admin_only(current_user)

    orders = db.query(Order).filter(
        Order.delivery_requested == True,
        Order.status == "completed"
    ).all()

    return {
        "count": len(orders),
        "orders": orders
    }
