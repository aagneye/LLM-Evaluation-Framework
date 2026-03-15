import time
from typing import Dict, Any
import structlog

from app.services.models.base import BaseModelProvider, ModelResponse
from app.config import get_settings
from app.core.retry import retry_with_backoff
from app.core.exceptions import ModelProviderError

logger = structlog.get_logger(__name__)
settings = get_settings()


class AnthropicProvider(BaseModelProvider):
    """Anthropic Claude API provider implementation."""
    
    AVAILABLE_MODELS = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]
    
    def __init__(self):
        super().__init__("anthropic")
        self.client = None
        self.api_key = getattr(settings, 'anthropic_api_key', None)
        
        if self.api_key:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
            except ImportError:
                logger.warning("anthropic_not_installed")
    
    def is_available(self) -> bool:
        """Check if Anthropic is configured."""
        return self.client is not None and bool(self.api_key)
    
    def list_models(self) -> list[str]:
        """List available Anthropic models."""
        return self.AVAILABLE_MODELS.copy()
    
    @retry_with_backoff(max_retries=3, initial_delay=1.0, exceptions=(Exception,))
    def generate(
        self,
        prompt: str,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> ModelResponse:
        """
        Generate response using Anthropic API.
        
        Args:
            prompt: Input prompt
            model_name: Anthropic model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional Anthropic parameters
            
        Returns:
            ModelResponse with generated text
        """
        if not self.is_available():
            raise ModelProviderError("Anthropic", "API key not configured")
        
        if not self.validate_model(model_name):
            raise ModelProviderError("Anthropic", f"Model {model_name} not available")
        
        start_time = time.time()
        
        try:
            logger.info(
                "anthropic_request_started",
                model=model_name,
                prompt_length=len(prompt),
            )
            
            response = self.client.messages.create(
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            latency = time.time() - start_time
            
            text = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            logger.info(
                "anthropic_request_completed",
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
                    "stop_reason": response.stop_reason,
                    "model": response.model,
                }
            )
            
        except Exception as e:
            latency = time.time() - start_time
            error_msg = str(e)
            
            logger.error(
                "anthropic_request_failed",
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
