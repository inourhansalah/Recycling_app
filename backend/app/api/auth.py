# app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User

from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# =====================================================
# ✅ Register (Customer Only)
# =====================================================
@router.post("/register")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.phone == data.phone).first()
    if existing:
        raise HTTPException(400, "Phone already registered")

    # ✅ SECURITY FIX:
    # Any new user must always be customer
    user = User(
        name=data.name,
        phone=data.phone,
        role="customer",   # 🔥 FORCE CUSTOMER ONLY
        password_hash=hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "status": "registered",
        "user_id": user.id,
        "role": user.role
    }


# =====================================================
# ✅ Login
# =====================================================
@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user:
        raise HTTPException(404, "User not found")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid password")

    token = create_access_token({
        "user_id": user.id,
        "role": user.role
    })

    return TokenResponse(access_token=token)
