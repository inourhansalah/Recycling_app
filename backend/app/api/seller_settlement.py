from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.money_transaction import MoneyTransaction
from app.models.user import User

from app.services.activity_service import log_activity
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/seller-settlement",
    tags=["Seller Settlement"]
)


# =====================================================
# ✅ Admin Settles Seller Cash Earnings
# =====================================================
@router.post("/settle")
def settle_seller_cash(
    seller_id: int,
    amount: float,
    notes: str = "Seller cash settlement",

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin records offline cash settlement paid to seller.
    """

    # ✅ Admin Only
    if current_user.role != "admin":
        raise HTTPException(403, "Admin only")

    # ===============================
    # 1️⃣ Validate Seller Exists
    # ===============================
    seller = db.query(User).filter(User.id == seller_id).first()

    if not seller:
        raise HTTPException(404, "Seller not found")

    # ===============================
    # 2️⃣ Create MoneyTransaction Record
    # ===============================
    transaction = MoneyTransaction(
        user_id=seller_id,
        order_id=None,
        amount=amount,
        currency="EGP",
        direction="receive",
        reason="seller_cash_settlement",
        notes=notes,
        created_by=current_user.id
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # ===============================
    # 3️⃣ Activity Log
    # ===============================
    log_activity(
        db=db,
        user_id=current_user.id,
        user_role="admin",
        entity_type="seller",
        entity_id=seller_id,
        action="cash_settlement",
        description="Admin settled seller cash earnings",
        details={
            "amount": amount,
            "notes": notes
        }
    )

    return {
        "status": "settled",
        "seller_id": seller_id,
        "amount": amount,
        "transaction_id": transaction.id
    }


# =====================================================
# ✅ Admin View Seller Settlement History
# =====================================================
@router.get("/seller/{seller_id}/history")
def seller_settlement_history(
    seller_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin views settlement history for a seller.
    """

    if current_user.role != "admin":
        raise HTTPException(403, "Admin only")

    records = db.query(MoneyTransaction).filter(
        MoneyTransaction.user_id == seller_id,
        MoneyTransaction.reason == "seller_cash_settlement"
    ).order_by(
        MoneyTransaction.created_at.desc()
    ).all()

    return {
        "seller_id": seller_id,
        "records_count": len(records),
        "records": records
    }
