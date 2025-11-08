"""
Configuration settings for the API
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/sentiment"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # OpenTelemetry
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4318"
    OTEL_SERVICE_NAME: str = "sentiment-api"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # Environment
    ENVIRONMENT: str = "development"
    VERSION: str = "1.0.0"

    # ML Model
    MODEL_PATH: str = "models/sentiment_model.joblib"

    # Instrumentation
    ENABLE_TRACING: bool = True
    ENABLE_METRICS: bool = True
    JAEGER_ENDPOINT: str = "localhost:6831"
    OTLP_ENDPOINT: str = ""  # Optional OTLP endpoint
    PROMETHEUS_PORT: int = 9090

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text

    class Config:
        env_file = "../../.env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
