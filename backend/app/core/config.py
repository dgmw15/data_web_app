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
        gemini_api_key (str): Google Gemini API key
        openai_api_key (str): OpenAI API key
        anthropic_api_key (str): Anthropic Claude API key
        deepseek_api_key (str): DeepSeek API key
        deepseek_base_url (str): DeepSeek API base URL
        vertex_ai_project_id (str): Google Cloud project ID for Vertex AI
        vertex_ai_location (str): Vertex AI location/region
        vertex_ai_credentials_path (str): Path to service account JSON file
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
    
    # AI Provider API Keys
    gemini_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    
    # Vertex AI Configuration
    vertex_ai_project_id: str = ""
    vertex_ai_location: str = "us-central1"
    vertex_ai_credentials_path: str = ""
    
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
