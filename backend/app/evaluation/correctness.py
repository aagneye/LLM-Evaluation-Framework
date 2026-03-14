import re


def check_correctness(prompt: str, response: str) -> float:
    """
    Rule-based correctness check.
    Returns a score from 0 to 10.
    
    This is a simplified heuristic-based approach.
    In production, you'd use more sophisticated methods.
    """
    score = 10.0
    
    # Check for common error indicators
    error_patterns = [
        r"i don't know",
        r"i'm not sure",
        r"i cannot",
        r"i can't answer",
        r"no information",
        r"error:",
        r"invalid"
    ]
    
    response_lower = response.lower()
    
    for pattern in error_patterns:
        if re.search(pattern, response_lower):
            score -= 3.0
    
    # Check if response is too short (likely incomplete)
    if len(response.split()) < 10:
        score -= 2.0
    
    # Check if response seems to address the prompt
    prompt_keywords = set(re.findall(r'\w+', prompt.lower()))
    response_keywords = set(re.findall(r'\w+', response_lower))
    
    overlap = len(prompt_keywords & response_keywords)
    if overlap < 2:
        score -= 2.0
    
    return max(0.0, min(10.0, score))
