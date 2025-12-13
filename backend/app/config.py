"""
Application Configuration

Loads settings from environment variables with sensible defaults.
Uses Pydantic BaseSettings for validation and type coercion.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via environment variables or .env file.
    """
    
    # Use SettingsConfigDict for Pydantic v2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra env vars not defined here
    )
    
    # Application
    APP_NAME: str = "Proaktiv Dokument Hub"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    SECRET_KEY: str = "dev_secret_key_change_in_production"
    
    # CORS
    ALLOWED_ORIGINS: str = '["http://localhost:3000"]'
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/dokument_hub"
    
    # Azure Storage
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER_NAME: str = "templates"
    AZURE_CONTAINER_NAME: str = "templates"  # Alias
    AZURE_STORAGE_PREVIEWS_CONTAINER: str = "previews"
    
    # Azure Key Vault (Phase 2)
    KEY_VAULT_URL: str = ""
    
    # Redis Cache (Optional)
    REDIS_URL: str = ""
    
    # Authentication (mocked for Phase 1)
    AUTH_ENABLED: bool = False
    MOCK_USER_EMAIL: str = "admin@proaktiv.no"
    MOCK_USER_NAME: str = "Admin User"
    
    # Vitec Integration (Phase 2)
    VITEC_INSTALLATION_ID: str = ""
    VITEC_ENVIRONMENT: str = "qa"
    VITEC_ACCESS_KEY: str = ""


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Settings are loaded once and cached for the lifetime of the application.
    """
    return Settings()


# Global settings instance
settings = get_settings()


def get_mock_user() -> dict:
    """
    Get mock user for Phase 1 development.
    
    In production, this will be replaced by Easy Auth headers.
    
    Returns:
        dict: User information with email, name, and admin status.
    """
    return {
        "email": settings.MOCK_USER_EMAIL,
        "name": settings.MOCK_USER_NAME,
        "is_admin": True
    }
