from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.address import Address
from app.schemas.order import BuyerOrderDetailsOut
from app.utils.dependencies import get_current_user

router = APIRouter(
    prefix="/buyer-orders",
    tags=["Buyer Orders"]
)

@router.get("/{order_id}", response_model=BuyerOrderDetailsOut)
def buyer_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    buyer=Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order or order.user_id != buyer.id:
        raise HTTPException(404 if not order else 403, "Order not found or not yours")

    # Buyer Address
    address = db.query(Address).filter(Address.id == order.address_id).first()
    buyer_address_text = address.address_text if address else None

    # Seller Pickup Address (Marketplace Only)
    pickup_address = None
    if order.source == "marketplace":
        item = db.query(OrderItem).filter(OrderItem.order_id == order.id).first()
        if item:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                pickup_address = product.pickup_address

    return {
        "id": order.id,
        "status": order.status,
        "source": order.source,
        "delivery_requested": order.delivery_requested,
        "delivery_price": float(order.delivery_price) if order.delivery_price else None,
        "payment_type": order.payment_type,
        "buyer_address": buyer_address_text,
        "seller_pickup_address": pickup_address,
        "assigned_delivery_id": order.assigned_delivery_id
    }

@router.get("/me/history")
def buyer_orders_history(
    db: Session = Depends(get_db),
    buyer=Depends(get_current_user)
):
    orders = db.query(Order).filter(
        Order.user_id == buyer.id
    ).order_by(Order.created_at.desc()).all()

    return {
        "buyer_id": buyer.id,
        "count": len(orders),
        "orders": orders
    }

@router.get("/me/active")
def buyer_active_orders(
    db: Session = Depends(get_db),
    buyer=Depends(get_current_user)
):
    active_orders = db.query(Order).filter(
        Order.user_id == buyer.id,
        Order.status.in_([
            "pending",
            "seller_approved",
            "delivery_priced",
            "approved",
            "assigned",
            "on_the_way",
            "collected",
            "delivered_to_hub",
            "delivered_waiting_confirmation",
            "buyer_paid"
        ])
    ).order_by(Order.created_at.desc()).all()

    return {
        "buyer_id": buyer.id,
        "active_count": len(active_orders),
        "orders": active_orders
    }
