from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryOut

from app.services.activity_service import log_activity
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/categories", tags=["Categories"])


# =====================================================
# ✅ Admin Create Category
# =====================================================
@router.post("/", response_model=CategoryOut)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin only can create categories.
    """

    if current_user.role != "admin":
        raise HTTPException(403, "Admin only")

    category = Category(
        name=data.name,
        type=data.type,
        image_url=data.image_url
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    # ✅ Activity Log
    log_activity(
        db=db,
        user_id=current_user.id,
        user_role="admin",
        entity_type="category",
        entity_id=category.id,
        action="create",
        description="Admin created category",
        details={
            "name": category.name,
            "type": category.type
        }
    )

    return category


# =====================================================
# ✅ Public View Categories
# =====================================================
@router.get("/", response_model=list[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    """
    Anyone can view active categories.
    """

    return db.query(Category).filter(
        Category.is_active == True
    ).all()
