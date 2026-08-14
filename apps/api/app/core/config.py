from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "L API"
    web_app_url: str

    # 🔏 Clerk config
    clerk_secret_key: str
    clerk_authorized_parties: list[str]

    # 🤖 Groq config
    groq_api_key: str
    groq_model: str = "openai/gpt-oss-20b"

    # 💾 Postgres database
    database_url: str

    # 💬 Telegram token
    telegram_bot_token: str
    telegram_chat_id: str

    # 🔎 Tavily config
    tavily_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


# Read Setting(.env) once and use it as cache.
@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
