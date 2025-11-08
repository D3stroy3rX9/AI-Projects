"""
Configuration management using pydantic-settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    database_url: str = "postgresql://translator:translator_password@localhost:5432/audio_translator"

    # Whisper Model Configuration
    whisper_model: str = "base"  # Options: tiny, base, small, medium

    # Translation Backend
    translation_backend: str = "libretranslate"  # Options: libretranslate, nllb
    libretranslate_url: str = "https://libretranslate.de"

    # CORS
    cors_origins: str = "http://localhost:3000"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Optional: Redis for caching
    redis_url: str = ""

    # Debug mode
    debug: bool = False

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
