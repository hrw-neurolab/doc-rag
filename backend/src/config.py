from enum import Enum
import os

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoSettings(BaseModel):

    uri: str = "mongodb://localhost:27017"
    db_name: str = "doc-rag"
    search_index_dimensions: int = 1536
    search_index_similarity: str = "cosine"
    search_index_field: str = "embedding"
    search_index_name: str = "embedding_index"
    search_top_k: int = 5


class JWTSettings(BaseModel):

    secret_key_access: str
    secret_key_refresh: str
    expires_hours_access: int = 1
    expires_hours_refresh: int = 7200  # 30 days
    algorithm: str = "HS256"


class StorageSettings(BaseModel):

    directory: str = os.path.join("..", "storage")


class ModelProvider(str, Enum):
    OLLAMA = "ollama"


class EmbeddingClientSettings(BaseModel):
    model_provider: ModelProvider = ModelProvider.OLLAMA
    model_name: str = "nomic-embed-text:latest"
    base_url: str = "http://localhost:11434"
    num_ctx: int = 5000
    temperature: float = 0.0
    chunk_size: int = 1000
    chunk_overlap: int = 300


class ChatClientSettings(BaseModel):
    model_provider: ModelProvider = ModelProvider.OLLAMA
    model_name: str = "gemma3:12b"
    base_url: str = "http://localhost:11435"
    num_ctx: int = 10000
    temperature: float = 0.2
    max_history: int = 10


class Settings(BaseSettings):

    # General settings
    frontend_url: str = "http://localhost:5173"
    version: str = "0.1.0"

    # Mongo Engine settings
    mongo: MongoSettings = MongoSettings()

    # JWT settings
    jwt: JWTSettings

    # Storage settings
    storage: StorageSettings = StorageSettings()

    # Embedding Client settings
    embedding_client: EmbeddingClientSettings = EmbeddingClientSettings()

    # Chat Client settings
    chat_client: ChatClientSettings = ChatClientSettings()

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=os.path.join("..", ".env"),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
    )


CONFIG = Settings()
"""Global configuration object."""
