from functools import cached_property

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(default="postgresql+psycopg://agentflow:agentflow@localhost:5432/agentflow", alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    jwt_secret_key: str = Field(default="change-me-in-production", alias="JWT_SECRET_KEY")
    api_key_encryption_secret: str = Field(default="change-me-32-bytes-secret", alias="API_KEY_ENCRYPTION_SECRET")
    default_chat_model: str = Field(default="gpt-4o-mini", alias="DEFAULT_CHAT_MODEL")
    default_embedding_model: str = Field(default="text-embedding-3-small", alias="DEFAULT_EMBEDDING_MODEL")

    @cached_property
    def cors_origins(self) -> list[str]:
        if self.app_env == "production":
            return []
        return ["http://localhost:3000", "http://127.0.0.1:3000"]


settings = Settings()
