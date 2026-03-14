from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ModelResponseBase(BaseModel):
    prompt_id: int
    model_name: str
    response_text: str
    latency: Optional[float] = None


class ModelResponseCreate(ModelResponseBase):
    pass


class ModelResponseResponse(ModelResponseBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
