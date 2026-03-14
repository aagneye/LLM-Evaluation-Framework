from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import HumanFeedback, ModelResponse
from app.schemas.evaluation_schema import HumanFeedbackCreate, HumanFeedbackResponse

router = APIRouter(prefix="/human-feedback", tags=["human-feedback"])


@router.get("/", response_model=List[HumanFeedbackResponse])
def get_human_feedback(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all human feedback entries."""
    feedback = db.query(HumanFeedback).offset(skip).limit(limit).all()
    return feedback


@router.get("/response/{response_id}", response_model=List[HumanFeedbackResponse])
def get_feedback_for_response(response_id: int, db: Session = Depends(get_db)):
    """Get all human feedback for a specific response."""
    feedback = db.query(HumanFeedback).filter(
        HumanFeedback.response_id == response_id
    ).all()
    return feedback


@router.post("/", response_model=HumanFeedbackResponse)
def create_human_feedback(feedback: HumanFeedbackCreate, db: Session = Depends(get_db)):
    """Submit human feedback for a model response."""
    # Verify response exists
    response = db.query(ModelResponse).filter(
        ModelResponse.id == feedback.response_id
    ).first()
    
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    db_feedback = HumanFeedback(**feedback.model_dump())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback
