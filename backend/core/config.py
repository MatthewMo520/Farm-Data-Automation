"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # App settings
    APP_NAME: str = "Farm Data Automation"
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Database settings
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/farm_data_automation"

    # Azure settings
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER_NAME: str = "voice-recordings"
    AZURE_SPEECH_KEY: str = ""
    AZURE_SPEECH_REGION: str = "eastus"
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_KEY: str = ""
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4"
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"

    # Dynamics 365 settings
    DYNAMICS_BASE_URL: str = ""  # e.g., https://org.crm.dynamics.com
    DYNAMICS_CLIENT_ID: str = ""
    DYNAMICS_CLIENT_SECRET: str = ""
    DYNAMICS_TENANT_ID: str = ""

    # Queue settings
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
