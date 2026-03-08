from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction

from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/wallets", tags=["Wallets"])


# =====================================================
# ✅ Get My Wallet (JWT)
# =====================================================
@router.get("/me")
def get_my_wallet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Logged-in user views his wallet.
    """

    wallet = db.query(Wallet).filter(
        Wallet.user_id == current_user.id
    ).first()

    if not wallet:
        raise HTTPException(404, "Wallet not found")

    return wallet


# =====================================================
# ✅ My Wallet Transactions History
# =====================================================
@router.get("/me/transactions")
def my_wallet_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Logged user views his wallet transactions.
    """

    wallet = db.query(Wallet).filter(
        Wallet.user_id == current_user.id
    ).first()

    if not wallet:
        raise HTTPException(404, "Wallet not found")

    transactions = db.query(WalletTransaction).filter(
        WalletTransaction.wallet_id == wallet.id
    ).order_by(
        WalletTransaction.created_at.desc()
    ).all()

    return {
        "user_id": current_user.id,
        "count": len(transactions),
        "transactions": transactions
    }
