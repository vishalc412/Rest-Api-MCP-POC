from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://vita:vita@localhost:5432/vitaclan"
    SYNC_DATABASE_URL: str = "postgresql://vita:vita@localhost:5432/vitaclan"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080  # 7 days

    # Firebase (OTP)
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_CREDENTIALS_PATH: str = ""

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_LLM_MODEL: str = "llama3.3:70b"
    OLLAMA_VISION_MODEL: str = "llava:13b"

    # Storage (MinIO / S3)
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_BUCKET: str = "vitaclan-docs"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_REGION: str = "ap-south-1"
    S3_USE_SSL: bool = False

    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001

    # WhatsApp Business API
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = "vitaclan-webhook-verify"

    # FCM
    FCM_SERVER_KEY: str = ""

    # Google Cloud Vision (OCR fallback)
    GOOGLE_CLOUD_CREDENTIALS_PATH: str = ""

    # AI rate limits (free tier)
    FREE_TIER_AI_SUMMARIES_PER_MONTH: int = 5
    FREE_TIER_VOICE_QUERIES_PER_MONTH: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
