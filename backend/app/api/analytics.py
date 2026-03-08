from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime

from app.db.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User
from app.models.money_transaction import MoneyTransaction
from app.models.wallet_transaction import WalletTransaction

from app.utils.dependencies import require_role

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# =====================================================
# Helper → Date Filter
# =====================================================
def apply_date_filter(query, model, from_date, to_date):
    if from_date:
        query = query.filter(model.created_at >= from_date)
    if to_date:
        query = query.filter(model.created_at <= to_date)
    return query


# =====================================================
# 1️⃣ Revenue with Date Range
# =====================================================
@router.get("/revenue")
def revenue(
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):

    cash_query = db.query(func.sum(MoneyTransaction.amount)).filter(
        MoneyTransaction.reason == "marketplace_cash_record"
    )

    cash_query = apply_date_filter(
        cash_query, MoneyTransaction, from_date, to_date
    )

    cash = cash_query.scalar() or 0

    return {
        "cash_revenue": float(cash),
        "from_date": from_date,
        "to_date": to_date
    }


# =====================================================
# 2️⃣ Monthly Revenue Growth
# =====================================================
@router.get("/revenue/monthly-growth")
def monthly_growth(
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):

    results = db.query(
        extract("year", MoneyTransaction.created_at).label("year"),
        extract("month", MoneyTransaction.created_at).label("month"),
        func.sum(MoneyTransaction.amount).label("total")
    ).filter(
        MoneyTransaction.reason == "marketplace_cash_record"
    ).group_by("year", "month").order_by("year", "month").all()

    return [
        {
            "year": int(r.year),
            "month": int(r.month),
            "revenue": float(r.total)
        }
        for r in results
    ]


# =====================================================
# 3️⃣ Revenue Per City
# =====================================================
@router.get("/revenue/city")
def revenue_per_city(
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):

    results = db.query(
        User.city,
        func.sum(MoneyTransaction.amount).label("total")
    ).join(Order, Order.user_id == User.id
    ).join(MoneyTransaction, MoneyTransaction.order_id == Order.id
    ).filter(
        MoneyTransaction.reason == "marketplace_cash_record"
    ).group_by(User.city).all()

    return [
        {
            "city": r.city,
            "revenue": float(r.total or 0)
        }
        for r in results
    ]


# =====================================================
# 4️⃣ Average Order Value (AOV)
# =====================================================
@router.get("/orders/average-value")
def average_order_value(
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):

    total_revenue = db.query(
        func.sum(MoneyTransaction.amount)
    ).filter(
        MoneyTransaction.reason == "marketplace_cash_record"
    ).scalar() or 0

    total_orders = db.query(
        func.count(Order.id)
    ).filter(
        Order.status == "completed"
    ).scalar() or 1

    aov = total_revenue / total_orders

    return {
        "average_order_value": round(float(aov), 2)
    }


# =====================================================
# 5️⃣ Customer Lifetime Value (CLV)
# =====================================================
@router.get("/customers/lifetime-value")
def customer_lifetime_value(
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):

    results = db.query(
        Order.user_id,
        func.sum(MoneyTransaction.amount).label("total_spent")
    ).join(MoneyTransaction, MoneyTransaction.order_id == Order.id
    ).filter(
        MoneyTransaction.reason == "marketplace_cash_record"
    ).group_by(Order.user_id).all()

    return [
        {
            "user_id": r.user_id,
            "lifetime_value": float(r.total_spent or 0)
        }
        for r in results
    ]


# =====================================================
# 6️⃣ Cohort Analysis (Users grouped by registration month)
# =====================================================
@router.get("/customers/cohort")
def cohort_analysis(
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):

    results = db.query(
        extract("year", User.created_at).label("year"),
        extract("month", User.created_at).label("month"),
        func.count(User.id).label("new_users")
    ).group_by("year", "month").order_by("year", "month").all()

    return [
        {
            "year": int(r.year),
            "month": int(r.month),
            "new_users": r.new_users
        }
        for r in results
    ]