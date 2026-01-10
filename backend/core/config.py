"""
Application Configuration

This module manages all application settings using Pydantic Settings.
Environment variables are loaded from .env file (see .env.example for template).

Key Features:
- Automatic environment detection (development vs production)
- Database URL auto-switching (SQLite for dev, PostgreSQL for prod)
- Storage path configuration (local dev vs cloud deployment)
- API key management for Whisper, Groq, and Dynamics 365
- CORS configuration for frontend access

Usage:
    from backend.core.config import settings

    # Access settings
    api_key = settings.WHISPER_API_KEY
    is_prod = settings.is_production
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    """
    Application Settings

    All settings are loaded from environment variables or .env file.
    Case-sensitive variable names are required.

    Environment Variables:
        ENVIRONMENT: "development" or "production" (default: development)
        DATABASE_URL: Database connection string (auto-detects from environment)
        LOCAL_STORAGE_PATH: File storage directory (auto-detects from environment)
        WHISPER_API_KEY: OpenAI API key for Whisper transcription
        GROQ_API_KEY: Groq API key for AI data extraction
        DYNAMICS_BASE_URL: Microsoft Dynamics 365 base URL
        DYNAMICS_CLIENT_ID: Azure AD app client ID
        DYNAMICS_CLIENT_SECRET: Azure AD app client secret
        DYNAMICS_TENANT_ID: Azure AD tenant ID
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_parse_enums=True
    )

    # ==================== Environment Detection ====================
    # Set to "production" for deployed environments, "development" for local dev
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT == "production"

    # ==================== Application Settings ====================
    APP_NAME: str = "Farm Data Automation"
    DEBUG: bool = False
    # Comma-separated list of allowed CORS origins for frontend access
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    def get_origins_list(self) -> List[str]:
        """
        Parse ALLOWED_ORIGINS into a list for CORS middleware

        Returns:
            List of allowed origin URLs
        """
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',')]
        return self.ALLOWED_ORIGINS

    # ==================== Database Settings ====================
    # Auto-switches: SQLite for development, PostgreSQL for production
    # Production should set DATABASE_URL to postgresql+asyncpg://... connection string
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./farm_data.db"
    )

    # ==================== Storage Settings ====================
    # Auto-detects environment: uses ./storage/recordings for development,
    # /app/storage/recordings for production (Docker/cloud deployments)
    # Override with LOCAL_STORAGE_PATH environment variable if needed
    LOCAL_STORAGE_PATH: str = os.getenv(
        "LOCAL_STORAGE_PATH",
        "/app/storage/recordings" if os.getenv("ENVIRONMENT") == "production"
        else "./storage/recordings"
    )

    # ==================== Whisper Transcription Settings ====================
    # Choose transcription method:
    # - "api": OpenAI Whisper API (~$0.006/min, fast, requires API key)
    # - "local": Local Whisper model (FREE, slower, no API key needed)
    WHISPER_MODE: str = os.getenv("WHISPER_MODE", "local")  # Default to FREE local

    # OpenAI Whisper API Settings (only needed if WHISPER_MODE="api")
    # Get API key from https://platform.openai.com/api-keys
    WHISPER_API_KEY: str = ""
    WHISPER_MODEL: str = "whisper-1"

    # Local Whisper Settings (used if WHISPER_MODE="local")
    # Model options: tiny, base, small, medium, large
    # Recommended: "base" for good balance of speed and quality
    WHISPER_LOCAL_MODEL: str = os.getenv("WHISPER_LOCAL_MODEL", "base")

    # ==================== Groq AI Settings ====================
    # Used for structured data extraction from transcribed text
    # FREE tier: 14,400 requests/day
    # Get API key from https://console.groq.com/keys
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    GROQ_TEMPERATURE: float = 0.1  # Low temperature for consistent extraction

    # ==================== Azure Settings (Legacy) ====================
    # DEPRECATED: Kept for backward compatibility during migration
    # The system now uses OpenAI Whisper + Groq AI instead of Azure services
    # These can be removed in future versions
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER_NAME: str = "voice-recordings"
    AZURE_SPEECH_KEY: str = ""
    AZURE_SPEECH_REGION: str = "eastus"
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_KEY: str = ""
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4"
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"

    # ==================== Microsoft Dynamics 365 Settings ====================
    # Used for syncing animal data to bioTrack+ (Dynamics 365)
    # Setup Instructions:
    #   1. Register an app in Azure AD (Azure Portal > App Registrations)
    #   2. Grant API permissions: Dynamics CRM > user_impersonation
    #   3. Create a client secret and copy the values below
    #   4. Add the app user to Dynamics 365 with appropriate roles
    DYNAMICS_BASE_URL: str = ""  # e.g., https://agsights.crm3.dynamics.com
    DYNAMICS_CLIENT_ID: str = ""  # Azure AD App Registration Client ID
    DYNAMICS_CLIENT_SECRET: str = ""  # Azure AD App Registration Client Secret
    DYNAMICS_TENANT_ID: str = ""  # Azure AD Tenant ID

    # ==================== Queue Settings ====================
    # Redis URL for background job processing (future feature)
    # Not currently used - processing is done synchronously
    REDIS_URL: str = "redis://localhost:6379/0"

    # ==================== Security Settings ====================
    # SECRET_KEY: Change this to a random secure string in production
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"  # JWT algorithm for token signing
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Session timeout duration


settings = Settings()
