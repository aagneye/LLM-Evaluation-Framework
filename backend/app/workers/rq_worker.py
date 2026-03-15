import time
from typing import Dict, Any, List
from redis import Redis
from rq import Queue
import structlog

from app.config import get_settings
from app.services.models.registry import get_model_registry
from app.evaluation.metrics.registry import get_metric_registry
from app.core.cache import get_cache_manager

logger = structlog.get_logger(__name__)
settings = get_settings()


def run_experiment_job(
    experiment_id: int,
    model_name: str,
    provider_name: str,
    prompts: List[Dict[str, Any]],
    temperature: float = 0.7
) -> Dict[str, Any]:
    """
    Execute an experiment job: run prompts through model and evaluate.
    
    This function runs in a worker process.
    
    Args:
        experiment_id: ID of the experiment
        model_name: Name of the model
        provider_name: Model provider name
        prompts: List of prompt dicts with id and text
        temperature: Model temperature
        
    Returns:
        Job result summary
    """
    logger.info(
        "experiment_job_started",
        experiment_id=experiment_id,
        model=model_name,
        prompt_count=len(prompts)
    )
    
    start_time = time.time()
    
    model_registry = get_model_registry()
    metric_registry = get_metric_registry()
    cache_manager = get_cache_manager()
    
    results = {
        "experiment_id": experiment_id,
        "model_name": model_name,
        "responses": [],
        "evaluations": [],
        "errors": []
    }
    
    for prompt_data in prompts:
        prompt_id = prompt_data["id"]
        prompt_text = prompt_data["text"]
        
        try:
            cached_response = cache_manager.get_model_response(
                model_name, prompt_text, temperature
            )
            
            if cached_response:
                logger.info("using_cached_response", prompt_id=prompt_id)
                model_response = cached_response
            else:
                model_response = model_registry.generate(
                    provider_name=provider_name,
                    prompt=prompt_text,
                    model_name=model_name,
                    temperature=temperature
                )
                
                response_dict = {
                    "text": model_response.text,
                    "latency": model_response.latency,
                    "success": model_response.success,
                    "tokens_used": model_response.tokens_used
                }
                
                cache_manager.set_model_response(
                    model_name, prompt_text, response_dict, temperature
                )
                
                model_response = response_dict
            
            results["responses"].append({
                "prompt_id": prompt_id,
                "response_text": model_response["text"],
                "latency": model_response["latency"],
                "success": model_response["success"]
            })
            
            if model_response["success"]:
                eval_results = metric_registry.evaluate_all(
                    prompt_text,
                    model_response["text"]
                )
                
                for metric_name, metric_result in eval_results.items():
                    results["evaluations"].append({
                        "prompt_id": prompt_id,
                        "metric": metric_name,
                        "score": metric_result.score,
                        "passed": metric_result.passed
                    })
            
        except Exception as e:
            logger.error(
                "prompt_execution_failed",
                prompt_id=prompt_id,
                error=str(e),
                exc_info=True
            )
            results["errors"].append({
                "prompt_id": prompt_id,
                "error": str(e)
            })
    
    duration = time.time() - start_time
    
    logger.info(
        "experiment_job_completed",
        experiment_id=experiment_id,
        duration=duration,
        responses=len(results["responses"]),
        evaluations=len(results["evaluations"]),
        errors=len(results["errors"])
    )
    
    return results


class JobQueue:
    """RQ-based job queue for experiment execution."""
    
    def __init__(self):
        self.redis = Redis.from_url(settings.redis_url)
        self.queue = Queue('experiments', connection=self.redis)
        logger.info("job_queue_initialized")
    
    def enqueue_experiment(
        self,
        experiment_id: int,
        model_name: str,
        provider_name: str,
        prompts: List[Dict[str, Any]],
        temperature: float = 0.7
    ) -> str:
        """
        Enqueue an experiment job.
        
        Args:
            experiment_id: ID of the experiment
            model_name: Model name
            provider_name: Provider name
            prompts: List of prompts
            temperature: Model temperature
            
        Returns:
            Job ID
        """
        job = self.queue.enqueue(
            run_experiment_job,
            experiment_id=experiment_id,
            model_name=model_name,
            provider_name=provider_name,
            prompts=prompts,
            temperature=temperature,
            job_timeout='1h'
        )
        
        logger.info(
            "experiment_enqueued",
            experiment_id=experiment_id,
            job_id=job.id
        )
        
        return job.id
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a job."""
        job = self.queue.fetch_job(job_id)
        
        if not job:
            return {"status": "not_found"}
        
        return {
            "status": job.get_status(),
            "result": job.result if job.is_finished else None,
            "error": str(job.exc_info) if job.is_failed else None,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None
        }
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job."""
        job = self.queue.fetch_job(job_id)
        
        if job:
            job.cancel()
            logger.info("job_cancelled", job_id=job_id)
            return True
        
        return False


def get_job_queue() -> JobQueue:
    """Get job queue instance."""
    return JobQueue()
