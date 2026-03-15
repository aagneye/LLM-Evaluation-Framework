import time
from typing import Dict, Any
import structlog

from app.services.models.base import BaseModelProvider, ModelResponse
from app.config import get_settings
from app.core.exceptions import ModelProviderError

logger = structlog.get_logger(__name__)
settings = get_settings()


class LocalLlamaProvider(BaseModelProvider):
    """Local Llama model provider (Ollama/vLLM integration)."""
    
    AVAILABLE_MODELS = [
        "llama-3.1-8b",
        "llama-3.1-70b",
        "llama-3.2-3b",
        "mistral-7b",
        "mixtral-8x7b",
    ]
    
    def __init__(self):
        super().__init__("local_llama")
        self.base_url = getattr(settings, 'ollama_base_url', 'http://localhost:11434')
        self.client = None
        
        try:
            import httpx
            self.client = httpx.Client(base_url=self.base_url, timeout=60.0)
        except ImportError:
            logger.warning("httpx_not_available")
    
    def is_available(self) -> bool:
        """Check if local Llama server is available."""
        if not self.client:
            return False
        
        try:
            response = self.client.get("/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.debug("local_llama_not_available", error=str(e))
            return False
    
    def list_models(self) -> list[str]:
        """List available local models."""
        if not self.is_available():
            return []
        
        try:
            response = self.client.get("/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.error("failed_to_list_models", error=str(e))
        
        return self.AVAILABLE_MODELS.copy()
    
    def generate(
        self,
        prompt: str,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> ModelResponse:
        """
        Generate response using local Llama model.
        
        Args:
            prompt: Input prompt
            model_name: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters
            
        Returns:
            ModelResponse with generated text
        """
        if not self.is_available():
            raise ModelProviderError("LocalLlama", "Ollama server not available")
        
        start_time = time.time()
        
        try:
            logger.info(
                "local_llama_request_started",
                model=model_name,
                prompt_length=len(prompt),
            )
            
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }
            
            response = self.client.post("/api/generate", json=payload)
            response.raise_for_status()
            
            latency = time.time() - start_time
            
            data = response.json()
            text = data.get("response", "")
            
            logger.info(
                "local_llama_request_completed",
                model=model_name,
                latency=latency,
            )
            
            return ModelResponse(
                text=text,
                latency=latency,
                success=True,
                model_name=model_name,
                provider=self.provider_name,
                metadata={
                    "total_duration": data.get("total_duration"),
                    "load_duration": data.get("load_duration"),
                }
            )
            
        except Exception as e:
            latency = time.time() - start_time
            error_msg = str(e)
            
            logger.error(
                "local_llama_request_failed",
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
