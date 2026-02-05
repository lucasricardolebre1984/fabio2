"""Application configuration."""
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # ==================================================================
    # App
    # ==================================================================
    APP_NAME: str = "FC Soluções Financeiras API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # ==================================================================
    # Server
    # ==================================================================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # ==================================================================
    # Database
    # ==================================================================
    DATABASE_URL: str = "postgresql+asyncpg://fabio2_user:fabio2_pass@localhost:5432/fabio2"
    
    # Or separate
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "fabio2_user"
    DB_PASSWORD: str = "fabio2_pass"
    DB_NAME: str = "fabio2"
    
    # ==================================================================
    # Redis
    # ==================================================================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # ==================================================================
    # Security
    # ==================================================================
    SECRET_KEY: str = "dev-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12
    
    # ==================================================================
    # CORS
    # ==================================================================
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003,http://localhost:3004,http://localhost:3005"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # ==================================================================
    # Evolution API (WhatsApp)
    # ==================================================================
    EVOLUTION_API_URL: str = "http://localhost:8080"
    EVOLUTION_API_KEY: str = "default_key"
    WEBHOOK_URL: Optional[str] = None
    WA_INSTANCE_NAME: str = "fc-solucoes"
    WA_QR_TIMEOUT: int = 60000
    
    # ==================================================================
    # Storage
    # ==================================================================
    STORAGE_MODE: str = "local"  # local | s3
    STORAGE_LOCAL_PATH: str = "./storage"
    
    # AWS (if STORAGE_MODE=s3)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: Optional[str] = None
    AWS_S3_ENDPOINT: Optional[str] = None
    
    # ==================================================================
    # Z.AI API (GLM Models) - Chat, Vision, Audio, Image
    # ==================================================================
    ZAI_API_KEY: Optional[str] = None
    ZAI_MODEL_CHAT: str = "glm-4"
    ZAI_MODEL_VISION: str = "glm-4v"
    ZAI_MODEL_AUDIO: str = "glm-asr"
    ZAI_MODEL_IMAGE: str = "glm-image"
    
    # ==================================================================
    # DeepSeek API (Backup)
    # ==================================================================
    DEEPSEEK_API_KEY: Optional[str] = None
    
    # ==================================================================
    # OpenRouter API (Gratuito)
    # Obter API key: https://openrouter.ai/
    # ==================================================================
    OPENROUTER_API_KEY: Optional[str] = None
    
    # ==================================================================
    # Ollama API (Local)
    # ==================================================================
    OLLAMA_API_KEY: Optional[str] = None
    OLLAMA_URL: str = "http://localhost:11434"
    
    # Cost tracking
    CUSTO_POR_IMAGEM_USD: float = 0.015
    TAXA_CAMBIO_BRL: float = 5.0
    
    # ==================================================================
    # Logging
    # ==================================================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"  # json | text
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
