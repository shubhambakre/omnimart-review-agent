from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    omnimart_site_base_url: str = Field(default="http://localhost:8080")
    omnimart_internal_base_url: str = Field(default="http://localhost:8081")
    omnimart_internal_api_key: str = Field(default="dev-internal-key")

    gateway_base_url: str | None = None
    gateway_api_key: str | None = None

    anthropic_api_key: str | None = None
    anthropic_planner_model: str = "claude-sonnet-4-6"
    anthropic_critic_model: str = "claude-opus-4-7"
    anthropic_tool_model: str = "claude-haiku-4-5-20251001"


def load_settings() -> Settings:
    return Settings()
