from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ModelResponse:
    """Standardized model response format."""
    text: str
    latency: float
    success: bool
    model_name: str
    provider: str
    tokens_used: Optional[int] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseModelProvider(ABC):
    """Abstract base class for all model providers."""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.logger = structlog.get_logger(f"{__name__}.{provider_name}")
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> ModelResponse:
        """
        Generate a response from the model.
        
        Args:
            prompt: Input prompt text
            model_name: Name of the model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            ModelResponse object with generated text and metadata
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured."""
        pass
    
    @abstractmethod
    def list_models(self) -> list[str]:
        """List available models for this provider."""
        pass
    
    def validate_model(self, model_name: str) -> bool:
        """Validate if a model is available."""
        return model_name in self.list_models()
