from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "Appcentre by iDev"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database URLs
    # Vercel / FastAPI ulanishi uchun (Transaction Pool)
    DATABASE_URL: str = Field(
        ...,
        description="Asyncpg bilan ishlash uchun postgresql+asyncpg:// bilan boshlanishi kerak",
    )
    # Alembic migratsiyalari uchun (Direct Connection)
    DIRECT_DATABASE_URL: str = Field(
        ..., description="Alembic uchun to'g'ridan-to'g'ri ulanish URLi"
    )

    # JWT Authentication sozlamalari
    SECRET_KEY: str = Field(..., description="JWT tokenlar uchun maxfiy kalit")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 kun amal qiladi

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()