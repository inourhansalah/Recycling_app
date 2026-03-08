from pydantic import BaseModel
from typing import Optional

class ProductCreate(BaseModel):
    name: str
    price: float
    type: str                 # recycling | marketplace
    category_id: int
    image_url: str
    seller_id: int | None = None 
    # recycling only
    unit: Optional[str] = None
   
    # marketplace only
    description: Optional[str] = None
    pickup_address: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    type: str
    status: str
    image_url: str

    class Config:
        from_attributes = True


class AdminProductReview(BaseModel):
    admin_notes: str | None = None
