import os

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoSettings(BaseModel):

    uri: str = "mongodb://localhost:27017"
    db_name: str = "doc-rag"


class JWTSettings(BaseModel):

    secret_key_access: str
    secret_key_refresh: str
    expires_hours_access: int = 1
    expires_hours_refresh: int = 7200  # 30 days
    algorithm: str = "HS256"


class Settings(BaseSettings):
    """Server config settings."""

    # General settings
    frontend_url: str = "http://localhost:5173"
    version: str = "0.1.0"

    # Mongo Engine settings
    mongo: MongoSettings = MongoSettings()

    # JWT settings
    jwt: JWTSettings

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=os.path.join("..", ".env"),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
    )


CONFIG = Settings()
"""Global configuration object."""
