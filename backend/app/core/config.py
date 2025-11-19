"""
Core Configuration for DataCrunch API

This module manages environment variables and application settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        app_name (str): Application name
        debug (bool): Debug mode flag
        api_version (str): API version string
        redis_url (str): Redis connection URL for Celery
        database_url (str): Database connection string
        secret_key (str): Secret key for encryption
        algorithm (str): Encryption algorithm
    """
    app_name: str = "DataCrunch API"
    debug: bool = True
    api_version: str = "v1"
    
    # Redis Configuration (Celery Broker)
    redis_url: str = "redis://localhost:6379/0"
    
    # Database Configuration
    database_url: str = "sqlite:///./datacrunch.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Singleton pattern for settings to avoid re-reading .env file.
    
    Returns:
        Settings: Application settings instance.
    
    Source/Caller:
        - Called by: All modules requiring configuration
    """
    return Settings()


settings = get_settings()
