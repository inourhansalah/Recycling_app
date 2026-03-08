from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.favorite import Favorite
from app.models.product import Product

from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/favorites", tags=["Favorites"])


# =====================================================
# ⭐ Add Favorite
# =====================================================
@router.post("/add")
def add_to_favorites(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True,
        Product.status == "approved"
    ).first()

    if not product:
        raise HTTPException(404, "Product not found")

    if product.type != "marketplace":
        raise HTTPException(
            status_code=400,
            detail="Favorites only for marketplace products"
        )

    existing = db.query(Favorite).filter(
        Favorite.user_id == user.id,
        Favorite.product_id == product_id
    ).first()

    if existing:
        return {"status": "already in favorites"}

    fav = Favorite(
        user_id=user.id,
        product_id=product_id
    )

    db.add(fav)
    db.commit()

    return {"status": "added"}


# =====================================================
# ⭐ Remove Favorite
# =====================================================
@router.delete("/remove")
def remove_from_favorites(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    fav = db.query(Favorite).filter(
        Favorite.user_id == user.id,
        Favorite.product_id == product_id
    ).first()

    if not fav:
        raise HTTPException(404, "Favorite not found")

    db.delete(fav)
    db.commit()

    return {"status": "removed"}


# =====================================================
# ⭐ View My Favorites
# =====================================================
@router.get("/me")
def view_my_favorites(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    favorites = db.query(Favorite).filter(
        Favorite.user_id == user.id
    ).all()

    result = []

    for fav in favorites:
        product = db.query(Product).filter(
            Product.id == fav.product_id
        ).first()

        if product:
            result.append({
                "product_id": product.id,
                "name": product.name,
                "price": float(product.price),
                "image_url": product.image_url,
                "seller_id": product.seller_id
            })

    return {
        "user_id": user.id,
        "count": len(result),
        "favorites": result
    }
