from typing import Dict, List, Optional
import structlog

from app.evaluation.metrics.base import BaseMetric, MetricResult, MetricCategory
from app.evaluation.metrics.correctness_metric import CorrectnessMetric
from app.evaluation.metrics.hallucination_metric import HallucinationMetric
from app.evaluation.metrics.reasoning_metric import ReasoningMetric
from app.evaluation.metrics.safety_metric import SafetyMetric

logger = structlog.get_logger(__name__)


class MetricRegistry:
    """Central registry for all evaluation metrics with plugin support."""
    
    _instance = None
    _metrics: Dict[str, BaseMetric] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_default_metrics()
        return cls._instance
    
    def _initialize_default_metrics(self):
        """Initialize default metrics."""
        default_metrics = [
            CorrectnessMetric(),
            HallucinationMetric(),
            ReasoningMetric(),
            SafetyMetric(),
        ]
        
        for metric in default_metrics:
            self.register_metric(metric)
        
        logger.info(
            "metric_registry_initialized",
            metrics=list(self._metrics.keys())
        )
    
    def register_metric(self, metric: BaseMetric) -> None:
        """
        Register a new metric.
        
        Args:
            metric: Metric instance to register
        """
        if metric.name in self._metrics:
            logger.warning(
                "metric_already_registered",
                metric_name=metric.name,
                action="overwriting"
            )
        
        self._metrics[metric.name] = metric
        logger.info("metric_registered", metric_name=metric.name)
    
    def unregister_metric(self, metric_name: str) -> bool:
        """
        Unregister a metric.
        
        Args:
            metric_name: Name of metric to unregister
            
        Returns:
            True if metric was unregistered, False if not found
        """
        if metric_name in self._metrics:
            del self._metrics[metric_name]
            logger.info("metric_unregistered", metric_name=metric_name)
            return True
        return False
    
    def get_metric(self, metric_name: str) -> Optional[BaseMetric]:
        """Get a metric by name."""
        return self._metrics.get(metric_name)
    
    def list_metrics(self) -> List[str]:
        """List all registered metric names."""
        return list(self._metrics.keys())
    
    def list_metrics_by_category(self, category: MetricCategory) -> List[str]:
        """List metrics filtered by category."""
        return [
            name for name, metric in self._metrics.items()
            if metric.category == category
        ]
    
    def get_all_metadata(self) -> List[Dict]:
        """Get metadata for all metrics."""
        return [metric.get_metadata() for metric in self._metrics.values()]
    
    def evaluate(
        self,
        metric_name: str,
        prompt: str,
        response: str,
        **kwargs
    ) -> Optional[MetricResult]:
        """
        Evaluate using a specific metric.
        
        Args:
            metric_name: Name of the metric to use
            prompt: Input prompt
            response: Model response
            **kwargs: Additional metric-specific parameters
            
        Returns:
            MetricResult or None if metric not found
        """
        metric = self.get_metric(metric_name)
        
        if not metric:
            logger.error("metric_not_found", metric_name=metric_name)
            return None
        
        try:
            result = metric.evaluate(prompt, response, **kwargs)
            logger.debug(
                "metric_evaluated",
                metric_name=metric_name,
                score=result.score
            )
            return result
        except Exception as e:
            logger.error(
                "metric_evaluation_failed",
                metric_name=metric_name,
                error=str(e),
                exc_info=True
            )
            return None
    
    def evaluate_all(
        self,
        prompt: str,
        response: str,
        **kwargs
    ) -> Dict[str, MetricResult]:
        """
        Evaluate using all registered metrics.
        
        Args:
            prompt: Input prompt
            response: Model response
            **kwargs: Additional parameters
            
        Returns:
            Dictionary mapping metric names to results
        """
        results = {}
        
        for metric_name in self.list_metrics():
            result = self.evaluate(metric_name, prompt, response, **kwargs)
            if result:
                results[metric_name] = result
        
        logger.info(
            "all_metrics_evaluated",
            metrics_count=len(results),
            prompt_length=len(prompt)
        )
        
        return results


def get_metric_registry() -> MetricRegistry:
    """Get the singleton metric registry instance."""
    return MetricRegistry()
