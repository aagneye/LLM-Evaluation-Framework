from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class ExperimentMetrics(BaseModel):
    """Metrics for a single experiment."""
    experiment_id: int
    experiment_name: str
    model_name: str
    dataset_name: str
    total_responses: int
    average_score: float
    average_latency: float
    metric_scores: Dict[str, float]


class MetricComparison(BaseModel):
    """Comparison of a specific metric across experiments."""
    metric_name: str
    experiment_scores: Dict[int, float]  # experiment_id -> score
    best_experiment_id: int
    worst_experiment_id: int
    score_range: float


class ExperimentComparisonResponse(BaseModel):
    """Detailed comparison between multiple experiments."""
    experiments: List[ExperimentMetrics]
    metric_comparisons: List[MetricComparison]
    best_overall_experiment_id: int
    summary: Dict[str, any]
