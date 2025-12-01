"""
Application configuration module
Loads settings from environment variables
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "profile_service_db"
    
    # JWT settings (for token validation)
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    # Environment settings
    ENV: str = "local"  # local, dev, prod
    LOG_LEVEL: str = "INFO"
    
    # Application settings
    APP_NAME: str = "Profile Service"
    APP_VERSION: str = "1.0.0"
    
    # CORS settings (optional)
    CORS_ORIGINS: str = "*"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components"""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Construct async database URL from components"""
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENV in ("local", "dev")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENV == "prod"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance
    Uses lru_cache to avoid recreating settings on every call
    """
    return Settings()


# Convenience function to get settings
settings = get_settings()

