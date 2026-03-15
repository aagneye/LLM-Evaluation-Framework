from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import structlog

from app.models import Experiment, ModelResponse, Evaluation, Prompt
from app.schemas.comparison_schema import (
    ExperimentMetrics,
    MetricComparison,
    ExperimentComparisonResponse
)

logger = structlog.get_logger(__name__)


class ComparisonService:
    """Service for comparing experiments and their results."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def compare_experiments(
        self,
        experiment_ids: List[int]
    ) -> ExperimentComparisonResponse:
        """
        Compare multiple experiments across all metrics.
        
        Args:
            experiment_ids: List of experiment IDs to compare
            
        Returns:
            ExperimentComparisonResponse with detailed comparison
        """
        if len(experiment_ids) < 2:
            raise ValueError("Need at least 2 experiments to compare")
        
        logger.info("comparing_experiments", experiment_ids=experiment_ids)
        
        experiments_data = []
        all_metrics = set()
        
        for exp_id in experiment_ids:
            metrics = self._get_experiment_metrics(exp_id)
            if metrics:
                experiments_data.append(metrics)
                all_metrics.update(metrics.metric_scores.keys())
        
        if not experiments_data:
            raise ValueError("No valid experiments found")
        
        metric_comparisons = []
        for metric_name in all_metrics:
            comparison = self._compare_metric(metric_name, experiments_data)
            if comparison:
                metric_comparisons.append(comparison)
        
        best_exp_id = max(
            experiments_data,
            key=lambda x: x.average_score
        ).experiment_id
        
        summary = self._generate_summary(experiments_data, metric_comparisons)
        
        logger.info(
            "experiments_compared",
            count=len(experiments_data),
            best_experiment_id=best_exp_id
        )
        
        return ExperimentComparisonResponse(
            experiments=experiments_data,
            metric_comparisons=metric_comparisons,
            best_overall_experiment_id=best_exp_id,
            summary=summary
        )
    
    def _get_experiment_metrics(self, experiment_id: int) -> Optional[ExperimentMetrics]:
        """Get metrics for a single experiment."""
        experiment = self.db.query(Experiment).filter(
            Experiment.id == experiment_id
        ).first()
        
        if not experiment:
            logger.warning("experiment_not_found", experiment_id=experiment_id)
            return None
        
        responses_query = self.db.query(
            func.count(ModelResponse.id).label('total'),
            func.avg(ModelResponse.latency).label('avg_latency')
        ).filter(
            ModelResponse.experiment_id == experiment_id
        ).first()
        
        if not responses_query or responses_query.total == 0:
            return None
        
        evaluations_query = self.db.query(
            func.avg(Evaluation.score).label('avg_score')
        ).join(
            ModelResponse, Evaluation.response_id == ModelResponse.id
        ).filter(
            ModelResponse.experiment_id == experiment_id
        ).first()
        
        metric_scores = self._get_metric_breakdown(experiment_id)
        
        return ExperimentMetrics(
            experiment_id=experiment.id,
            experiment_name=experiment.name,
            model_name=experiment.model_name,
            dataset_name=experiment.dataset_name,
            total_responses=responses_query.total,
            average_score=round(float(evaluations_query.avg_score or 0), 2),
            average_latency=round(float(responses_query.avg_latency or 0), 3),
            metric_scores=metric_scores
        )
    
    def _get_metric_breakdown(self, experiment_id: int) -> Dict[str, float]:
        """Get average scores for each metric in an experiment."""
        results = self.db.query(
            Evaluation.metric,
            func.avg(Evaluation.score).label('avg_score')
        ).join(
            ModelResponse, Evaluation.response_id == ModelResponse.id
        ).filter(
            ModelResponse.experiment_id == experiment_id
        ).group_by(
            Evaluation.metric
        ).all()
        
        return {
            metric: round(float(score), 2)
            for metric, score in results
        }
    
    def _compare_metric(
        self,
        metric_name: str,
        experiments: List[ExperimentMetrics]
    ) -> Optional[MetricComparison]:
        """Compare a specific metric across experiments."""
        experiment_scores = {}
        
        for exp in experiments:
            score = exp.metric_scores.get(metric_name)
            if score is not None:
                experiment_scores[exp.experiment_id] = score
        
        if not experiment_scores:
            return None
        
        best_exp_id = max(experiment_scores, key=experiment_scores.get)
        worst_exp_id = min(experiment_scores, key=experiment_scores.get)
        
        score_range = max(experiment_scores.values()) - min(experiment_scores.values())
        
        return MetricComparison(
            metric_name=metric_name,
            experiment_scores=experiment_scores,
            best_experiment_id=best_exp_id,
            worst_experiment_id=worst_exp_id,
            score_range=round(score_range, 2)
        )
    
    def _generate_summary(
        self,
        experiments: List[ExperimentMetrics],
        comparisons: List[MetricComparison]
    ) -> Dict[str, any]:
        """Generate summary statistics for the comparison."""
        total_responses = sum(exp.total_responses for exp in experiments)
        avg_score_range = max(exp.average_score for exp in experiments) - min(exp.average_score for exp in experiments)
        avg_latency_range = max(exp.average_latency for exp in experiments) - min(exp.average_latency for exp in experiments)
        
        fastest_exp = min(experiments, key=lambda x: x.average_latency)
        slowest_exp = max(experiments, key=lambda x: x.average_latency)
        
        metric_winners = {}
        for comp in comparisons:
            best_exp = next(
                (exp for exp in experiments if exp.experiment_id == comp.best_experiment_id),
                None
            )
            if best_exp:
                metric_winners[comp.metric_name] = best_exp.experiment_name
        
        return {
            "total_experiments": len(experiments),
            "total_responses": total_responses,
            "average_score_range": round(avg_score_range, 2),
            "average_latency_range": round(avg_latency_range, 3),
            "fastest_experiment": {
                "id": fastest_exp.experiment_id,
                "name": fastest_exp.experiment_name,
                "latency": fastest_exp.average_latency
            },
            "slowest_experiment": {
                "id": slowest_exp.experiment_id,
                "name": slowest_exp.experiment_name,
                "latency": slowest_exp.average_latency
            },
            "metric_winners": metric_winners
        }
    
    def compare_models(
        self,
        model_names: List[str],
        dataset_filter: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Compare multiple models across all their experiments.
        
        Args:
            model_names: List of model names to compare
            dataset_filter: Optional dataset filter
            
        Returns:
            Comparison data for models
        """
        model_stats = {}
        
        for model_name in model_names:
            query = self.db.query(
                func.count(ModelResponse.id).label('total_responses'),
                func.avg(Evaluation.score).label('avg_score'),
                func.avg(ModelResponse.latency).label('avg_latency')
            ).join(
                Evaluation, ModelResponse.id == Evaluation.response_id
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
            
            if result and result.total_responses > 0:
                model_stats[model_name] = {
                    "total_responses": result.total_responses,
                    "average_score": round(float(result.avg_score or 0), 2),
                    "average_latency": round(float(result.avg_latency or 0), 3)
                }
        
        logger.info("models_compared", models=model_names, dataset=dataset_filter)
        
        return {
            "models": model_stats,
            "dataset_filter": dataset_filter
        }
