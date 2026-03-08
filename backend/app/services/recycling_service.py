from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.money_transaction import MoneyTransaction
from app.models.wallet_transaction import WalletTransaction
from app.services.wallet_service import get_or_create_wallet
from app.services.activity_service import log_activity
from app.config import RECYCLING_REWARD_CONVERSION_RATE

class RecyclingService:
    @staticmethod
    def complete_recycling_order(db: Session, order_id: int, admin_id: int, data):
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(404, "Order not found")

        if order.source != "recycling":
            raise HTTPException(400, "Only recycling orders allowed")

        if order.status not in ["collected", "delivered_to_hub"]:
            raise HTTPException(400, f"Order must be delivered first. Current status = {order.status}")

        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        if not order_items:
            raise HTTPException(400, "Order has no items")

        item_map = {item.id: item for item in order_items}
        total_quantity = 0

        for update in data.items:
            if update.item_id not in item_map:
                raise HTTPException(400, f"Item {update.item_id} does not belong to this order")
            item = item_map[update.item_id]
            item.actual_quantity = update.actual_quantity
            total_quantity += float(update.actual_quantity)

        system_value = 0
        for item in order_items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product or product.type != "recycling":
                raise HTTPException(400, "Order contains invalid or non-recycling product")
            if item.actual_quantity is None:
                raise HTTPException(400, "Actual quantity missing")
            system_value += float(product.price) * float(item.actual_quantity)

        final_value = system_value
        overridden = False
        if data.final_reward_value is not None:
            final_value = float(data.final_reward_value)
            overridden = True

        order.system_reward_value = system_value
        order.final_reward_value = final_value
        order.reward_overridden = overridden
        order.reward_notes = data.reward_notes

        customer_wallet = get_or_create_wallet(db, order.user_id)
        points_given = 0
        cash_given = 0

        if data.payment_type in ["cash", "cash_points"]:
            cash_given = final_value
            db.add(MoneyTransaction(
                user_id=order.user_id,
                order_id=order.id,
                amount=cash_given,
                currency="EGP",
                direction="receive",
                reason="recycling_cash_reward",
                notes="Paid offline by admin",
                created_by=admin_id
            ))

        if data.payment_type in ["points", "cash_points"]:
            points_given = final_value * RECYCLING_REWARD_CONVERSION_RATE
            customer_wallet.points_balance += points_given
            db.add(WalletTransaction(
                wallet_id=customer_wallet.id,
                order_id=order.id,
                amount=points_given,
                direction="earn",
                reason="recycling_reward",
                created_by=admin_id
            ))

        order.status = "completed"
        db.commit()

        log_activity(db, admin_id, "admin", "order", order.id, "recycling_completed", 
                     "Admin completed recycling order", 
                     details={
                         "items_count": len(data.items),
                         "total_quantity": total_quantity,
                         "system_value": system_value,
                         "final_value": final_value,
                         "reward_overridden": overridden,
                         "payment_type": data.payment_type,
                         "cash_given": cash_given,
                         "points_given": points_given
                     })

        return {
            "status": "completed",
            "order_id": order.id,
            "items_completed": len(data.items),
            "total_quantity": total_quantity,
            "reward": {
                "system_value": system_value,
                "final_value": final_value,
                "overridden": overridden,
                "notes": data.reward_notes,
                "cash": cash_given,
                "points": points_given
            }
        }
