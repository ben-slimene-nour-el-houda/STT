import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Core configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = REDIS_URL
    API_KEYS: List[str] = os.getenv("API_KEYS", "testkey").split(",")
    RATE_LIMIT_TOKENS: int = int(os.getenv("RATE_LIMIT_TOKENS", "10"))
    RATE_LIMIT_INTERVAL: int = int(os.getenv("RATE_LIMIT_INTERVAL", "60"))  # seconds
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    # Set to "auto" for automatic detection, "cpu" or "cuda" to force
    STT_MODEL_SIZE: str = os.getenv("STT_MODEL_SIZE", "base")
    ENABLE_LLM: bool = os.getenv("ENABLE_LLM", "false").lower() == "true"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
