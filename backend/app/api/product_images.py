from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.product import Product
from app.models.product_image import ProductImage
from app.schemas.product_image import ProductImageCreate

from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/product-images", tags=["Product Images"])


# =====================================================
# ✅ Seller Add Product Images
# =====================================================
@router.post("/{product_id}")
def add_product_images(
    product_id: int,
    images: list[ProductImageCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(404, "Product not found")

    if product.type != "marketplace":
        raise HTTPException(400, "Only marketplace products allow images")

    # ✅ Seller Ownership
    if product.seller_id != current_user.id:
        raise HTTPException(403, "Not your product")

    # Cover reset
    if any(img.is_cover for img in images):
        db.query(ProductImage).filter(
            ProductImage.product_id == product_id,
            ProductImage.is_cover == True
        ).update({"is_cover": False})

    for img in images:
        db.add(ProductImage(
            product_id=product_id,
            image_url=img.image_url,
            is_cover=img.is_cover
        ))

        if img.is_cover:
            product.image_url = img.image_url

    db.commit()

    return {"status": "images added"}
