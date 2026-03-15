from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.database import init_db
from app.api import prompts, responses, experiments, evaluation, human_feedback, auth, arena, comparison
from app.core.logging import setup_logging, get_logger
from app.core.middleware import CorrelationIdMiddleware, RequestLoggingMiddleware
from app.core.metrics import PrometheusMiddleware, get_metrics
from app.core.exceptions import BaseAPIException
from app.core.error_handlers import (
    base_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler,
)
from app.config import get_settings

settings = get_settings()

setup_logging(log_level=settings.log_level, json_logs=settings.json_logs)
logger = get_logger(__name__)

app = FastAPI(
    title="LLM Evaluation Framework",
    description="Production-ready LLM evaluation platform with automated and human grading",
    version="1.0.0"
)

app.add_exception_handler(BaseAPIException, base_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(PrometheusMiddleware)

allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://yourdomain.com",
]

if settings.environment == "development":
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    max_age=3600,
)

app.include_router(auth.router)
app.include_router(prompts.router)
app.include_router(responses.router)
app.include_router(experiments.router)
app.include_router(evaluation.router)
app.include_router(human_feedback.router)
app.include_router(arena.router)
app.include_router(comparison.router)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    logger.info("application_startup", environment=settings.environment)
    init_db()
    logger.info("database_initialized")


@app.on_event("shutdown")
def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("application_shutdown")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "LLM Evaluation Framework API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    logger.debug("health_check_called")
    return {"status": "healthy"}


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return get_metrics()
