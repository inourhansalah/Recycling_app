from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.order import Order
from app.schemas.order import (
    OrderCreate,
    OrderOut,
    SellerReviewOrder,
    AdminDeliveryReview,
    AssignDelivery,
    BuyerDeliveryDecision,
    BuyerConfirmAndPay,
)

from app.services.order_service import OrderService
from app.utils.dependencies import (
    get_current_user,
    require_role
)

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=list[OrderOut])
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return OrderService.create_order(db, current_user.id, data)

@router.post("/{order_id}/seller-review")
def seller_review(
    order_id: int,
    data: SellerReviewOrder,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = OrderService.seller_review(db, order_id, current_user.id, data.approve)
    return {"status": order.status}

@router.post("/{order_id}/admin-delivery")
def admin_delivery_review(
    order_id: int,
    data: AdminDeliveryReview,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    order = OrderService.admin_delivery_review(db, order_id, admin.id, data.approve, data.delivery_price, data.admin_notes)
    return {
        "status": order.status,
        "delivery_price": float(order.delivery_price) if order.delivery_price else None
    }

@router.post("/{order_id}/buyer-delivery-decision")
def buyer_delivery_decision(
    order_id: int,
    data: BuyerDeliveryDecision,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = OrderService.buyer_delivery_decision(db, order_id, current_user.id, data.accept)
    return {"status": order.status}

@router.post("/{order_id}/assign-delivery")
def assign_delivery(
    order_id: int,
    data: AssignDelivery,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    order = OrderService.assign_delivery(db, order_id, admin.id, data.delivery_id)
    return {"status": order.status}

@router.post("/{order_id}/buyer-confirm-and-pay")
def buyer_confirm_and_pay(
    order_id: int,
    data: BuyerConfirmAndPay,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = OrderService.buyer_confirm_and_pay(db, order_id, current_user.id, data.cash_paid, data.points_paid)
    return {
        "status": order.status,
        "order_id": order.id,
        "cash_paid": float(order.cash_paid),
        "points_paid": float(order.points_paid),
        "message": "Waiting seller confirmation"
    }

@router.post("/{order_id}/seller-confirm-payment")
def seller_confirm_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = OrderService.seller_confirm_payment(db, order_id, current_user.id)
    return {
        "status": "completed",
        "message": "Order finished successfully"
    }

@router.get("/seller/waiting-confirmation")
def seller_waiting_confirmation(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != "customer":
        raise HTTPException(403, "Only sellers allowed")

    orders = db.query(Order).filter(
        Order.seller_id == current_user.id,
        Order.status == "buyer_paid"
    ).order_by(Order.created_at.desc()).all()

    return {
        "seller_id": current_user.id,
        "count": len(orders),
        "orders": orders
    }

@router.get("/{order_id}/payment-summary")
def order_payment_summary(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    if current_user.id not in [order.user_id, order.seller_id]:
        raise HTTPException(403, "Not allowed")

    return {
        "order_id": order.id,
        "status": order.status,
        "cash_paid": float(order.cash_paid or 0),
        "points_paid": float(order.points_paid or 0),
        "seller_payment_confirmed": order.seller_payment_confirmed,
        "payment_type": order.payment_type,
        "delivery_requested": order.delivery_requested,
        "delivery_price": float(order.delivery_price or 0)
    }
