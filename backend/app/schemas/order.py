# app/schemas/order.py

from pydantic import BaseModel
from typing import List, Optional

class OrderItemCreate(BaseModel):
    product_id: int
    estimated_quantity: float


class OrderCreate(BaseModel):
    address_id: int
    items: List[OrderItemCreate]
    source: str
    delivery_requested: bool
    payment_type: str            # cash | points | cash_points


# seller review (marketplace only)
class SellerReviewOrder(BaseModel):
    approve: bool
    seller_notes: Optional[str] = None


# admin delivery pricing
class AdminDeliveryReview(BaseModel):
    approve: bool
    delivery_price: Optional[float] = None
    admin_notes: Optional[str] = None


class AssignDelivery(BaseModel):
    delivery_id: int


class BuyerConfirm(BaseModel):
    confirm: bool


class OrderOut(BaseModel):
    id: int
    status: str
    source: str
    delivery_requested: bool
    seller_id: int | None = None

    class Config:
        from_attributes = True


class BuyerOrderDetailsOut(BaseModel):
    id: int
    status: str
    source: str

    delivery_requested: bool
    delivery_price: float | None
    payment_type: str | None

    buyer_address: str | None
    seller_pickup_address: str | None

    assigned_delivery_id: int | None

    class Config:
        from_attributes = True


class AdminDeliveryOrderView(BaseModel):
    order_id: int
    buyer_address: str
    seller_pickup_address: str
    delivery_requested: bool
    payment_type: str

class BuyerDeliveryDecision(BaseModel):
    accept: bool



class BuyerConfirmAndPay(BaseModel):
    cash_paid: float = 0
    points_paid: float = 0
