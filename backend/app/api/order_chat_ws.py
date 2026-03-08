from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.order_message import OrderMessage
from app.models.order import Order
from app.utils.security import decode_token
from app.services.notification_service import create_notification

router = APIRouter()

active_connections = {}


async def connect_user(order_id: int, websocket: WebSocket):
    await websocket.accept()
    active_connections.setdefault(order_id, []).append(websocket)


async def broadcast(order_id: int, message: dict):
    if order_id in active_connections:
        for ws in active_connections[order_id]:
            await ws.send_json(message)


@router.websocket("/ws/orders/{order_id}")
async def websocket_chat(
    websocket: WebSocket,
    order_id: int,
    db: Session = Depends(get_db)
):

    token = websocket.query_params.get("token")
    payload = decode_token(token)

    if not payload:
        await websocket.close(code=1008)
        return

    user_id = payload["user_id"]

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        await websocket.close()
        return

    if user_id not in [order.user_id, order.seller_id]:
        await websocket.close(code=1008)
        return

    await connect_user(order_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            message = data.get("message")
            attachment_url = data.get("attachment_url")
            attachment_type = data.get("attachment_type")

            # ✅ Prevent empty messages
            if not message and not attachment_url:
                continue

            msg = OrderMessage(
                order_id=order.id,
                sender_id=user_id,
                message=message,
                attachment_url=attachment_url,
                attachment_type=attachment_type,
            )

            db.add(msg)
            db.commit()
            db.refresh(msg)

            # 🔔 Notify the other party
            receiver_id = (
                order.seller_id
                if user_id == order.user_id
                else order.user_id
            )

            create_notification(
                db=db,
                user_id=receiver_id,
                title="New Message",
                message=f"New message in order #{order.id}",
                entity_type="order",
                entity_id=order.id
            )

            await broadcast(order_id, {
                "sender_id": user_id,
                "message": msg.message,
                "attachment_url": msg.attachment_url,
                "attachment_type": msg.attachment_type,
                "created_at": str(msg.created_at)
            })

    except WebSocketDisconnect:
        active_connections[order_id].remove(websocket)