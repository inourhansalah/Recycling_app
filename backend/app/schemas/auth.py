from pydantic import BaseModel


# =====================================================
# Register Schema
# =====================================================
class RegisterRequest(BaseModel):
    name: str
    phone: str
    password: str
  


# =====================================================
# Login Schema
# =====================================================
class LoginRequest(BaseModel):
    phone: str
    password: str


# =====================================================
# Token Response
# =====================================================
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
