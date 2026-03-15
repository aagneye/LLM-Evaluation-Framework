import re
from typing import Any
import structlog

logger = structlog.get_logger(__name__)


class InputValidator:
    """Security-focused input validation."""
    
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\bOR\b.*=.*)",
        r"(\bUNION\b.*\bSELECT\b)",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
    ]
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 10000) -> str:
        """
        Sanitize string input.
        
        Args:
            value: Input string
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            raise ValueError("Input must be a string")
        
        if len(value) > max_length:
            raise ValueError(f"Input exceeds maximum length of {max_length}")
        
        value = value.strip()
        
        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning("potential_sql_injection_detected", pattern=pattern)
                raise ValueError("Invalid input detected")
        
        for pattern in InputValidator.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning("potential_xss_detected", pattern=pattern)
                raise ValueError("Invalid input detected")
        
        return value
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_model_name(model_name: str) -> bool:
        """Validate model name format."""
        pattern = r'^[a-zA-Z0-9._-]+$'
        return bool(re.match(pattern, model_name)) and len(model_name) <= 100
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key format."""
        return len(api_key) >= 20 and len(api_key) <= 200
