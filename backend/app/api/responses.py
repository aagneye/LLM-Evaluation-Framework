from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import ModelResponse
from app.schemas.response_schema import ModelResponseCreate, ModelResponseResponse

router = APIRouter(prefix="/responses", tags=["responses"])


@router.get("/", response_model=List[ModelResponseResponse])
def get_responses(
    skip: int = 0, 
    limit: int = 100, 
    model_name: str = None,
    db: Session = Depends(get_db)
):
    """Get all model responses with optional filtering."""
    query = db.query(ModelResponse)
    
    if model_name:
        query = query.filter(ModelResponse.model_name == model_name)
    
    responses = query.offset(skip).limit(limit).all()
    return responses


@router.get("/{response_id}", response_model=ModelResponseResponse)
def get_response(response_id: int, db: Session = Depends(get_db)):
    """Get a specific response by ID."""
    response = db.query(ModelResponse).filter(ModelResponse.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    return response


@router.post("/", response_model=ModelResponseResponse)
def create_response(response: ModelResponseCreate, db: Session = Depends(get_db)):
    """Create a new model response."""
    db_response = ModelResponse(**response.model_dump())
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return db_response
