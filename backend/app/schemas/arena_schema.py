from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ArenaComparisonCreate(BaseModel):
    """Create a new arena comparison."""
    response_a_id: int
    response_b_id: int
    winner: str = Field(..., pattern="^[ABT]$", description="Winner: 'A', 'B', or 'T' (tie)")


class ArenaComparisonResponse(BaseModel):
    """Arena comparison response."""
    id: int
    prompt_id: int
    response_a_id: int
    response_b_id: int
    winner: str
    user_id: Optional[int]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ArenaMatchup(BaseModel):
    """Arena matchup for user voting."""
    prompt_text: str
    response_a: str
    response_a_id: int
    response_a_model: str
    response_b: str
    response_b_id: int
    response_b_model: str


class EloRatingResponse(BaseModel):
    """ELO rating for a model."""
    model_name: str
    elo_rating: float
    total_comparisons: int
    wins: int
    losses: int
    ties: int
    win_rate: float
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ArenaLeaderboard(BaseModel):
    """Arena leaderboard with ELO rankings."""
    rankings: List[EloRatingResponse]
    total_models: int
    total_comparisons: int
