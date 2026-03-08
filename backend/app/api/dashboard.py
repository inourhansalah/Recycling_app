# app/api/dashboard.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.models.order import Order
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction
from app.models.money_transaction import MoneyTransaction

from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboards"])


# =====================================================
# ✅ My Selling Dashboard (Customer Only)
# =====================================================
@router.get("/my-selling")
def my_selling_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "customer":
        raise HTTPException(403, "Only customers allowed")

    seller_id = current_user.id

    completed_orders = db.query(func.count(Order.id)).filter(
        Order.seller_id == seller_id,
        Order.status == "completed"
    ).scalar() or 0

    wallet = db.query(Wallet).filter(Wallet.user_id == seller_id).first()

    points_earned = 0
    if wallet:
        points_earned = db.query(
            func.coalesce(func.sum(WalletTransaction.amount), 0)
        ).filter(
            WalletTransaction.wallet_id == wallet.id,
            WalletTransaction.reason == "seller_earning",
            WalletTransaction.direction == "earn"
        ).scalar()

    cash_earned = db.query(
        func.coalesce(func.sum(MoneyTransaction.amount), 0)
    ).filter(
        MoneyTransaction.user_id == seller_id,
        MoneyTransaction.reason == "seller_cash_settlement",
        MoneyTransaction.direction == "receive"
    ).scalar()

    return {
        "customer_id": seller_id,
        "completed_orders": completed_orders,
        "points_earned": float(points_earned),
        "cash_earned": float(cash_earned),
        "currency": "EGP"
    }


# =====================================================
# ✅ Buyer Dashboard (Customer Only)
# =====================================================
@router.get("/my-buying")
def my_buying_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    buyer_id = current_user.id

    marketplace_orders = db.query(func.count(Order.id)).filter(
        Order.user_id == buyer_id,
        Order.source == "marketplace",
        Order.status == "completed"
    ).scalar() or 0

    recycling_orders = db.query(func.count(Order.id)).filter(
        Order.user_id == buyer_id,
        Order.source == "recycling",
        Order.status == "completed"
    ).scalar() or 0

    return {
        "customer_id": buyer_id,
        "marketplace_completed": marketplace_orders,
        "recycling_completed": recycling_orders
    }
