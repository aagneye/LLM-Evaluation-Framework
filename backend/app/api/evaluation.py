from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.database import get_db
from app.models import Evaluation, ModelResponse, Prompt
from app.schemas.evaluation_schema import EvaluationCreate, EvaluationResponse
from app.schemas.leaderboard_schema import LeaderboardResponse, ModelMetricsDetail
from app.services.evaluation_engine import EvaluationEngine
from app.services.llm_judge import LLMJudge
from app.services.metrics_service import MetricsService
from app.services.leaderboard_service import LeaderboardService
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("/evaluate-response")
def evaluate_response(
    response_id: int,
    method: str = "rule",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Evaluate a model response using specified method.
    Methods: 'rule' (rule-based), 'llm' (LLM-as-judge)
    """
    response = db.query(ModelResponse).filter(ModelResponse.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    prompt = db.query(Prompt).filter(Prompt.id == response.prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    if method == "rule":
        engine = EvaluationEngine()
        result = engine.evaluate(prompt.prompt_text, response.response_text)
        
        # Store evaluations
        for metric, score in result["scores"].items():
            evaluation = Evaluation(
                response_id=response_id,
                metric=metric,
                score=score,
                evaluation_method="rule"
            )
            db.add(evaluation)
        
        db.commit()
        return result
    
    elif method == "llm":
        judge = LLMJudge()
        result = judge.evaluate(prompt.prompt_text, response.response_text)
        
        if result["success"]:
            # Store evaluations
            for metric, score in result["scores"].items():
                if isinstance(score, (int, float)):
                    evaluation = Evaluation(
                        response_id=response_id,
                        metric=metric,
                        score=float(score),
                        evaluation_method="llm",
                        details=result["scores"].get("explanation", "")
                    )
                    db.add(evaluation)
            
            db.commit()
        
        return result
    
    else:
        raise HTTPException(status_code=400, detail="Invalid evaluation method")


@router.get("/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(
    dataset: Optional[str] = Query(None, description="Filter by dataset name"),
    metric: Optional[str] = Query(None, description="Sort by specific metric"),
    limit: int = Query(50, ge=1, le=100, description="Number of entries to return"),
    db: Session = Depends(get_db)
):
    """
    Get model leaderboard with average scores.
    
    Supports filtering by dataset and sorting by specific metrics.
    """
    logger.info("leaderboard_requested", dataset=dataset, metric=metric, limit=limit)
    
    service = LeaderboardService(db)
    return service.get_leaderboard(
        dataset_filter=dataset,
        metric_filter=metric,
        limit=limit
    )


@router.get("/metrics/{model_name}", response_model=ModelMetricsDetail)
def get_model_metrics(
    model_name: str,
    dataset: Optional[str] = Query(None, description="Filter by dataset"),
    db: Session = Depends(get_db)
):
    """Get detailed metrics for a specific model."""
    logger.info("model_metrics_requested", model_name=model_name, dataset=dataset)
    
    service = LeaderboardService(db)
    metrics = service.get_model_details(model_name, dataset_filter=dataset)
    
    if not metrics:
        raise HTTPException(status_code=404, detail="Model not found or no evaluations")
    
    return metrics


@router.get("/experiment/{experiment_id}/summary")
def get_experiment_summary(experiment_id: int, db: Session = Depends(get_db)):
    """Get summary statistics for an experiment."""
    return MetricsService.get_experiment_summary(db, experiment_id)
