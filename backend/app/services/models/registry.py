from typing import Dict, Optional
import structlog

from app.services.models.base import BaseModelProvider, ModelResponse
from app.services.models.openai_provider import OpenAIProvider
from app.services.models.anthropic_provider import AnthropicProvider
from app.services.models.local_llama_provider import LocalLlamaProvider
from app.core.exceptions import ModelProviderError

logger = structlog.get_logger(__name__)


class ModelRegistry:
    """Central registry for all model providers."""
    
    _instance = None
    _providers: Dict[str, BaseModelProvider] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_providers()
        return cls._instance
    
    def _initialize_providers(self):
        """Initialize all available providers."""
        self._providers = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "local_llama": LocalLlamaProvider(),
        }
        
        logger.info("model_registry_initialized", providers=list(self._providers.keys()))
    
    def get_provider(self, provider_name: str) -> Optional[BaseModelProvider]:
        """Get a provider by name."""
        return self._providers.get(provider_name)
    
    def list_providers(self) -> list[str]:
        """List all registered providers."""
        return list(self._providers.keys())
    
    def list_available_providers(self) -> list[str]:
        """List only available (configured) providers."""
        return [
            name for name, provider in self._providers.items()
            if provider.is_available()
        ]
    
    def list_all_models(self) -> Dict[str, list[str]]:
        """List all models from all providers."""
        return {
            name: provider.list_models()
            for name, provider in self._providers.items()
        }
    
    def generate(
        self,
        provider_name: str,
        prompt: str,
        model_name: str,
        **kwargs
    ) -> ModelResponse:
        """
        Generate response using specified provider and model.
        
        Args:
            provider_name: Name of the provider
            prompt: Input prompt
            model_name: Model name
            **kwargs: Additional parameters
            
        Returns:
            ModelResponse object
            
        Raises:
            ModelProviderError: If provider not found or unavailable
        """
        provider = self.get_provider(provider_name)
        
        if not provider:
            raise ModelProviderError(
                provider_name,
                f"Provider '{provider_name}' not found"
            )
        
        if not provider.is_available():
            raise ModelProviderError(
                provider_name,
                f"Provider '{provider_name}' is not available or not configured"
            )
        
        return provider.generate(prompt, model_name, **kwargs)
    
    def auto_detect_provider(self, model_name: str) -> Optional[str]:
        """
        Auto-detect provider based on model name.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Provider name or None if not found
        """
        if model_name.startswith("gpt"):
            return "openai"
        elif model_name.startswith("claude"):
            return "anthropic"
        elif any(x in model_name.lower() for x in ["llama", "mistral", "mixtral"]):
            return "local_llama"
        
        for provider_name, provider in self._providers.items():
            if provider.is_available() and model_name in provider.list_models():
                return provider_name
        
        return None


def get_model_registry() -> ModelRegistry:
    """Get the singleton model registry instance."""
    return ModelRegistry()
