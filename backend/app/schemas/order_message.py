from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MessageCreate(BaseModel):
    message: Optional[str] = None
    attachment_url: Optional[str] = None
    attachment_type: Optional[str] = None


class MessageOut(BaseModel):
    id: int
    sender_id: int
    message: Optional[str]

    attachment_url: Optional[str]
    attachment_type: Optional[str]

    created_at: datetime

    class Config:
        from_attributes = True
