from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["local", "test", "staging", "production"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AI_",
        env_file=".env",
        extra="ignore",
        frozen=True,
    )

    environment: Environment = "local"
    debug: bool = False
    redis_url: str = "redis://localhost:6379/0"
    celery_task_always_eager: bool = False

    @property
    def docs_enabled(self) -> bool:
        return self.environment != "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
