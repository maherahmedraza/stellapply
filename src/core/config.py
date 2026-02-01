from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database connection and pool settings."""

    model_config = SettingsConfigDict(env_prefix="DB_", extra="ignore")

    URL: str = Field(
        default="postgresql+asyncpg://stellapply:password@localhost:5432/stellapply",
        description="Full SQLAlchemy database connection URL.",
    )
    POOL_SIZE: int = Field(default=20, ge=5, le=100)
    MAX_OVERFLOW: int = Field(default=10, ge=0, le=50)
    POOL_TIMEOUT: int = Field(default=30, ge=10)


class RedisSettings(BaseSettings):
    """Redis cache and session settings."""

    model_config = SettingsConfigDict(env_prefix="REDIS_", extra="ignore")

    URL: str = Field(default="redis://localhost:6379/0")
    USE_SSL: bool = Field(default=False)
    TIMEOUT: int = Field(default=5, ge=1)


class SecuritySettings(BaseSettings):
    """Security, JWT, and Encryption settings."""

    model_config = SettingsConfigDict(env_prefix="SECURITY_", extra="ignore")

    SECRET_KEY: str = Field(
        default="super-secret-key-that-is-at-least-32-chars-long", min_length=32
    )
    ENCRYPTION_KEY: str = Field(
        default="another-very-long-secret-key-for-encryption-32", min_length=32
    )
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, ge=1)


class AISettings(BaseSettings):
    """AI Service settings for Gemini and embeddings."""

    model_config = SettingsConfigDict(env_prefix="AI_", extra="ignore")

    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-pro"
    EMBEDDING_MODEL: str = "text-embedding-004"
    RATE_LIMIT_RPM: int = Field(default=60, ge=1)


class StorageSettings(BaseSettings):
    """Object storage settings (MinIO/S3)."""

    model_config = SettingsConfigDict(env_prefix="STORAGE_", extra="ignore")

    ENDPOINT: str = "localhost:9000"
    ACCESS_KEY: str = "minioadmin"
    SECRET_KEY: str = "minioadmin"
    SECURE: bool = False
    BUCKET_RESUMES: str = "resumes"
    BUCKET_ASSETS: str = "assets"


class KeycloakSettings(BaseSettings):
    """Keycloak OIDC settings."""

    model_config = SettingsConfigDict(env_prefix="KC_", extra="ignore")

    URL: str = "http://localhost:8081"
    REALM: str = "stellapply"
    CLIENT_ID: str = "stellapply-backend"
    CLIENT_SECRET: str | None = None
    ADMIN_USER: str = "admin"
    ADMIN_PASSWORD: str = "admin"


class FeatureSettings(BaseSettings):
    """Feature flags for gradual rollout."""

    model_config = SettingsConfigDict(env_prefix="FEATURE_", extra="ignore")

    ENABLE_AI_MATCHING: bool = True
    ENABLE_RESUME_PARSING: bool = True
    ENABLE_BETA_UI: bool = False


class Settings(BaseSettings):
    """Main settings composition."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Core
    APP_NAME: str = "Stellapply"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True

    # Composed Settings
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    ai: AISettings = Field(default_factory=AISettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    keycloak: KeycloakSettings = Field(default_factory=KeycloakSettings)
    features: FeatureSettings = Field(default_factory=FeatureSettings)

    # Global CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    @field_validator("ENVIRONMENT")
    @classmethod
    def set_debug(cls, v: str) -> str:
        if v == "production":
            cls.DEBUG = False
        return v


@lru_cache
def get_settings() -> Settings:
    """Singleton pattern for settings loading."""
    return Settings()


# Global settings instance
settings = get_settings()
