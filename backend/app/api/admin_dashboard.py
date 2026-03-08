from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.models.order import Order
from app.models.product import Product

from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/admin-dashboard",
    tags=["Admin Dashboard"]
)


# =====================================================
# Helper → Admin Only
# =====================================================
def admin_only(current_user: User):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin only access"
        )


# =====================================================
# ✅ 1️⃣ System Summary (Admin Only)
# =====================================================
@router.get("/summary")
def system_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    admin_only(current_user)

    return {
        "total_orders": db.query(func.count(Order.id)).scalar(),

        "marketplace_orders": db.query(func.count(Order.id))
        .filter(Order.source == "marketplace").scalar(),

        "recycling_orders": db.query(func.count(Order.id))
        .filter(Order.source == "recycling").scalar(),

        "completed_orders": db.query(func.count(Order.id))
        .filter(Order.status == "completed").scalar(),

        "cancelled_orders": db.query(func.count(Order.id))
        .filter(Order.status == "cancelled").scalar(),
    }


# =====================================================
# ✅ 2️⃣ Products Review Dashboard (Admin Only)
# =====================================================
@router.get("/products-review")
def products_review(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    admin_only(current_user)

    return {
        "pending": db.query(func.count(Product.id))
        .filter(Product.status == "pending").scalar(),

        "approved": db.query(func.count(Product.id))
        .filter(Product.status == "approved").scalar(),

        "rejected": db.query(func.count(Product.id))
        .filter(Product.status == "rejected").scalar(),

        "needs_edit": db.query(func.count(Product.id))
        .filter(Product.status == "needs_edit").scalar(),
    }


# =====================================================
# ✅ 3️⃣ Delivery Requests Dashboard (Admin Only)
# =====================================================
@router.get("/delivery-requests")
def delivery_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    admin_only(current_user)

    orders = db.query(Order).filter(
        Order.delivery_requested == True,
        Order.status.in_([
            "seller_approved",
            "delivery_priced",
            "approved"
        ])
    ).all()

    return {
        "total_requests": len(orders),
        "orders": orders
    }
