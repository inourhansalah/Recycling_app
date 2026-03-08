from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.order import Order
from app.models.order_message import OrderMessage

from app.schemas.order_message import MessageCreate, MessageOut
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/order-chat",
    tags=["Order Chat"]
)


# =====================================================
# ✅ Send Message (Buyer or Seller)
# =====================================================
@router.post("/{order_id}/send", response_model=MessageOut)
def send_message(
    order_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    # Only buyer or seller allowed
    if current_user.id not in [order.user_id, order.seller_id]:
        raise HTTPException(403, "Not allowed")

    msg = OrderMessage(
        order_id=order.id,
        sender_id=current_user.id,
        message=data.message,
        attachment_url=data.attachment_url,
        attachment_type=data.attachment_type
    )

    db.add(msg)
    db.commit()
    db.refresh(msg)

    return msg


# =====================================================
# ✅ View Chat Messages (Buyer or Seller)
# =====================================================
@router.get("/{order_id}/messages", response_model=list[MessageOut])
def view_messages(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    # Only buyer or seller allowed
    if current_user.id not in [order.user_id, order.seller_id]:
        raise HTTPException(403, "Not allowed")

    messages = db.query(OrderMessage).filter(
        OrderMessage.order_id == order.id
    ).order_by(OrderMessage.created_at.asc()).all()

    return messages
