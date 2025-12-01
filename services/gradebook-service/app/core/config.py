"""Application configuration"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "gradebook_service_db"
    ENV: str = "local"
    LOG_LEVEL: str = "INFO"
    APP_NAME: str = "Gradebook Service"
    APP_VERSION: str = "1.0.0"
    CORS_ORIGINS: str = "*"
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

