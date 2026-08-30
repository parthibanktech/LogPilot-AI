"""
production_rag.config.settings - Centralized Environment Configuration
"""

import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "LogPilot AI Enterprise System"
    VERSION: str = "5.3.0"
    
    # Base Paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    LOG_DIR: str = os.path.join(DATA_DIR, "logs")
    SOP_DIR: str = os.path.join(DATA_DIR, "it_sops.md")
    SOP_PATH: str = os.path.join(DATA_DIR, "it_sops.md")
    FAISS_SAVE_DIR: str = os.path.join(DATA_DIR, "faiss_index")
    TELEMETRY_PATH: str = os.path.join(DATA_DIR, "telemetry.json")
    
    # Model Configurations
    DEEPSEEK_MODEL: str = "deepseek-chat"
    OPENAI_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # LLM Settings
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # RAG Configuration
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_DENSE: int = 15
    TOP_K_SPARSE: int = 15
    FINAL_TOP_K: int = 5
    
    # Resilience & Backoff Settings
    MAX_RETRIES: int = 3
    INITIAL_BACKOFF: float = 1.0
    MAX_BACKOFF: float = 8.0
    
    # Cache Settings
    CACHE_SIMILARITY_THRESHOLD: float = 0.92

    # Guardrails
    BLOCKED_COMMAND_KEYWORDS: List[str] = [
        "DROP DATABASE", "DELETE FROM", "rm -rf", "sudo rm", "mkfs", "dd if="
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
