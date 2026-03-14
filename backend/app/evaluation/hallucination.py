import re


def check_hallucination(prompt: str, response: str) -> float:
    """
    Rule-based hallucination detection.
    Returns a score from 0 to 10 (higher = less hallucination).
    
    This is a simplified heuristic approach.
    """
    score = 10.0
    
    # Check for overly confident false statements
    confidence_patterns = [
        r"definitely",
        r"absolutely",
        r"certainly",
        r"without a doubt",
        r"100% sure"
    ]
    
    response_lower = response.lower()
    
    # Penalize excessive confidence (which might indicate hallucination)
    confidence_count = sum(1 for pattern in confidence_patterns if re.search(pattern, response_lower))
    if confidence_count > 2:
        score -= 2.0
    
    # Check for made-up numbers or dates without context
    if re.search(r'\b\d{4}\b', response) and "year" not in response_lower:
        score -= 1.0
    
    # Check for contradictions within response
    if "however" in response_lower or "but" in response_lower:
        sentences = response.split(".")
        if len(sentences) > 2:
            score -= 0.5
    
    return max(0.0, min(10.0, score))
