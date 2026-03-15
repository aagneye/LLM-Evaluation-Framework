import time
from typing import Optional
from fastapi import Request
from redis import Redis
import structlog

from app.config import get_settings
from app.core.exceptions import RateLimitError

logger = structlog.get_logger(__name__)
settings = get_settings()


class RateLimiter:
    """Redis-based rate limiter using sliding window algorithm."""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> tuple[bool, dict]:
        """
        Check if request is within rate limit.
        
        Args:
            key: Unique identifier for rate limiting (e.g., user_id, ip_address)
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, info_dict)
        """
        current_time = time.time()
        window_start = current_time - window_seconds
        
        rate_limit_key = f"rate_limit:{key}"
        
        try:
            pipe = self.redis.pipeline()
            
            pipe.zremrangebyscore(rate_limit_key, 0, window_start)
            
            pipe.zadd(rate_limit_key, {str(current_time): current_time})
            
            pipe.zcard(rate_limit_key)
            
            pipe.expire(rate_limit_key, window_seconds)
            
            results = pipe.execute()
            request_count = results[2]
            
            remaining = max(0, max_requests - request_count)
            reset_time = int(current_time + window_seconds)
            
            info = {
                "limit": max_requests,
                "remaining": remaining,
                "reset": reset_time,
                "retry_after": window_seconds if request_count >= max_requests else 0,
            }
            
            is_allowed = request_count <= max_requests
            
            if not is_allowed:
                logger.warning(
                    "rate_limit_exceeded",
                    key=key,
                    request_count=request_count,
                    max_requests=max_requests,
                )
            
            return is_allowed, info
            
        except Exception as e:
            logger.error("rate_limit_check_failed", error=str(e), exc_info=True)
            return True, {
                "limit": max_requests,
                "remaining": max_requests,
                "reset": int(current_time + window_seconds),
                "retry_after": 0,
            }
    
    def get_rate_limit_info(self, key: str, window_seconds: int) -> dict:
        """Get current rate limit info for a key."""
        current_time = time.time()
        window_start = current_time - window_seconds
        
        rate_limit_key = f"rate_limit:{key}"
        
        try:
            self.redis.zremrangebyscore(rate_limit_key, 0, window_start)
            request_count = self.redis.zcard(rate_limit_key)
            
            return {
                "current_requests": request_count,
                "window_seconds": window_seconds,
            }
        except Exception as e:
            logger.error("rate_limit_info_failed", error=str(e))
            return {
                "current_requests": 0,
                "window_seconds": window_seconds,
            }


def get_rate_limiter() -> RateLimiter:
    """Get rate limiter instance with Redis connection."""
    redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    return RateLimiter(redis_client)
