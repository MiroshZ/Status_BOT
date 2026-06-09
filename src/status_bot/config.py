from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    telegram_bot_token: SecretStr = Field(alias="TELEGRAM_BOT_TOKEN")
    polza_api_key: SecretStr = Field(alias="POLZA_API_KEY")
    polza_base_url: str = Field(default="https://polza.ai/api/v1", alias="POLZA_BASE_URL")
    polza_model: str = Field(default="openai/gpt-4o", alias="POLZA_MODEL")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


@lru_cache
def get_settings() -> Settings:
    return Settings()
