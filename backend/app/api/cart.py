from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.cart_item import CartItem
from app.models.product import Product

from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


# =====================================================
# 🛒 Add Product to Cart (Marketplace Only)
# =====================================================
@router.post("/add")
def add_to_cart(
    product_id: int,
    quantity: int = 1,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Validate product
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True,
        Product.is_sold == False,
        Product.status == "approved"
    ).first()

    if not product:
        raise HTTPException(404, "Product not found")

    if product.type != "marketplace":
        raise HTTPException(
            status_code=400,
            detail="Cart is only for marketplace products"
        )

    # Check existing item
    item = db.query(CartItem).filter(
        CartItem.user_id == user.id,
        CartItem.product_id == product_id
    ).first()

    if item:
        item.quantity += quantity
    else:
        item = CartItem(
            user_id=user.id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(item)

    db.commit()

    return {
        "status": "added",
        "product_id": product_id,
        "quantity": quantity
    }


# =====================================================
# 🛒 Remove Item from Cart
# =====================================================
@router.delete("/remove")
def remove_from_cart(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    item = db.query(CartItem).filter(
        CartItem.user_id == user.id,
        CartItem.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(404, "Item not found in cart")

    db.delete(item)
    db.commit()

    return {"status": "removed"}


# =====================================================
# 🛒 Clear My Cart
# =====================================================
@router.delete("/clear")
def clear_cart(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    db.query(CartItem).filter(
        CartItem.user_id == user.id
    ).delete()

    db.commit()

    return {"status": "cart cleared"}


# =====================================================
# 🛒 View My Cart
# =====================================================
@router.get("/me")
def view_my_cart(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    items = db.query(CartItem).filter(
        CartItem.user_id == user.id
    ).all()

    result = []

    for item in items:
        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        if product:
            result.append({
                "cart_item_id": item.id,
                "product_id": product.id,
                "name": product.name,
                "price": float(product.price),
                "seller_id": product.seller_id,
                "quantity": item.quantity,
                "image_url": product.image_url
            })

    return {
        "user_id": user.id,
        "count": len(result),
        "cart": result
    }
