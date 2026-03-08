from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.recycling_service import RecyclingService
from app.utils.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.recycling_completion import RecyclingCompletionRequest

router = APIRouter(
    prefix="/recycling-completion",
    tags=["Recycling Completion"]
)

@router.post("/{order_id}/complete")
def complete_recycling_order(
    order_id: int,
    data: RecyclingCompletionRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin"))
):
    return RecyclingService.complete_recycling_order(db, order_id, admin.id, data)
