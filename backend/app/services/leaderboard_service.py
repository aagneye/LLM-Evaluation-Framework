from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import structlog

from app.models import Evaluation, ModelResponse, Prompt, Experiment
from app.schemas.leaderboard_schema import LeaderboardEntry, LeaderboardResponse, ModelMetricsDetail

logger = structlog.get_logger(__name__)


class LeaderboardService:
    """Service for generating leaderboards and model rankings."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_leaderboard(
        self,
        dataset_filter: Optional[str] = None,
        metric_filter: Optional[str] = None,
        limit: int = 50
    ) -> LeaderboardResponse:
        """
        Generate leaderboard with optional filtering.
        
        Args:
            dataset_filter: Filter by dataset name
            metric_filter: Sort by specific metric
            limit: Maximum number of entries
            
        Returns:
            LeaderboardResponse with ranked entries
        """
        logger.info(
            "generating_leaderboard",
            dataset_filter=dataset_filter,
            metric_filter=metric_filter,
            limit=limit
        )
        
        query = self.db.query(
            ModelResponse.model_name,
            func.avg(Evaluation.score).label('avg_score'),
            func.count(Evaluation.id).label('eval_count'),
            func.avg(ModelResponse.latency).label('avg_latency')
        ).join(
            Evaluation, ModelResponse.id == Evaluation.response_id
        )
        
        if dataset_filter:
            query = query.join(
                Prompt, ModelResponse.prompt_id == Prompt.id
            ).filter(
                Prompt.dataset_name == dataset_filter
            )
        
        query = query.group_by(ModelResponse.model_name)
        
        if metric_filter:
            metric_query = self.db.query(
                ModelResponse.model_name,
                func.avg(Evaluation.score).label('metric_avg')
            ).join(
                Evaluation, ModelResponse.id == Evaluation.response_id
            ).filter(
                Evaluation.metric == metric_filter
            ).group_by(ModelResponse.model_name).subquery()
            
            query = query.join(
                metric_query,
                ModelResponse.model_name == metric_query.c.model_name
            ).order_by(metric_query.c.metric_avg.desc())
        else:
            query = query.order_by(func.avg(Evaluation.score).desc())
        
        results = query.limit(limit).all()
        
        entries = []
        for rank, (model_name, avg_score, eval_count, avg_latency) in enumerate(results, 1):
            metric_scores = self._get_metric_breakdown(model_name, dataset_filter)
            
            entry = LeaderboardEntry(
                model_name=model_name,
                average_score=round(float(avg_score), 2),
                total_evaluations=eval_count,
                correctness_score=metric_scores.get('correctness'),
                hallucination_score=metric_scores.get('hallucination'),
                reasoning_score=metric_scores.get('reasoning'),
                safety_score=metric_scores.get('safety'),
                average_latency=round(float(avg_latency), 3) if avg_latency else None,
                rank=rank
            )
            entries.append(entry)
        
        logger.info("leaderboard_generated", total_models=len(entries))
        
        return LeaderboardResponse(
            entries=entries,
            total_models=len(entries),
            dataset_filter=dataset_filter,
            metric_filter=metric_filter
        )
    
    def _get_metric_breakdown(
        self,
        model_name: str,
        dataset_filter: Optional[str] = None
    ) -> Dict[str, float]:
        """Get average scores for each metric for a model."""
        query = self.db.query(
            Evaluation.metric,
            func.avg(Evaluation.score).label('avg_score')
        ).join(
            ModelResponse, Evaluation.response_id == ModelResponse.id
        ).filter(
            ModelResponse.model_name == model_name
        )
        
        if dataset_filter:
            query = query.join(
                Prompt, ModelResponse.prompt_id == Prompt.id
            ).filter(
                Prompt.dataset_name == dataset_filter
            )
        
        query = query.group_by(Evaluation.metric)
        
        results = query.all()
        
        return {
            metric: round(float(score), 2)
            for metric, score in results
        }
    
    def get_model_details(
        self,
        model_name: str,
        dataset_filter: Optional[str] = None
    ) -> Optional[ModelMetricsDetail]:
        """
        Get detailed metrics for a specific model.
        
        Args:
            model_name: Name of the model
            dataset_filter: Optional dataset filter
            
        Returns:
            ModelMetricsDetail or None if not found
        """
        query = self.db.query(
            func.count(Evaluation.id).label('eval_count'),
            func.avg(Evaluation.score).label('avg_score'),
            func.avg(ModelResponse.latency).label('avg_latency'),
            func.min(ModelResponse.latency).label('min_latency'),
            func.max(ModelResponse.latency).label('max_latency')
        ).join(
            ModelResponse, Evaluation.response_id == ModelResponse.id
        ).filter(
            ModelResponse.model_name == model_name
        )
        
        if dataset_filter:
            query = query.join(
                Prompt, ModelResponse.prompt_id == Prompt.id
            ).filter(
                Prompt.dataset_name == dataset_filter
            )
        
        result = query.first()
        
        if not result or result.eval_count == 0:
            return None
        
        metric_scores = self._get_metric_breakdown(model_name, dataset_filter)
        
        eval_distribution = self._get_evaluation_distribution(model_name, dataset_filter)
        
        latency_stats = {
            "average": round(float(result.avg_latency), 3) if result.avg_latency else 0,
            "min": round(float(result.min_latency), 3) if result.min_latency else 0,
            "max": round(float(result.max_latency), 3) if result.max_latency else 0,
        }
        
        logger.info("model_details_retrieved", model_name=model_name)
        
        return ModelMetricsDetail(
            model_name=model_name,
            total_evaluations=result.eval_count,
            average_score=round(float(result.avg_score), 2),
            metric_scores=metric_scores,
            latency_stats=latency_stats,
            evaluation_distribution=eval_distribution
        )
    
    def _get_evaluation_distribution(
        self,
        model_name: str,
        dataset_filter: Optional[str] = None
    ) -> Dict[str, int]:
        """Get distribution of evaluations by score range."""
        query = self.db.query(
            Evaluation.score
        ).join(
            ModelResponse, Evaluation.response_id == ModelResponse.id
        ).filter(
            ModelResponse.model_name == model_name
        )
        
        if dataset_filter:
            query = query.join(
                Prompt, ModelResponse.prompt_id == Prompt.id
            ).filter(
                Prompt.dataset_name == dataset_filter
            )
        
        scores = [float(score) for (score,) in query.all()]
        
        distribution = {
            "excellent (9-10)": sum(1 for s in scores if s >= 9),
            "good (7-9)": sum(1 for s in scores if 7 <= s < 9),
            "moderate (5-7)": sum(1 for s in scores if 5 <= s < 7),
            "poor (0-5)": sum(1 for s in scores if s < 5),
        }
        
        return distribution
    
    def get_dataset_leaderboards(self) -> Dict[str, LeaderboardResponse]:
        """Get separate leaderboards for each dataset."""
        datasets = self.db.query(Prompt.dataset_name).distinct().all()
        
        leaderboards = {}
        for (dataset_name,) in datasets:
            if dataset_name:
                leaderboards[dataset_name] = self.get_leaderboard(
                    dataset_filter=dataset_name,
                    limit=20
                )
        
        return leaderboards
