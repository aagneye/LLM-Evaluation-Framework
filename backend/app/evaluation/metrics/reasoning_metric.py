import re
from typing import Dict, Any
import structlog

from app.evaluation.metrics.base import BaseMetric, MetricResult, MetricCategory

logger = structlog.get_logger(__name__)


class ReasoningMetric(BaseMetric):
    """Evaluate logical reasoning and explanation quality."""
    
    def __init__(self):
        super().__init__(
            name="reasoning",
            category=MetricCategory.REASONING,
            description="Evaluates logical reasoning structure and explanation quality",
            version="1.0.0"
        )
        
        self.reasoning_indicators = [
            "because", "therefore", "thus", "hence", "consequently",
            "as a result", "due to", "since", "given that", "this means"
        ]
        
        self.structure_indicators = [
            "first", "second", "third", "finally",
            "step 1", "step 2", "next", "then"
        ]
    
    def evaluate(self, prompt: str, response: str, **kwargs) -> MetricResult:
        """
        Evaluate reasoning quality in response.
        
        Args:
            prompt: Input prompt
            response: Model response
            **kwargs: Additional parameters
            
        Returns:
            MetricResult with reasoning score
        """
        if not self.validate_inputs(prompt, response):
            return MetricResult(
                metric_name=self.name,
                score=0.0,
                category=self.category,
                passed=False,
                explanation="Invalid inputs"
            )
        
        score = 5.0
        details: Dict[str, Any] = {
            "indicators_found": [],
            "checks": {}
        }
        
        response_lower = response.lower()
        
        reasoning_count = sum(
            1 for indicator in self.reasoning_indicators
            if indicator in response_lower
        )
        details["checks"]["reasoning_indicators"] = reasoning_count
        
        if reasoning_count > 0:
            score += min(3.0, reasoning_count * 0.5)
            details["indicators_found"].extend([
                ind for ind in self.reasoning_indicators
                if ind in response_lower
            ])
        
        structure_count = sum(
            1 for indicator in self.structure_indicators
            if indicator in response_lower
        )
        details["checks"]["structure_indicators"] = structure_count
        
        if structure_count >= 2:
            score += 2.0
        elif structure_count == 1:
            score += 1.0
        
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        details["checks"]["sentence_count"] = len(sentences)
        
        if len(sentences) >= 3:
            score += 1.0
        
        has_examples = bool(re.search(r"(for example|such as|like|e\.g\.|instance)", response_lower))
        details["checks"]["has_examples"] = has_examples
        
        if has_examples:
            score += 1.0
        
        final_score = self.normalize_score(score)
        
        explanation = self._generate_explanation(final_score, details)
        
        self.logger.info(
            "reasoning_evaluated",
            score=final_score,
            reasoning_indicators=reasoning_count,
            structure_indicators=structure_count
        )
        
        return MetricResult(
            metric_name=self.name,
            score=final_score,
            category=self.category,
            details=details,
            explanation=explanation,
            passed=final_score >= 6.0
        )
    
    def _generate_explanation(self, score: float, details: Dict[str, Any]) -> str:
        """Generate human-readable explanation."""
        if score >= 9.0:
            return "Excellent reasoning with clear logical structure and explanations"
        elif score >= 7.0:
            return "Good reasoning with adequate logical connections"
        elif score >= 5.0:
            return "Moderate reasoning with some logical structure"
        else:
            return "Poor reasoning with limited logical connections"
