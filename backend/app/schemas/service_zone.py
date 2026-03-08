from pydantic import BaseModel, ConfigDict
from typing import List


class ServiceZoneCreate(BaseModel):
    city_id: int
    name: str
    coordinates: List[List[float]]  
    # [[lng, lat], [lng, lat], ...]

class ServiceZoneOut(BaseModel):
    id: int
    name: str
    city_id: int

    model_config = ConfigDict(from_attributes=True)
