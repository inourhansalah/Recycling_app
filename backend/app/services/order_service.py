from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.money_transaction import MoneyTransaction
from app.services.wallet_service import get_or_create_wallet, record_wallet_transaction
from app.services.activity_service import log_activity

class OrderService:
    @staticmethod
    def create_order(db: Session, user_id: int, data) -> list[Order]:
        if data.source == "recycling":
            if not data.delivery_requested:
                raise HTTPException(400, "Delivery is mandatory for recycling orders")

            order = Order(
                user_id=user_id,
                seller_id=None,
                address_id=data.address_id,
                source="recycling",
                delivery_requested=True,
                payment_type=data.payment_type,
                status="pending"
            )
            db.add(order)
            db.commit()
            db.refresh(order)

            for it in data.items:
                db.add(OrderItem(
                    order_id=order.id,
                    product_id=it.product_id,
                    estimated_quantity=it.estimated_quantity
                ))
            db.commit()

            log_activity(db, user_id, "customer", "order", order.id, "create", "Recycling order created")
            return [order]

        if data.source != "marketplace":
            raise HTTPException(400, "Invalid source")

        if not data.delivery_requested:
            if len(data.items) > 1:
                raise HTTPException(400, "Without delivery, checkout must be one product only")

            product = db.query(Product).filter(
                Product.id == data.items[0].product_id,
                Product.is_sold == False,
                Product.status == "approved"
            ).first()

            if not product:
                raise HTTPException(400, "Product not available")

            order = Order(
                user_id=user_id,
                seller_id=product.seller_id,
                address_id=data.address_id,
                source="marketplace",
                delivery_requested=False,
                payment_type=data.payment_type,
                status="pending"
            )
            db.add(order)
            db.commit()
            db.refresh(order)

            db.add(OrderItem(order_id=order.id, product_id=product.id, estimated_quantity=1))
            db.commit()

            log_activity(db, user_id, "customer", "order", order.id, "create", "Marketplace order created (no delivery)")
            return [order]

        # Marketplace WITH delivery
        product_ids = [it.product_id for it in data.items]
        products = db.query(Product).filter(
            Product.id.in_(product_ids),
            Product.is_sold == False,
            Product.status == "approved"
        ).all()

        if len(products) != len(product_ids):
            raise HTTPException(400, "Some products not available")

        seller_map = {}
        for p in products:
            seller_map.setdefault(p.seller_id, []).append(p)

        created_orders = []
        for seller_id, seller_products in seller_map.items():
            order = Order(
                user_id=user_id,
                seller_id=seller_id,
                address_id=data.address_id,
                source="marketplace",
                delivery_requested=True,
                payment_type=data.payment_type,
                status="pending"
            )
            db.add(order)
            db.commit()
            db.refresh(order)

            for prod in seller_products:
                db.add(OrderItem(order_id=order.id, product_id=prod.id, estimated_quantity=1))

            db.commit()
            created_orders.append(order)
            log_activity(db, user_id, "customer", "order", order.id, "create", f"Marketplace delivery order created for seller {seller_id}")

        return created_orders

    @staticmethod
    def seller_review(db: Session, order_id: int, seller_id: int, approve: bool):
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order or order.seller_id != seller_id:
            raise HTTPException(404 if not order else 403, "Order not found or not yours")

        if order.source != "marketplace":
            raise HTTPException(400, "Seller review only for marketplace")

        if approve:
            order.status = "seller_approved"
            order.seller_approved = True
            # Cancel other pending orders for same product
            OrderItemService.cancel_other_orders_for_product(db, order)
        else:
            order.status = "cancelled"

        db.commit()
        log_activity(db, seller_id, "customer", "order", order_id, "seller_review", "Seller reviewed the order")
        return order

    @staticmethod
    def admin_delivery_review(db: Session, order_id: int, admin_id: int, approve: bool, delivery_price: float = None, admin_notes: str = None):
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(404, "Order not found")

        if not order.delivery_requested:
            raise HTTPException(400, "Delivery not requested")

        if order.source == "marketplace" and not order.seller_approved:
            raise HTTPException(400, "Seller must approve first")

        if not approve:
            order.status = "cancelled"
            db.commit()
            log_activity(db, admin_id, "admin", "order", order.id, "delivery_rejected", "Admin rejected delivery request")
            return order

        if delivery_price is None:
            raise HTTPException(400, "Delivery price required")

        order.delivery_price = delivery_price
        order.admin_notes = admin_notes
        order.status = "delivery_priced"
        db.commit()
        log_activity(db, admin_id, "admin", "order", order.id, "delivery_priced", "Admin priced delivery successfully")
        return order

    @staticmethod
    def buyer_delivery_decision(db: Session, order_id: int, user_id: int, accept: bool):
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order or order.user_id != user_id:
            raise HTTPException(404 if not order else 403, "Order not found or not yours")

        if order.status != "delivery_priced":
            raise HTTPException(400, "Delivery not priced yet")

        if accept:
            order.status = "approved"
        else:
            order.delivery_requested = False
            order.delivery_price = None
            order.status = "seller_approved"

        db.commit()
        return order

    @staticmethod
    def assign_delivery(db: Session, order_id: int, admin_id: int, delivery_id: int):
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(404, "Order not found")

        if order.status != "approved":
            raise HTTPException(400, "Order must be approved first")

        order.assigned_delivery_id = delivery_id
        order.status = "assigned"
        db.commit()
        log_activity(db, admin_id, "admin", "order", order.id, "assign_delivery", "Admin assigned delivery person")
        return order

    @staticmethod
    def buyer_confirm_and_pay(db: Session, order_id: int, user_id: int, cash_paid: float, points_paid: float):
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order or order.user_id != user_id:
            raise HTTPException(404 if not order else 403, "Order not found or not yours")

        if order.status != "delivered_waiting_confirmation":
            raise HTTPException(400, f"Order not ready. Current status = {order.status}")

        if order.source != "marketplace":
            raise HTTPException(400, "Only marketplace orders allowed")

        if cash_paid > 0:
            db.add(MoneyTransaction(
                user_id=user_id,
                order_id=order.id,
                amount=cash_paid,
                currency="EGP",
                direction="pay",
                reason="marketplace_cash_record",
                notes="Buyer recorded offline cash payment",
                created_by=user_id
            ))
            order.cash_paid = cash_paid

        if points_paid > 0:
            buyer_wallet = get_or_create_wallet(db, user_id)
            seller_wallet = get_or_create_wallet(db, order.seller_id)

            if buyer_wallet.points_balance < points_paid:
                raise HTTPException(400, "Not enough points")

            buyer_wallet.points_balance -= points_paid
            record_wallet_transaction(db, buyer_wallet.id, points_paid, "spend", "marketplace_points_payment", user_id, order.id)

            seller_wallet.points_balance += points_paid
            record_wallet_transaction(db, seller_wallet.id, points_paid, "earn", "marketplace_points_payment", user_id, order.id)

            order.points_paid = points_paid

        order.status = "buyer_paid"
        db.commit()
        log_activity(db, user_id, "customer", "order", order.id, "buyer_confirm_and_pay", "Buyer confirmed delivery and recorded payment",
                     details={"cash_paid": float(cash_paid), "points_paid": float(points_paid)})
        return order

    @staticmethod
    def seller_confirm_payment(db: Session, order_id: int, seller_id: int):
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order or order.seller_id != seller_id:
            raise HTTPException(404 if not order else 403, "Order not found or not yours")

        if order.status != "buyer_paid":
            raise HTTPException(400, f"Order not ready. Current status = {order.status}")

        order.seller_payment_confirmed = True
        order.status = "completed"
        db.commit()
        log_activity(db, seller_id, "customer", "order", order.id, "seller_confirm_payment", "Seller confirmed payment received",
                     details={"cash_paid": float(order.cash_paid), "points_paid": float(order.points_paid)})
        return order

class OrderItemService:
    @staticmethod
    def cancel_other_orders_for_product(db: Session, order: Order):
        item = db.query(OrderItem).filter(OrderItem.order_id == order.id).first()
        if item:
            db.query(Order).join(OrderItem).filter(
                OrderItem.product_id == item.product_id,
                Order.id != order.id,
                Order.status == "pending"
            ).update({"status": "cancelled"})
