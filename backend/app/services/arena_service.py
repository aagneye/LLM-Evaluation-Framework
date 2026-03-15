import math
import random
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import structlog

from app.models import (
    ArenaComparison,
    ArenaEloRating,
    ModelResponse,
    Prompt
)
from app.schemas.arena_schema import (
    ArenaMatchup,
    EloRatingResponse,
    ArenaLeaderboard
)

logger = structlog.get_logger(__name__)


class ArenaService:
    """Service for Arena-style pairwise model comparisons with ELO ranking."""
    
    K_FACTOR = 32  # ELO K-factor for rating updates
    INITIAL_RATING = 1500.0
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_random_matchup(self, user_id: Optional[int] = None) -> Optional[ArenaMatchup]:
        """
        Get a random matchup of two model responses for the same prompt.
        
        Args:
            user_id: Optional user ID for tracking
            
        Returns:
            ArenaMatchup or None if no suitable pair found
        """
        prompts_with_multiple_responses = self.db.query(
            ModelResponse.prompt_id
        ).group_by(
            ModelResponse.prompt_id
        ).having(
            func.count(ModelResponse.id) >= 2
        ).all()
        
        if not prompts_with_multiple_responses:
            logger.warning("no_prompts_with_multiple_responses")
            return None
        
        prompt_id = random.choice([p[0] for p in prompts_with_multiple_responses])
        
        responses = self.db.query(ModelResponse).filter(
            ModelResponse.prompt_id == prompt_id
        ).all()
        
        if len(responses) < 2:
            return None
        
        response_a, response_b = random.sample(responses, 2)
        
        prompt = self.db.query(Prompt).filter(Prompt.id == prompt_id).first()
        
        if not prompt:
            return None
        
        logger.info(
            "matchup_generated",
            prompt_id=prompt_id,
            model_a=response_a.model_name,
            model_b=response_b.model_name
        )
        
        return ArenaMatchup(
            prompt_text=prompt.prompt_text,
            response_a=response_a.response_text,
            response_a_id=response_a.id,
            response_a_model=response_a.model_name,
            response_b=response_b.response_text,
            response_b_id=response_b.id,
            response_b_model=response_b.model_name
        )
    
    def submit_comparison(
        self,
        response_a_id: int,
        response_b_id: int,
        winner: str,
        user_id: Optional[int] = None
    ) -> ArenaComparison:
        """
        Submit a comparison result and update ELO ratings.
        
        Args:
            response_a_id: ID of response A
            response_b_id: ID of response B
            winner: 'A', 'B', or 'T' (tie)
            user_id: Optional user ID
            
        Returns:
            Created ArenaComparison
        """
        response_a = self.db.query(ModelResponse).filter(
            ModelResponse.id == response_a_id
        ).first()
        
        response_b = self.db.query(ModelResponse).filter(
            ModelResponse.id == response_b_id
        ).first()
        
        if not response_a or not response_b:
            raise ValueError("Invalid response IDs")
        
        if response_a.prompt_id != response_b.prompt_id:
            raise ValueError("Responses must be for the same prompt")
        
        comparison = ArenaComparison(
            prompt_id=response_a.prompt_id,
            response_a_id=response_a_id,
            response_b_id=response_b_id,
            winner=winner,
            user_id=user_id
        )
        
        self.db.add(comparison)
        self.db.commit()
        
        self._update_elo_ratings(
            response_a.model_name,
            response_b.model_name,
            winner
        )
        
        logger.info(
            "comparison_submitted",
            model_a=response_a.model_name,
            model_b=response_b.model_name,
            winner=winner
        )
        
        return comparison
    
    def _update_elo_ratings(
        self,
        model_a: str,
        model_b: str,
        winner: str
    ) -> None:
        """
        Update ELO ratings based on comparison result.
        
        Args:
            model_a: Name of model A
            model_b: Name of model B
            winner: 'A', 'B', or 'T'
        """
        rating_a = self._get_or_create_rating(model_a)
        rating_b = self._get_or_create_rating(model_b)
        
        expected_a = self._expected_score(rating_a.elo_rating, rating_b.elo_rating)
        expected_b = 1 - expected_a
        
        if winner == 'A':
            actual_a, actual_b = 1.0, 0.0
            rating_a.wins += 1
            rating_b.losses += 1
        elif winner == 'B':
            actual_a, actual_b = 0.0, 1.0
            rating_a.losses += 1
            rating_b.wins += 1
        else:  # Tie
            actual_a, actual_b = 0.5, 0.5
            rating_a.ties += 1
            rating_b.ties += 1
        
        new_rating_a = rating_a.elo_rating + self.K_FACTOR * (actual_a - expected_a)
        new_rating_b = rating_b.elo_rating + self.K_FACTOR * (actual_b - expected_b)
        
        rating_a.elo_rating = new_rating_a
        rating_b.elo_rating = new_rating_b
        rating_a.total_comparisons += 1
        rating_b.total_comparisons += 1
        
        self.db.commit()
        
        logger.info(
            "elo_ratings_updated",
            model_a=model_a,
            new_rating_a=new_rating_a,
            model_b=model_b,
            new_rating_b=new_rating_b
        )
    
    def _expected_score(self, rating_a: float, rating_b: float) -> float:
        """Calculate expected score for player A using ELO formula."""
        return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))
    
    def _get_or_create_rating(self, model_name: str) -> ArenaEloRating:
        """Get or create ELO rating for a model."""
        rating = self.db.query(ArenaEloRating).filter(
            ArenaEloRating.model_name == model_name
        ).first()
        
        if not rating:
            rating = ArenaEloRating(
                model_name=model_name,
                elo_rating=self.INITIAL_RATING
            )
            self.db.add(rating)
            self.db.commit()
            logger.info("elo_rating_created", model_name=model_name)
        
        return rating
    
    def get_leaderboard(self, limit: int = 50) -> ArenaLeaderboard:
        """
        Get Arena leaderboard sorted by ELO rating.
        
        Args:
            limit: Maximum number of entries
            
        Returns:
            ArenaLeaderboard with rankings
        """
        ratings = self.db.query(ArenaEloRating).order_by(
            ArenaEloRating.elo_rating.desc()
        ).limit(limit).all()
        
        total_comparisons = self.db.query(
            func.count(ArenaComparison.id)
        ).scalar() or 0
        
        rankings = []
        for rating in ratings:
            win_rate = 0.0
            if rating.total_comparisons > 0:
                win_rate = (rating.wins + 0.5 * rating.ties) / rating.total_comparisons
            
            rankings.append(EloRatingResponse(
                model_name=rating.model_name,
                elo_rating=round(rating.elo_rating, 1),
                total_comparisons=rating.total_comparisons,
                wins=rating.wins,
                losses=rating.losses,
                ties=rating.ties,
                win_rate=round(win_rate, 3),
                updated_at=rating.updated_at
            ))
        
        logger.info("arena_leaderboard_generated", total_models=len(rankings))
        
        return ArenaLeaderboard(
            rankings=rankings,
            total_models=len(rankings),
            total_comparisons=total_comparisons
        )
    
    def get_model_rating(self, model_name: str) -> Optional[EloRatingResponse]:
        """Get ELO rating for a specific model."""
        rating = self.db.query(ArenaEloRating).filter(
            ArenaEloRating.model_name == model_name
        ).first()
        
        if not rating:
            return None
        
        win_rate = 0.0
        if rating.total_comparisons > 0:
            win_rate = (rating.wins + 0.5 * rating.ties) / rating.total_comparisons
        
        return EloRatingResponse(
            model_name=rating.model_name,
            elo_rating=round(rating.elo_rating, 1),
            total_comparisons=rating.total_comparisons,
            wins=rating.wins,
            losses=rating.losses,
            ties=rating.ties,
            win_rate=round(win_rate, 3),
            updated_at=rating.updated_at
        )
