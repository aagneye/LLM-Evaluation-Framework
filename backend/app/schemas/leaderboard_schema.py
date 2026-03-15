from typing import Optional, List
from pydantic import BaseModel, Field


class LeaderboardEntry(BaseModel):
    """Single entry in the leaderboard."""
    model_name: str
    average_score: float = Field(..., ge=0.0, le=10.0)
    total_evaluations: int = Field(..., ge=0)
    correctness_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    hallucination_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    reasoning_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    safety_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    average_latency: Optional[float] = Field(None, ge=0.0)
    rank: int = Field(..., ge=1)


class LeaderboardResponse(BaseModel):
    """Leaderboard response with filtering info."""
    entries: List[LeaderboardEntry]
    total_models: int
    dataset_filter: Optional[str] = None
    metric_filter: Optional[str] = None


class ModelMetricsDetail(BaseModel):
    """Detailed metrics for a specific model."""
    model_name: str
    total_evaluations: int
    average_score: float
    metric_scores: dict
    latency_stats: dict
    evaluation_distribution: dict
