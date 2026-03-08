from pydantic import BaseModel, ConfigDict


class AddressCreate(BaseModel):
    city_id: int
    latitude: float
    longitude: float
    address_text: str



class AddressOut(BaseModel):
    id: int
    city_id: int
    address_text: str

    # Pydantic v2 replacement for orm_mode = True
    model_config = ConfigDict(from_attributes=True)
