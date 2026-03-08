from pydantic import BaseModel, ConfigDict

class CategoryCreate(BaseModel):
    name: str
    image_url: str
    type: str

class CategoryOut(BaseModel):
    id: int
    name: str
    image_url: str
    type: str

    model_config = ConfigDict(from_attributes=True)
