from typing import Dict, List, Any
from app.evaluation.correctness import check_correctness
from app.evaluation.hallucination import check_hallucination
from app.evaluation.reasoning import check_reasoning
from app.evaluation.safety import check_safety


class EvaluationEngine:
    """
    Orchestrates rule-based evaluation across multiple metrics.
    """
    
    def __init__(self):
        self.metrics = {
            "correctness": check_correctness,
            "hallucination": check_hallucination,
            "reasoning": check_reasoning,
            "safety": check_safety
        }
    
    def evaluate(self, prompt: str, response: str, metrics: List[str] = None) -> Dict[str, Any]:
        """
        Run rule-based evaluation on a response.
        
        Args:
            prompt: The original prompt
            response: The model's response
            metrics: List of metrics to evaluate (if None, evaluates all)
        
        Returns:
            Dictionary with scores for each metric
        """
        if metrics is None:
            metrics = list(self.metrics.keys())
        
        results = {}
        
        for metric in metrics:
            if metric in self.metrics:
                evaluator = self.metrics[metric]
                score = evaluator(prompt, response)
                results[metric] = score
        
        return {
            "success": True,
            "scores": results
        }
