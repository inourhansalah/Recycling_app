from pydantic import BaseModel

class ProductImageCreate(BaseModel):
    image_url: str
    is_cover: bool = False
