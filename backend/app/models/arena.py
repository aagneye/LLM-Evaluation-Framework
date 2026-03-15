from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.sql import func
from app.database import Base


class ArenaComparison(Base):
    """Store pairwise comparisons between model responses."""
    __tablename__ = "arena_comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    response_a_id = Column(Integer, ForeignKey("model_responses.id"), nullable=False)
    response_b_id = Column(Integer, ForeignKey("model_responses.id"), nullable=False)
    winner = Column(String(1), nullable=False)  # 'A', 'B', or 'T' (tie)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ArenaEloRating(Base):
    """Store ELO ratings for models."""
    __tablename__ = "arena_elo_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(255), unique=True, index=True, nullable=False)
    elo_rating = Column(Float, default=1500.0, nullable=False)
    total_comparisons = Column(Integer, default=0, nullable=False)
    wins = Column(Integer, default=0, nullable=False)
    losses = Column(Integer, default=0, nullable=False)
    ties = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
