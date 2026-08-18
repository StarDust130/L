from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "L API"
    web_app_url: str = "http://localhost:3000"

    # 🔏 Clerk config
    clerk_secret_key: str = "test"
    clerk_authorized_parties: list[str] = ["http://localhost:3000"]

    # 🤖 Groq config
    groq_api_key: str = "test"
    groq_model: str = "openai/gpt-oss-120b"

    # Gemini config
    gemini_api_key: str = "test"

    # 💾 Postgres database
    database_url: str = "sqlite+aiosqlite:///./local.db"

    # 💬 Telegram token
    telegram_bot_token: str = "test"
    telegram_chat_id: str = "test"

    # 🔎 Tavily config
    tavily_api_key: str = "test"

    @field_validator("clerk_authorized_parties", mode="before")
    @classmethod
    def parse_clerk_authorized_parties(cls, value):
        if value is None:
            return ["http://localhost:3000"]
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return ["http://localhost:3000"]
            if value.startswith("["):
                import json

                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return [str(v) for v in parsed]
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


# Read Setting(.env) once and use it as cache.
@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
