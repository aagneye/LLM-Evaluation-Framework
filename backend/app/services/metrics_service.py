from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Evaluation, ModelResponse, Experiment


class MetricsService:
    """
    Service for aggregating and computing metrics across experiments.
    """
    
    @staticmethod
    def get_leaderboard(db: Session) -> List[Dict[str, Any]]:
        """
        Get model leaderboard with average scores.
        """
        results = db.query(
            ModelResponse.model_name,
            func.avg(Evaluation.score).label("avg_score"),
            func.count(ModelResponse.id).label("response_count")
        ).join(
            Evaluation, ModelResponse.id == Evaluation.response_id
        ).group_by(
            ModelResponse.model_name
        ).order_by(
            func.avg(Evaluation.score).desc()
        ).all()
        
        return [
            {
                "model_name": r.model_name,
                "avg_score": float(r.avg_score) if r.avg_score else 0.0,
                "response_count": r.response_count
            }
            for r in results
        ]
    
    @staticmethod
    def get_model_metrics(db: Session, model_name: str) -> Dict[str, Any]:
        """
        Get detailed metrics for a specific model.
        """
        metrics = db.query(
            Evaluation.metric,
            func.avg(Evaluation.score).label("avg_score"),
            func.count(Evaluation.id).label("count")
        ).join(
            ModelResponse, Evaluation.response_id == ModelResponse.id
        ).filter(
            ModelResponse.model_name == model_name
        ).group_by(
            Evaluation.metric
        ).all()
        
        return {
            "model_name": model_name,
            "metrics": [
                {
                    "metric": m.metric,
                    "avg_score": float(m.avg_score) if m.avg_score else 0.0,
                    "count": m.count
                }
                for m in metrics
            ]
        }
    
    @staticmethod
    def get_experiment_summary(db: Session, experiment_id: int) -> Dict[str, Any]:
        """
        Get summary statistics for an experiment.
        """
        experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
        
        if not experiment:
            return {"error": "Experiment not found"}
        
        responses = db.query(ModelResponse).filter(
            ModelResponse.model_name == experiment.model_name
        ).all()
        
        response_ids = [r.id for r in responses]
        
        evaluations = db.query(
            Evaluation.metric,
            func.avg(Evaluation.score).label("avg_score")
        ).filter(
            Evaluation.response_id.in_(response_ids)
        ).group_by(
            Evaluation.metric
        ).all()
        
        return {
            "experiment_id": experiment.id,
            "experiment_name": experiment.experiment_name,
            "model_name": experiment.model_name,
            "dataset_name": experiment.dataset_name,
            "status": experiment.status,
            "total_responses": len(responses),
            "metrics": [
                {
                    "metric": e.metric,
                    "avg_score": float(e.avg_score) if e.avg_score else 0.0
                }
                for e in evaluations
            ]
        }
