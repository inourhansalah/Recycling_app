from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.utils.security import decode_token

# Login endpoint for Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# =====================================================
# ✅ Get Current Logged User
# =====================================================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(User.id == payload["user_id"]).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# =====================================================
# ✅ Role Guard Dependency
# =====================================================
def require_role(role: str):
    def checker(user: User = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(
                status_code=403,
                detail="Not allowed"
            )
        return user

    return checker
