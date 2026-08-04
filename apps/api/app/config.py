from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "L API" 
    frontend_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

# Read Setting(.env) once and use it as cache.
@lru_cache
def get_settings() -> Settings:
    return Settings() #type: ignore