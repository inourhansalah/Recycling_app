from pydantic import BaseModel, ConfigDict


class RecyclingHubCreate(BaseModel):
    city_id: int
    name: str
    latitude: float
    longitude: float


class RecyclingHubOut(BaseModel):
    id: int
    city_id: int
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
