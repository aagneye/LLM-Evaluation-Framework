from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import structlog

logger = structlog.get_logger(__name__)

http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

model_requests_total = Counter(
    'model_requests_total',
    'Total model API requests',
    ['model_name', 'provider', 'status']
)

model_request_duration_seconds = Histogram(
    'model_request_duration_seconds',
    'Model API request duration in seconds',
    ['model_name', 'provider']
)

evaluation_requests_total = Counter(
    'evaluation_requests_total',
    'Total evaluation requests',
    ['metric_name', 'status']
)

evaluation_duration_seconds = Histogram(
    'evaluation_duration_seconds',
    'Evaluation duration in seconds',
    ['metric_name']
)

cache_operations_total = Counter(
    'cache_operations_total',
    'Total cache operations',
    ['operation', 'status']
)

active_experiments = Gauge(
    'active_experiments',
    'Number of currently running experiments'
)

database_connections = Gauge(
    'database_connections',
    'Number of active database connections'
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics for HTTP requests."""
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            duration = time.time() - start_time
            
            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=500
            ).inc()
            
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            raise


def track_model_request(model_name: str, provider: str, duration: float, success: bool):
    """Track a model API request."""
    status = "success" if success else "error"
    
    model_requests_total.labels(
        model_name=model_name,
        provider=provider,
        status=status
    ).inc()
    
    model_request_duration_seconds.labels(
        model_name=model_name,
        provider=provider
    ).observe(duration)


def track_evaluation(metric_name: str, duration: float, success: bool):
    """Track an evaluation request."""
    status = "success" if success else "error"
    
    evaluation_requests_total.labels(
        metric_name=metric_name,
        status=status
    ).inc()
    
    evaluation_duration_seconds.labels(
        metric_name=metric_name
    ).observe(duration)


def track_cache_operation(operation: str, success: bool):
    """Track a cache operation."""
    status = "success" if success else "error"
    
    cache_operations_total.labels(
        operation=operation,
        status=status
    ).inc()


def get_metrics():
    """Get Prometheus metrics."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
