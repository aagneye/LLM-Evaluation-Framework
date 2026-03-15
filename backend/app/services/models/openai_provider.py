import time
from typing import Dict, Any
from openai import OpenAI, OpenAIError
import structlog

from app.services.models.base import BaseModelProvider, ModelResponse
from app.config import get_settings
from app.core.retry import retry_with_backoff
from app.core.exceptions import ModelProviderError

logger = structlog.get_logger(__name__)
settings = get_settings()


class OpenAIProvider(BaseModelProvider):
    """OpenAI API provider implementation."""
    
    AVAILABLE_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ]
    
    def __init__(self):
        super().__init__("openai")
        self.client = None
        if settings.openai_api_key:
            self.client = OpenAI(api_key=settings.openai_api_key)
    
    def is_available(self) -> bool:
        """Check if OpenAI is configured."""
        return self.client is not None and bool(settings.openai_api_key)
    
    def list_models(self) -> list[str]:
        """List available OpenAI models."""
        return self.AVAILABLE_MODELS.copy()
    
    @retry_with_backoff(max_retries=3, initial_delay=1.0, exceptions=(OpenAIError,))
    def generate(
        self,
        prompt: str,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> ModelResponse:
        """
        Generate response using OpenAI API.
        
        Args:
            prompt: Input prompt
            model_name: OpenAI model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional OpenAI parameters
            
        Returns:
            ModelResponse with generated text
        """
        if not self.is_available():
            raise ModelProviderError("OpenAI", "API key not configured")
        
        if not self.validate_model(model_name):
            raise ModelProviderError("OpenAI", f"Model {model_name} not available")
        
        start_time = time.time()
        
        try:
            logger.info(
                "openai_request_started",
                model=model_name,
                prompt_length=len(prompt),
            )
            
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            latency = time.time() - start_time
            
            text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            logger.info(
                "openai_request_completed",
                model=model_name,
                latency=latency,
                tokens_used=tokens_used,
            )
            
            return ModelResponse(
                text=text,
                latency=latency,
                success=True,
                model_name=model_name,
                provider=self.provider_name,
                tokens_used=tokens_used,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "model": response.model,
                }
            )
            
        except OpenAIError as e:
            latency = time.time() - start_time
            error_msg = str(e)
            
            logger.error(
                "openai_request_failed",
                model=model_name,
                latency=latency,
                error=error_msg,
            )
            
            return ModelResponse(
                text="",
                latency=latency,
                success=False,
                model_name=model_name,
                provider=self.provider_name,
                error=error_msg,
            )
