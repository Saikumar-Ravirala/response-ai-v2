from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "ResponseAI v2"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = Field("postgresql+asyncpg://postgres:postgres@localhost:5432/response_ai_v2", alias="DATABASE_URL")
    
    # Security
    SECRET_KEY: str = Field("your-secret-key-here", alias="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Voice Providers
    RETELL_API_KEY: str = Field("your-retell-api-key", alias="RETELL_API_KEY")
    RETELL_WEBHOOK_SECRET: str = Field("your-retell-webhook-secret", alias="RETELL_WEBHOOK_SECRET")
    
    LIVEKIT_API_KEY: str = Field("your-livekit-api-key", alias="LIVEKIT_API_KEY")
    LIVEKIT_API_SECRET: str = Field("your-livekit-api-secret", alias="LIVEKIT_API_SECRET")
    LIVEKIT_URL: str = Field("https://your-livekit-url.livekit.cloud", alias="LIVEKIT_URL")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
