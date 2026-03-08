from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.order import Order

from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/order-history", tags=["Order History"])


# =====================================================
# ✅ Buyer Views His Orders ONLY
# =====================================================
@router.get("/me")
def my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(Order.created_at.desc()).all()

    return {
        "user_id": current_user.id,
        "count": len(orders),
        "orders": orders
    }


# =====================================================
# ✅ Seller Views His Orders ONLY
# =====================================================
@router.get("/me/seller")
def my_seller_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(Order).filter(
        Order.seller_id == current_user.id
    ).order_by(Order.created_at.desc()).all()

    return {
        "seller_id": current_user.id,
        "count": len(orders),
        "orders": orders
    }


# =====================================================
# ✅ Admin Views All Orders
# =====================================================
@router.get("/admin/all")
def admin_all_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin only")

    orders = db.query(Order).order_by(Order.created_at.desc()).all()

    return {
        "count": len(orders),
        "orders": orders
    }
