from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.activity_log import ActivityLog

from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/activity-logs", tags=["Activity Logs"])


# =====================================================
# ✅ User Views His Own Logs ONLY
# =====================================================
@router.get("/me")
def my_activity_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logs = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id
    ).order_by(ActivityLog.created_at.desc()).all()

    return {
        "user_id": current_user.id,
        "count": len(logs),
        "logs": logs
    }


# =====================================================
# ✅ Admin Views Logs for Any Order
# =====================================================
@router.get("/order/{order_id}")
def order_activity_logs(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin only")

    logs = db.query(ActivityLog).filter(
        ActivityLog.entity_type == "order",
        ActivityLog.entity_id == order_id
    ).order_by(ActivityLog.created_at.desc()).all()

    return {
        "order_id": order_id,
        "count": len(logs),
        "logs": logs
    }


# =====================================================
# ✅ Admin Views All System Logs
# =====================================================
@router.get("/admin/all")
def admin_all_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin only")

    logs = db.query(ActivityLog).order_by(
        ActivityLog.created_at.desc()
    ).all()

    return {
        "count": len(logs),
        "logs": logs
    }
