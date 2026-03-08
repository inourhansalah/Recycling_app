from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.database import get_db
from app.models.notification import Notification
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# =====================================================
# 1️⃣ Get My Notifications (Paginated)
# =====================================================
@router.get("/me")
def get_my_notifications(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if page < 1:
        page = 1

    offset = (page - 1) * limit

    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_deleted == False
    ).order_by(
        desc(Notification.created_at)
    ).offset(offset).limit(limit).all()

    return {
        "page": page,
        "limit": limit,
        "count": len(notifications),
        "notifications": notifications
    }


# =====================================================
# 2️⃣ Get Unread Count
# =====================================================
@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
        Notification.is_deleted == False
    ).count()

    return {"unread_count": count}


# =====================================================
# 3️⃣ Mark Single Notification as Read
# =====================================================
@router.post("/{notification_id}/mark-read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
        Notification.is_deleted == False
    ).first()

    if not notification:
        raise HTTPException(404, "Notification not found")

    notification.is_read = True
    db.commit()

    return {"status": "marked_as_read"}


# =====================================================
# 4️⃣ Mark All Notifications as Read
# =====================================================
@router.post("/mark-all-read")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_deleted == False
    ).update({"is_read": True})

    db.commit()

    return {"status": "all_marked_as_read"}


# =====================================================
# 5️⃣ Soft Delete Notification
# =====================================================
@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(404, "Notification not found")

    notification.is_deleted = True
    db.commit()

    return {"status": "deleted"}