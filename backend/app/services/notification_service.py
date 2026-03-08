from sqlalchemy.orm import Session
from app.models.notification import Notification

def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    entity_type: str = None,
    entity_id: int = None
):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        entity_type=entity_type,
        entity_id=entity_id
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification
