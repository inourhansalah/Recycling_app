from sqlalchemy.orm import Session
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction

def get_or_create_wallet(db: Session, user_id: int) -> Wallet:
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        wallet = Wallet(user_id=user_id)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet

def record_wallet_transaction(
    db: Session,
    wallet_id: int,
    amount: float,
    direction: str,
    reason: str,
    created_by: int,
    order_id: int = None
):
    transaction = WalletTransaction(
        wallet_id=wallet_id,
        amount=amount,
        direction=direction,
        reason=reason,
        created_by=created_by,
        order_id=order_id
    )
    db.add(transaction)
    return transaction
