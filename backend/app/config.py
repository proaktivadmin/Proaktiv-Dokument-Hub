"""
Application Configuration

Loads settings from environment variables with sensible defaults.
Uses Pydantic BaseSettings for validation and type coercion.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache
from typing import Optional
import logging
import warnings

logger = logging.getLogger(__name__)

# Default development secret key - NEVER use in production
_DEV_SECRET_KEY = "dev_secret_key_change_in_production"


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
    APP_NAME: str = "Proaktiv Admin"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    SECRET_KEY: str = ""  # Will be validated below
    
    # CORS
    ALLOWED_ORIGINS: str = '["http://localhost:3000"]'
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/dokument_hub"
    
    # Platform indicator (railway, vercel, azure)
    PLATFORM: str = "railway"
    
    # Azure Storage (DEPRECATED - kept for backward compatibility)
    # Template content is now stored in the database.
    # These variables are only used if PLATFORM is "azure" for rollback.
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER_NAME: str = "templates"
    AZURE_CONTAINER_NAME: str = "templates"  # Alias
    AZURE_STORAGE_PREVIEWS_CONTAINER: str = "previews"
    
    # Azure Key Vault (DEPRECATED)
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
    VITEC_HUB_BASE_URL: str = ""
    VITEC_HUB_PRODUCT_LOGIN: str = ""
    VITEC_HUB_ACCESS_KEY: str = ""
    
    # WebDAV Network Storage
    WEBDAV_URL: str = ""
    WEBDAV_USERNAME: str = ""
    WEBDAV_PASSWORD: str = ""
    
    # Simple Password Auth
    APP_PASSWORD_HASH: str = ""  # bcrypt hash of the app password
    AUTH_SESSION_EXPIRE_DAYS: int = 7
    AUTH_INACTIVITY_TIMEOUT_MINUTES: int = 30
    
    # Microsoft Graph API (Teams/SharePoint/Exchange integration)
    MICROSOFT_TENANT_ID: str = "placeholder"  # Azure AD tenant ID
    MICROSOFT_CLIENT_ID: str = "placeholder"  # App registration client ID
    MICROSOFT_CLIENT_SECRET: str = ""  # App registration secret
    MICROSOFT_SENDER_EMAIL: str = ""  # Email address for sending (must be authorized)

    # Firecrawl (web scraping / crawling)
    # Keep secrets out of code: set FIRECRAWL_API_KEY via env (.env locally, Railway variables in prod)
    FIRECRAWL_API_KEY: str = ""
    FIRECRAWL_TIMEOUT_MS: int = 30000
    FIRECRAWL_ONLY_MAIN_CONTENT: bool = True


    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """
        Validate SECRET_KEY based on environment.
        
        - In production: Raise error if missing or using default
        - In development: Use default key with warning
        """
        # Get APP_ENV from the values dict or use default
        # Note: info.data contains already validated fields
        app_env = "development"  # Default
        
        if not v or v == _DEV_SECRET_KEY:
            # Check if we're in production by looking at common production indicators
            # This is validated before APP_ENV is available, so we check env directly
            import os
            env = os.getenv("APP_ENV", "development")
            
            if env in ("production", "prod", "staging"):
                raise ValueError(
                    "SECRET_KEY must be set to a secure value in production! "
                    "Set the SECRET_KEY environment variable to a random string (32+ chars)."
                )
            else:
                # Development environment - use default with warning
                if not v:
                    warnings.warn(
                        "SECRET_KEY not set. Using insecure default for development. "
                        "Set SECRET_KEY in production!",
                        UserWarning,
                        stacklevel=2
                    )
                    return _DEV_SECRET_KEY
                return v
        
        # Warn if key is too short
        if len(v) < 32:
            warnings.warn(
                f"SECRET_KEY is only {len(v)} characters. "
                "Recommended: 32+ characters for security.",
                UserWarning,
                stacklevel=2
            )
        
        return v


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
