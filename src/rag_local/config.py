from pathlib import Path

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracion central cargada desde variables de entorno y .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ollama_base_url: HttpUrl = Field(alias="OLLAMA_BASE_URL")
    ollama_chat_model: str = Field(alias="OLLAMA_CHAT_MODEL")
    ollama_embed_model: str = Field(alias="OLLAMA_EMBED_MODEL")

    rag_data_raw_dir: Path = Field(alias="RAG_DATA_RAW_DIR")
    rag_data_processed_dir: Path = Field(alias="RAG_DATA_PROCESSED_DIR")
    rag_vector_index_dir: Path = Field(alias="RAG_VECTOR_INDEX_DIR")

    rag_chunk_size: int = Field(default=1200, alias="RAG_CHUNK_SIZE")
    rag_chunk_overlap: int = Field(default=150, alias="RAG_CHUNK_OVERLAP")

    rag_top_k: int = Field(default=5, alias="RAG_TOP_K")
    rag_score_threshold: float = Field(default=0.2, alias="RAG_SCORE_THRESHOLD")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


def get_settings() -> Settings:
    """Devuelve una instancia validada de Settings."""
    return Settings()
