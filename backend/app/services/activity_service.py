from datetime import datetime
from sqlalchemy.orm import Session
from app.models.activity_log import ActivityLog

def log_activity(
    db: Session,
    user_id: int,
    user_role: str,
    entity_type: str,
    entity_id: int,
    action: str,
    description: str,
    details: dict | None = None
):
    log = ActivityLog(
        user_id=user_id,
        user_role=user_role,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        description=description,
        details=details,
        created_at=datetime.utcnow()
    )

    db.add(log)
    db.commit()
    return log
