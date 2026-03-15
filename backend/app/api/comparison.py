from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import structlog

from app.database import get_db
from app.schemas.comparison_schema import ExperimentComparisonResponse
from app.services.comparison_service import ComparisonService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/compare", tags=["Comparison"])


@router.get("/experiments", response_model=ExperimentComparisonResponse)
def compare_experiments(
    experiment_ids: List[int] = Query(..., description="List of experiment IDs to compare"),
    db: Session = Depends(get_db)
):
    """
    Compare multiple experiments across all metrics.
    
    Provides detailed comparison including:
    - Overall scores
    - Per-metric comparisons
    - Latency comparisons
    - Best/worst performers
    """
    if len(experiment_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="Need at least 2 experiment IDs to compare"
        )
    
    logger.info("experiment_comparison_requested", experiment_ids=experiment_ids)
    
    service = ComparisonService(db)
    
    try:
        return service.compare_experiments(experiment_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/models")
def compare_models(
    model_names: List[str] = Query(..., description="List of model names to compare"),
    dataset: Optional[str] = Query(None, description="Filter by dataset"),
    db: Session = Depends(get_db)
):
    """
    Compare multiple models across all their experiments.
    
    Optionally filter by dataset for fair comparison.
    """
    if len(model_names) < 2:
        raise HTTPException(
            status_code=400,
            detail="Need at least 2 model names to compare"
        )
    
    logger.info("model_comparison_requested", models=model_names, dataset=dataset)
    
    service = ComparisonService(db)
    return service.compare_models(model_names, dataset_filter=dataset)
