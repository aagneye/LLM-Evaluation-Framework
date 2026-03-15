from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class MetricCategory(str, Enum):
    """Categories for evaluation metrics."""
    CORRECTNESS = "correctness"
    HALLUCINATION = "hallucination"
    REASONING = "reasoning"
    SAFETY = "safety"
    COHERENCE = "coherence"
    RELEVANCE = "relevance"
    CUSTOM = "custom"


@dataclass
class MetricResult:
    """Standardized metric evaluation result."""
    metric_name: str
    score: float  # 0-10 scale
    category: MetricCategory
    details: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None
    passed: bool = True


class BaseMetric(ABC):
    """Abstract base class for all evaluation metrics."""
    
    def __init__(
        self,
        name: str,
        category: MetricCategory,
        description: str = "",
        version: str = "1.0.0"
    ):
        self.name = name
        self.category = category
        self.description = description
        self.version = version
        self.logger = structlog.get_logger(f"{__name__}.{name}")
    
    @abstractmethod
    def evaluate(self, prompt: str, response: str, **kwargs) -> MetricResult:
        """
        Evaluate a prompt-response pair.
        
        Args:
            prompt: The input prompt
            response: The model's response
            **kwargs: Additional metric-specific parameters
            
        Returns:
            MetricResult with score and details
        """
        pass
    
    def validate_inputs(self, prompt: str, response: str) -> bool:
        """Validate inputs before evaluation."""
        if not prompt or not isinstance(prompt, str):
            self.logger.warning("invalid_prompt", prompt_type=type(prompt))
            return False
        
        if not response or not isinstance(response, str):
            self.logger.warning("invalid_response", response_type=type(response))
            return False
        
        return True
    
    def normalize_score(self, score: float, min_val: float = 0.0, max_val: float = 10.0) -> float:
        """Normalize score to 0-10 range."""
        return max(min_val, min(max_val, score))
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metric metadata."""
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "version": self.version,
        }
