import hashlib
import json
from typing import Optional, Any
from redis import Redis
import structlog

from app.config import get_settings
from app.core.exceptions import CacheError

logger = structlog.get_logger(__name__)
settings = get_settings()


class CacheManager:
    """Redis-based cache manager for model responses and other data."""
    
    def __init__(self, redis_client: Optional[Redis] = None):
        self.redis = redis_client or Redis.from_url(
            settings.redis_url,
            decode_responses=True
        )
        self.default_ttl = 3600 * 24 * 7  # 7 days
    
    def _generate_cache_key(self, prefix: str, *args: Any) -> str:
        """
        Generate a cache key from prefix and arguments.
        
        Args:
            prefix: Key prefix (e.g., 'model_response', 'evaluation')
            *args: Arguments to include in key
            
        Returns:
            Cache key string
        """
        key_parts = [str(arg) for arg in args]
        key_string = ":".join(key_parts)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            value = self.redis.get(key)
            if value:
                logger.debug("cache_hit", key=key)
                return json.loads(value)
            logger.debug("cache_miss", key=key)
            return None
        except Exception as e:
            logger.error("cache_get_failed", key=key, error=str(e))
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 7 days)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            self.redis.setex(key, ttl, serialized)
            logger.debug("cache_set", key=key, ttl=ttl)
            return True
        except Exception as e:
            logger.error("cache_set_failed", key=key, error=str(e))
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            result = self.redis.delete(key)
            logger.debug("cache_delete", key=key, deleted=bool(result))
            return bool(result)
        except Exception as e:
            logger.error("cache_delete_failed", key=key, error=str(e))
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching a pattern.
        
        Args:
            pattern: Key pattern (e.g., 'model_response:*')
            
        Returns:
            Number of keys deleted
        """
        try:
            keys = self.redis.keys(pattern)
            if keys:
                deleted = self.redis.delete(*keys)
                logger.info("cache_pattern_cleared", pattern=pattern, count=deleted)
                return deleted
            return 0
        except Exception as e:
            logger.error("cache_clear_pattern_failed", pattern=pattern, error=str(e))
            return 0
    
    def get_model_response(
        self,
        model_name: str,
        prompt: str,
        temperature: float = 0.7
    ) -> Optional[dict]:
        """
        Get cached model response.
        
        Args:
            model_name: Name of the model
            prompt: Input prompt
            temperature: Temperature parameter
            
        Returns:
            Cached response dict or None
        """
        key = self._generate_cache_key(
            "model_response",
            model_name,
            prompt,
            temperature
        )
        return self.get(key)
    
    def set_model_response(
        self,
        model_name: str,
        prompt: str,
        response: dict,
        temperature: float = 0.7,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache a model response.
        
        Args:
            model_name: Name of the model
            prompt: Input prompt
            response: Response dict to cache
            temperature: Temperature parameter
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        key = self._generate_cache_key(
            "model_response",
            model_name,
            prompt,
            temperature
        )
        
        logger.info(
            "caching_model_response",
            model=model_name,
            prompt_length=len(prompt),
            key=key
        )
        
        return self.set(key, response, ttl)
    
    def get_evaluation_result(
        self,
        metric_name: str,
        prompt: str,
        response: str
    ) -> Optional[dict]:
        """
        Get cached evaluation result.
        
        Args:
            metric_name: Name of the metric
            prompt: Input prompt
            response: Model response
            
        Returns:
            Cached evaluation result or None
        """
        key = self._generate_cache_key(
            "evaluation",
            metric_name,
            prompt,
            response
        )
        return self.get(key)
    
    def set_evaluation_result(
        self,
        metric_name: str,
        prompt: str,
        response: str,
        result: dict,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache an evaluation result.
        
        Args:
            metric_name: Name of the metric
            prompt: Input prompt
            response: Model response
            result: Evaluation result to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        key = self._generate_cache_key(
            "evaluation",
            metric_name,
            prompt,
            response
        )
        return self.set(key, result, ttl)
    
    def health_check(self) -> bool:
        """
        Check if Redis is healthy.
        
        Returns:
            True if Redis is accessible
        """
        try:
            self.redis.ping()
            return True
        except Exception as e:
            logger.error("redis_health_check_failed", error=str(e))
            return False


def get_cache_manager() -> CacheManager:
    """Get cache manager instance."""
    return CacheManager()
