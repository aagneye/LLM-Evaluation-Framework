from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PromptBase(BaseModel):
    prompt_text: str
    category: Optional[str] = None
    dataset_name: Optional[str] = None


class PromptCreate(PromptBase):
    pass


class PromptResponse(PromptBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
