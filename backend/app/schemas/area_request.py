from pydantic import BaseModel, ConfigDict

class AreaRequestCreate(BaseModel):
    city_id: int
    latitude: float
    longitude: float
    address_text: str


class AreaRequestOut(BaseModel):
    id: int
    city_id: int
    address_text: str

    model_config = ConfigDict(from_attributes=True)
