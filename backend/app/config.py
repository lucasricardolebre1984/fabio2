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
    # Logging
    # ==================================================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"  # json | text
    
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
    EVOLUTION_API_KEY: str = "default_key_change_in_production"
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
    # DeepSeek API (Backup)
    # ==================================================================
    DEEPSEEK_API_KEY: Optional[str] = None
    
    # ==================================================================
    # OpenAI API (Primary for VIVA WhatsApp)
    # ==================================================================
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_API_MODEL: str = "gpt-5-mini"
    OPENAI_AUDIO_MODEL: str = "gpt-4o-mini-transcribe"
    OPENAI_TTS_MODEL: str = "tts-1"
    OPENAI_TTS_VOICE: str = "alloy"
    OPENAI_IMAGE_MODEL: str = "gpt-image-1"
    OPENAI_VISION_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_FALLBACK_LOCAL: bool = True
    OPENAI_TIMEOUT_SECONDS: int = 60

    # VIVA provider strategy (institucional): openai
    VIVA_PROVIDER: str = "openai"

    # ==================================================================
    # VIVA Memory (RAG/Redis/pgvector) - disabled by default (clean agent)
    # ==================================================================
    VIVA_MEMORY_ENABLED: bool = False
    VIVA_BRAIN_ROOT: str = "COFRE"
    VIVA_MEMORY_FILE_LOG_ENABLED: bool = True

    # ==================================================================
    # Google Calendar (agenda bridge)
    # ==================================================================
    FRONTEND_BASE_URL: str = "http://localhost:3000"
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_CALENDAR_CLIENT_ID: Optional[str] = None
    GOOGLE_CALENDAR_CLIENT_SECRET: Optional[str] = None
    GOOGLE_GMAIL_CLIENT_ID: Optional[str] = None
    GOOGLE_GMAIL_CLIENT_SECRET: Optional[str] = None
    GOOGLE_SERVICE_ACCOUNT_ID: Optional[str] = None
    GOOGLE_SERVICE_ACCOUNT_EMAIL: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/google-calendar/callback"
    GOOGLE_CALENDAR_DEFAULT_ID: str = "primary"
    GOOGLE_CALENDAR_SCOPE: str = "https://www.googleapis.com/auth/calendar"
    GOOGLE_CALENDAR_SYNC_ENABLED: bool = True

    # ==================================================================
    # MiniMax TTS (voz VIVA)
    # ==================================================================
    MINIMAX_API_KEY: Optional[str] = None
    MINIMAX_GROUP_ID: Optional[str] = None
    MINIMAX_BASE_URL: str = "https://api.minimax.io"
    MINIMAX_TTS_MODEL: str = "speech-2.8-hd"
    MINIMAX_TTS_VOICE_ID: str = "Portuguese_LovelyLady"
    MINIMAX_TTS_SPEED: float = 1.0
    MINIMAX_TTS_PITCH: float = 2.0
    MINIMAX_TTS_VOLUME: float = 3.64
    MINIMAX_TTS_FORMAT: str = "mp3"
    MINIMAX_TTS_SAMPLE_RATE: int = 32000
    MINIMAX_TTS_BITRATE: int = 128000
    MINIMAX_TTS_CHANNEL: int = 1

    # ==================================================================
    # Legacy vars (ignored in runtime logic; kept for backward compatibility)
    # ==================================================================
    ZAI_API_KEY: Optional[str] = None
    
    # ==================================================================
    # Ollama API (Local)
    # ==================================================================
    OLLAMA_API_KEY: Optional[str] = None
    OLLAMA_URL: str = "http://localhost:11434"
    
    # Cost tracking
    CUSTO_POR_IMAGEM_USD: float = 0.015
    TAXA_CAMBIO_BRL: float = 5.0
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
