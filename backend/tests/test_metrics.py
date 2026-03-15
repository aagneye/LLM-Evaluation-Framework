import pytest
from app.evaluation.metrics.correctness_metric import CorrectnessMetric
from app.evaluation.metrics.hallucination_metric import HallucinationMetric
from app.evaluation.metrics.reasoning_metric import ReasoningMetric
from app.evaluation.metrics.safety_metric import SafetyMetric
from app.evaluation.metrics.registry import MetricRegistry


def test_correctness_metric():
    """Test correctness metric evaluation."""
    metric = CorrectnessMetric()
    
    prompt = "What is 2+2?"
    response = "The answer is 4. This is a simple arithmetic calculation."
    
    result = metric.evaluate(prompt, response)
    
    assert result.score > 0
    assert result.score <= 10
    assert result.metric_name == "correctness"
    assert result.passed is True


def test_hallucination_metric():
    """Test hallucination detection."""
    metric = HallucinationMetric()
    
    prompt = "Tell me about AI"
    response = "According to my knowledge, AI is definitely the best technology."
    
    result = metric.evaluate(prompt, response)
    
    assert result.score >= 0
    assert result.score <= 10
    assert result.metric_name == "hallucination"


def test_reasoning_metric():
    """Test reasoning quality evaluation."""
    metric = ReasoningMetric()
    
    prompt = "Explain why the sky is blue"
    response = "First, light from the sun enters the atmosphere. Therefore, shorter wavelengths scatter more. This means blue light scatters the most."
    
    result = metric.evaluate(prompt, response)
    
    assert result.score > 5
    assert result.details["checks"]["reasoning_indicators"] > 0


def test_safety_metric():
    """Test safety evaluation."""
    metric = SafetyMetric()
    
    prompt = "How to stay healthy?"
    response = "Exercise regularly, eat balanced meals, and consult a healthcare professional for personalized advice."
    
    result = metric.evaluate(prompt, response)
    
    assert result.score >= 7
    assert len(result.details["violations"]) == 0


def test_metric_registry():
    """Test metric registry functionality."""
    registry = MetricRegistry()
    
    metrics = registry.list_metrics()
    assert "correctness" in metrics
    assert "hallucination" in metrics
    assert "reasoning" in metrics
    assert "safety" in metrics
    
    metric = registry.get_metric("correctness")
    assert metric is not None
    assert metric.name == "correctness"


def test_evaluate_all_metrics():
    """Test evaluating with all metrics."""
    registry = MetricRegistry()
    
    prompt = "What is Python?"
    response = "Python is a high-level programming language known for its simplicity and readability."
    
    results = registry.evaluate_all(prompt, response)
    
    assert len(results) >= 4
    assert all(result.score >= 0 and result.score <= 10 for result in results.values())
