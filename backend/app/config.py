from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/llm_eval"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str = ""
    judge_model: str = "gpt-4o-mini"
    environment: str = "development"
    log_level: str = "INFO"
    json_logs: bool = True
    secret_key: str = "your-secret-key-change-in-production-min-32-chars"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
