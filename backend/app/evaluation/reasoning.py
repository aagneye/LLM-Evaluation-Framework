import re


def check_reasoning(prompt: str, response: str) -> float:
    """
    Rule-based reasoning quality check.
    Returns a score from 0 to 10.
    """
    score = 5.0
    
    response_lower = response.lower()
    
    # Check for reasoning indicators
    reasoning_indicators = [
        r"because",
        r"therefore",
        r"thus",
        r"since",
        r"as a result",
        r"consequently",
        r"this means",
        r"which implies",
        r"first.*second.*third",
        r"step \d+"
    ]
    
    reasoning_count = sum(1 for pattern in reasoning_indicators if re.search(pattern, response_lower))
    score += min(3.0, reasoning_count * 0.5)
    
    # Check for structured thinking (lists, steps)
    if re.search(r'\n\s*[\d\-\*]', response):
        score += 1.0
    
    # Check for examples or explanations
    if "for example" in response_lower or "such as" in response_lower:
        score += 1.0
    
    # Penalize very short responses (likely lack reasoning)
    if len(response.split()) < 20:
        score -= 2.0
    
    return max(0.0, min(10.0, score))
