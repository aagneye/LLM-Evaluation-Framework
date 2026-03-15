import re
from typing import Dict, Any
import structlog

from app.evaluation.metrics.base import BaseMetric, MetricResult, MetricCategory

logger = structlog.get_logger(__name__)


class CorrectnessMetric(BaseMetric):
    """Evaluate response correctness using rule-based heuristics."""
    
    def __init__(self):
        super().__init__(
            name="correctness",
            category=MetricCategory.CORRECTNESS,
            description="Evaluates response correctness using error detection and completeness checks",
            version="1.0.0"
        )
        
        self.error_patterns = [
            (r"i don't know", 3.0, "uncertainty_expression"),
            (r"i'm not sure", 2.5, "uncertainty_expression"),
            (r"i cannot", 2.0, "inability_statement"),
            (r"i can't answer", 3.0, "inability_statement"),
            (r"no information", 2.5, "lack_of_info"),
            (r"error:", 4.0, "explicit_error"),
            (r"invalid", 2.0, "invalid_response"),
        ]
    
    def evaluate(self, prompt: str, response: str, **kwargs) -> MetricResult:
        """
        Evaluate correctness of the response.
        
        Args:
            prompt: Input prompt
            response: Model response
            **kwargs: Additional parameters
            
        Returns:
            MetricResult with correctness score
        """
        if not self.validate_inputs(prompt, response):
            return MetricResult(
                metric_name=self.name,
                score=0.0,
                category=self.category,
                passed=False,
                explanation="Invalid inputs"
            )
        
        score = 10.0
        details: Dict[str, Any] = {
            "deductions": [],
            "checks": {}
        }
        
        response_lower = response.lower()
        
        for pattern, penalty, reason in self.error_patterns:
            if re.search(pattern, response_lower):
                score -= penalty
                details["deductions"].append({
                    "reason": reason,
                    "penalty": penalty,
                    "pattern": pattern
                })
        
        word_count = len(response.split())
        details["checks"]["word_count"] = word_count
        
        if word_count < 10:
            penalty = 2.0
            score -= penalty
            details["deductions"].append({
                "reason": "response_too_short",
                "penalty": penalty,
                "word_count": word_count
            })
        
        prompt_keywords = set(re.findall(r'\w+', prompt.lower()))
        response_keywords = set(re.findall(r'\w+', response_lower))
        overlap = len(prompt_keywords & response_keywords)
        
        details["checks"]["keyword_overlap"] = overlap
        details["checks"]["prompt_keywords"] = len(prompt_keywords)
        
        if overlap < 2:
            penalty = 2.0
            score -= penalty
            details["deductions"].append({
                "reason": "low_relevance",
                "penalty": penalty,
                "overlap": overlap
            })
        
        final_score = self.normalize_score(score)
        
        explanation = self._generate_explanation(final_score, details)
        
        self.logger.info(
            "correctness_evaluated",
            score=final_score,
            deductions=len(details["deductions"])
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
            return "Excellent correctness with no major issues detected"
        elif score >= 7.0:
            return f"Good correctness with minor issues: {len(details['deductions'])} deductions"
        elif score >= 5.0:
            return f"Moderate correctness with some concerns: {len(details['deductions'])} deductions"
        else:
            return f"Poor correctness with significant issues: {len(details['deductions'])} deductions"
