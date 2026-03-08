from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.product import Product
from app.models.category import Category

from app.schemas.product import ProductCreate, ProductOut

from app.services.activity_service import log_activity
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/products", tags=["Products"])


# =====================================================
# ✅ Create Product (Secured)
# =====================================================
@router.post("/", response_model=ProductOut)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ✅ Seller creates marketplace products
    ✅ Admin creates recycling products
    """

    # ===============================
    # Category Check
    # ===============================
    category = db.query(Category).filter(
        Category.id == data.category_id,
        Category.is_active == True
    ).first()

    if not category:
        raise HTTPException(400, "Category not found")

    if category.type != data.type:
        raise HTTPException(400, "Category type does not match product type")

    # ===============================
    # Recycling Product → Admin Only
    # ===============================
    if data.type == "recycling":

        if current_user.role != "admin":
            raise HTTPException(403, "Only admin can add recycling products")

        if not data.unit:
            raise HTTPException(400, "unit required for recycling products")

        exists = db.query(Product).filter(
            Product.type == "recycling",
            Product.category_id == data.category_id,
            Product.name.ilike(data.name),
            Product.is_active == True
        ).first()

        if exists:
            raise HTTPException(400, "Recycling product already exists")

        status = "approved"
        seller_id = None

    # ===============================
    # Marketplace Product → Seller Only
    # ===============================
    elif data.type == "marketplace":

        if current_user.role != "customer":
            raise HTTPException(403, "Only sellers can add marketplace products")

        if not data.description or not data.pickup_address:
            raise HTTPException(
                400,
                "description and pickup_address required"
            )

        status = "pending"
        seller_id = current_user.id

    else:
        raise HTTPException(400, "Invalid product type")

    # ===============================
    # Create Product
    # ===============================
    product = Product(
        name=data.name,
        price=data.price,
        unit=data.unit,
        description=data.description,
        pickup_address=data.pickup_address,
        category_id=data.category_id,
        type=data.type,
        image_url=data.image_url,
        status=status,
        seller_id=seller_id
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    # ===============================
    # Activity Log
    # ===============================
    log_activity(
        db=db,
        user_id=current_user.id,
        user_role=current_user.role,
        entity_type="product",
        entity_id=product.id,
        action="create",
        description="Product created",
        details={
            "name": product.name,
            "type": product.type,
            "status": product.status
        }
    )

    return product


# =====================================================
# ✅ Public Products (Approved Only)
# =====================================================
@router.get("/", response_model=list[ProductOut])
def get_products(db: Session = Depends(get_db)):

    return db.query(Product).filter(
        Product.is_active == True,
        Product.status == "approved"
    ).all()


# =====================================================
# ✅ Admin View All Products
# =====================================================
@router.get("/admin", response_model=list[ProductOut])
def get_products_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin only")

    return db.query(Product).all()


# =====================================================
# ✅ Admin View Pending Marketplace Products
# =====================================================
@router.get("/admin/pending", response_model=list[ProductOut])
def get_pending_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin only")

    return db.query(Product).filter(
        Product.type == "marketplace",
        Product.status == "pending"
    ).all()


# =====================================================
# ✅ Admin Approve Product
# =====================================================
@router.post("/{product_id}/approve")
def approve_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin only")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    product.status = "approved"
    product.admin_notes = None

    db.commit()

    log_activity(
        db=db,
        user_id=current_user.id,
        user_role="admin",
        entity_type="product",
        entity_id=product.id,
        action="approve",
        description="Admin approved product"
    )

    return {"status": "approved"}


# =====================================================
# ✅ Admin Reject Product
# =====================================================
@router.post("/{product_id}/reject")
def reject_product(
    product_id: int,
    admin_notes: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin only")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    product.status = "rejected"
    product.admin_notes = admin_notes

    db.commit()

    log_activity(
        db=db,
        user_id=current_user.id,
        user_role="admin",
        entity_type="product",
        entity_id=product.id,
        action="reject",
        description="Admin rejected product",
        details={"reason": admin_notes}
    )

    return {"status": "rejected"}
