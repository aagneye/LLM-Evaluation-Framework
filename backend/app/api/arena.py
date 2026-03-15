from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import structlog

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.arena_schema import (
    ArenaComparisonCreate,
    ArenaComparisonResponse,
    ArenaMatchup,
    ArenaLeaderboard,
    EloRatingResponse
)
from app.services.arena_service import ArenaService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/arena", tags=["Arena Evaluation"])


@router.get("/matchup", response_model=ArenaMatchup)
def get_matchup(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a random matchup of two model responses for pairwise comparison.
    
    Returns two responses for the same prompt for the user to compare.
    """
    service = ArenaService(db)
    matchup = service.get_random_matchup(user_id=current_user.id)
    
    if not matchup:
        raise HTTPException(
            status_code=404,
            detail="No suitable matchups available. Need at least 2 responses per prompt."
        )
    
    return matchup


@router.post("/compare", response_model=ArenaComparisonResponse)
def submit_comparison(
    comparison: ArenaComparisonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a comparison result between two responses.
    
    Winner should be 'A', 'B', or 'T' (tie).
    This updates the ELO ratings for both models.
    """
    service = ArenaService(db)
    
    try:
        result = service.submit_comparison(
            response_a_id=comparison.response_a_id,
            response_b_id=comparison.response_b_id,
            winner=comparison.winner,
            user_id=current_user.id
        )
        
        logger.info(
            "arena_comparison_submitted",
            user_id=current_user.id,
            winner=comparison.winner
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/leaderboard", response_model=ArenaLeaderboard)
def get_arena_leaderboard(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get Arena leaderboard with ELO rankings.
    
    Models are ranked by their ELO rating computed from pairwise comparisons.
    """
    service = ArenaService(db)
    return service.get_leaderboard(limit=limit)


@router.get("/rating/{model_name}", response_model=EloRatingResponse)
def get_model_rating(
    model_name: str,
    db: Session = Depends(get_db)
):
    """Get ELO rating and statistics for a specific model."""
    service = ArenaService(db)
    rating = service.get_model_rating(model_name)
    
    if not rating:
        raise HTTPException(
            status_code=404,
            detail=f"No rating found for model: {model_name}"
        )
    
    return rating
