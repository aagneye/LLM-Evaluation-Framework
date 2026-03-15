import re
from typing import Dict, Any
import structlog

from app.evaluation.metrics.base import BaseMetric, MetricResult, MetricCategory

logger = structlog.get_logger(__name__)


class HallucinationMetric(BaseMetric):
    """Detect potential hallucinations in model responses."""
    
    def __init__(self):
        super().__init__(
            name="hallucination",
            category=MetricCategory.HALLUCINATION,
            description="Detects potential hallucinations and false claims",
            version="1.0.0"
        )
        
        self.warning_patterns = [
            (r"according to (my|the) (knowledge|data)", 2.0, "unverified_claim"),
            (r"studies show", 2.5, "unverified_study"),
            (r"research indicates", 2.5, "unverified_research"),
            (r"it is proven", 3.0, "unverified_proof"),
            (r"definitely|certainly|absolutely", 1.5, "overconfidence"),
            (r"\d{4} (study|research|paper)", 2.0, "specific_citation_without_source"),
        ]
    
    def evaluate(self, prompt: str, response: str, **kwargs) -> MetricResult:
        """
        Evaluate potential hallucinations in response.
        
        Args:
            prompt: Input prompt
            response: Model response
            **kwargs: Additional parameters
            
        Returns:
            MetricResult with hallucination score (higher is better)
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
            "warnings": [],
            "checks": {}
        }
        
        response_lower = response.lower()
        
        for pattern, penalty, reason in self.warning_patterns:
            matches = re.findall(pattern, response_lower)
            if matches:
                score -= penalty
                details["warnings"].append({
                    "reason": reason,
                    "penalty": penalty,
                    "pattern": pattern,
                    "occurrences": len(matches)
                })
        
        has_hedging = any(
            word in response_lower
            for word in ["might", "may", "could", "possibly", "perhaps", "likely"]
        )
        details["checks"]["has_hedging"] = has_hedging
        
        if has_hedging:
            score += 1.0
        
        has_sources = bool(re.search(r"(source:|reference:|citation:)", response_lower))
        details["checks"]["has_sources"] = has_sources
        
        if has_sources:
            score += 1.0
        
        final_score = self.normalize_score(score)
        
        explanation = self._generate_explanation(final_score, details)
        
        self.logger.info(
            "hallucination_evaluated",
            score=final_score,
            warnings=len(details["warnings"])
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
            return "Very low hallucination risk with appropriate hedging"
        elif score >= 7.0:
            return f"Low hallucination risk with {len(details['warnings'])} minor warnings"
        elif score >= 5.0:
            return f"Moderate hallucination risk with {len(details['warnings'])} warnings"
        else:
            return f"High hallucination risk with {len(details['warnings'])} significant warnings"
