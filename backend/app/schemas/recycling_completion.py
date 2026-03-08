from pydantic import BaseModel
from typing import List, Optional


class RecyclingCompleteItem(BaseModel):
    item_id: int
    actual_quantity: float


class RecyclingCompletionRequest(BaseModel):
    items: List[RecyclingCompleteItem]

    payment_type: str   # cash | points | cash_points

    # ✅ Optional admin override
    final_reward_value: Optional[float] = None
    reward_notes: Optional[str] = None
