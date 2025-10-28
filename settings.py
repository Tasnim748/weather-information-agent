# settings.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App
    app_name: str = "Weather Info Agent API"
    environment: str = "dev"  # dev|staging|prod
    log_level: str = "INFO"
    google_api_key: str = "please-give-valid-api-key"

    # Defaults
    default_units: str = "auto"   # metric|imperial|auto
    default_lang: str = "en"

    # Provider keys (optional at this stage)
    weather_api_key: str | None = None
    air_quality_api_key: str | None = None
    geocoding_api_key: str | None = None
    timezone_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env"
    )
