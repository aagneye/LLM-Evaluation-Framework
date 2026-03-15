from fastapi import Request, Depends
from app.core.rate_limiter import get_rate_limiter, RateLimiter
from app.core.exceptions import RateLimitError
from app.core.security import get_current_user
from app.models.user import User
import structlog

logger = structlog.get_logger(__name__)


async def rate_limit_dependency(
    request: Request,
    current_user: User = Depends(get_current_user),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
):
    """
    Rate limiting dependency for API endpoints.
    
    Limits: 100 requests per minute per user
    """
    user_key = f"user:{current_user.id}"
    
    is_allowed, info = rate_limiter.check_rate_limit(
        key=user_key,
        max_requests=100,
        window_seconds=60,
    )
    
    request.state.rate_limit_info = info
    
    if not is_allowed:
        raise RateLimitError(
            f"Rate limit exceeded. Try again in {info['retry_after']} seconds."
        )
    
    logger.debug(
        "rate_limit_checked",
        user_id=current_user.id,
        remaining=info["remaining"],
        limit=info["limit"],
    )


async def add_rate_limit_headers(request: Request, call_next):
    """Middleware to add rate limit headers to responses."""
    response = await call_next(request)
    
    if hasattr(request.state, "rate_limit_info"):
        info = request.state.rate_limit_info
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])
        
        if info["retry_after"] > 0:
            response.headers["Retry-After"] = str(info["retry_after"])
    
    return response
