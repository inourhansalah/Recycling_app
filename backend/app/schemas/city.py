from pydantic import BaseModel, ConfigDict


class CityOut(BaseModel):
    id: int
    name: str

    # Pydantic v2 replacement for orm_mode = True
    model_config = ConfigDict(from_attributes=True)
