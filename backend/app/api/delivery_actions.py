from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.address import Address
from app.models.recycling_hub import RecyclingHub

from app.services.activity_service import log_activity
from app.utils.dependencies import get_current_user

from app.models.user import User

router = APIRouter(
    prefix="/delivery-actions",
    tags=["Delivery Actions"]
)


# =====================================================
# Helper → Delivery can only act on his assigned orders
# =====================================================
def get_delivery_order(order_id: int, delivery_id: int, db: Session):

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.assigned_delivery_id == delivery_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found or not assigned to this delivery"
        )

    return order


# =====================================================
# 1️⃣ Delivery View Order Details
# =====================================================
@router.get("/order/{order_id}")
def delivery_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delivery sees pickup & dropoff.
    """

    if current_user.role != "delivery":
        raise HTTPException(403, "Only delivery allowed")

    order = get_delivery_order(order_id, current_user.id, db)

    buyer_address = db.query(Address).filter(
        Address.id == order.address_id
    ).first()

    pickup = None
    dropoff = None

    # Recycling → Buyer → Hub
    if order.source == "recycling":

        pickup = buyer_address.address_text

        hubs = db.query(RecyclingHub).filter(
            RecyclingHub.city_id == buyer_address.city_id,
            RecyclingHub.is_active == True
        ).all()

        if not hubs:
            raise HTTPException(404, "No recycling hubs in this city")

        dropoff = hubs[0].name  # Phase 12: pick first hub


    

    # Marketplace → Seller → Buyer
    elif order.source == "marketplace":

        item = db.query(OrderItem).filter(
            OrderItem.order_id == order.id
        ).first()

        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        pickup = product.pickup_address
        dropoff = buyer_address.address_text

    return {
        "order_id": order.id,
        "status": order.status,
        "source": order.source,
        "pickup_location": pickup,
        "dropoff_location": dropoff,
        "delivery_price": float(order.delivery_price or 0)
    }


# =====================================================
# 2️⃣ Delivery Start Trip → on_the_way
# =====================================================
@router.post("/order/{order_id}/start")
def delivery_start_trip(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    assigned → on_the_way
    """

    if current_user.role != "delivery":
        raise HTTPException(403, "Only delivery allowed")

    order = get_delivery_order(order_id, current_user.id, db)

    if order.status != "assigned":
        raise HTTPException(400, "Order must be assigned first")

    order.status = "on_the_way"
    db.commit()

    log_activity(
        db=db,
        user_id=current_user.id,
        user_role="delivery",
        entity_type="order",
        entity_id=order.id,
        action="start_trip",
        description="Delivery started the trip"
    )

    return {"status": "on_the_way"}


# =====================================================
# 3️⃣ Delivery Collected Items → collected
# =====================================================
@router.post("/order/{order_id}/collected")
def delivery_collected_items(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    on_the_way → collected
    """

    if current_user.role != "delivery":
        raise HTTPException(403, "Only delivery allowed")

    order = get_delivery_order(order_id, current_user.id, db)

    if order.status != "on_the_way":
        raise HTTPException(400, "Order must be on_the_way first")

    order.status = "collected"
    db.commit()

    log_activity(
        db=db,
        user_id=current_user.id,
        user_role="delivery",
        entity_type="order",
        entity_id=order.id,
        action="collected_items",
        description="Delivery collected the items"
    )

    return {"status": "collected"}


# =====================================================
# 4️⃣ Delivery Delivered → delivered_waiting_confirmation
# =====================================================
@router.post("/order/{order_id}/delivered")
def delivery_delivered_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    collected → delivered_waiting_confirmation
    """

    if current_user.role != "delivery":
        raise HTTPException(403, "Only delivery allowed")

    order = get_delivery_order(order_id, current_user.id, db)

    if order.status != "collected":
        raise HTTPException(400, "Order must be collected first")

    if order.source == "recycling":
        order.status = "delivered_to_hub"
    else:
        order.status = "delivered_waiting_confirmation"
    db.commit()

    log_activity(
        db=db,
        user_id=current_user.id,
        user_role="delivery",
        entity_type="order",
        entity_id=order.id,
        action="delivered",
        description="Delivery delivered the order successfully"
    )

    if order.source == "recycling":
        return {
            "status": "delivered_to_hub",
            "message": "Delivered successfully to recycling hub"
        }

    return {
        "status": "delivered_waiting_confirmation",
        "message": "Waiting buyer confirmation"
    }