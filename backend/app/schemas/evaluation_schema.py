from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class EvaluationBase(BaseModel):
    response_id: int
    metric: str
    score: float
    evaluation_method: str
    details: Optional[str] = None


class EvaluationCreate(EvaluationBase):
    pass


class EvaluationResponse(EvaluationBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class HumanFeedbackBase(BaseModel):
    response_id: int
    score: float
    reviewer_name: Optional[str] = None
    notes: Optional[str] = None


class HumanFeedbackCreate(HumanFeedbackBase):
    pass


class HumanFeedbackResponse(HumanFeedbackBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ExperimentBase(BaseModel):
    experiment_name: str
    model_name: str
    dataset_name: str


class ExperimentCreate(ExperimentBase):
    pass


class ExperimentResponse(ExperimentBase):
    id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
