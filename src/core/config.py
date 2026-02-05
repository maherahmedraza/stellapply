from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
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

    SECRET_KEY: SecretStr = Field(
        ...,  # Required - no default
        min_length=32,
        description="REQUIRED: Set via SECURITY_SECRET_KEY environment variable",
    )
    ENCRYPTION_KEY: SecretStr = Field(
        ...,  # Required - no default
        min_length=32,
        description="REQUIRED: Set via SECURITY_ENCRYPTION_KEY environment variable",
    )
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, ge=1)

    @field_validator("SECRET_KEY", "ENCRYPTION_KEY", mode="before")
    @classmethod
    def validate_not_default(cls, v: str) -> str:
        dangerous_defaults = [
            "super-secret",
            "password",
            "changeme",
            "secret",
            "default",
        ]
        if any(d in v.lower() for d in dangerous_defaults):
            raise ValueError("Using insecure default secret - set a proper value!")
        return v


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

    model_config = SettingsConfigDict(
        env_prefix="KC_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

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
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("ENVIRONMENT")
    @classmethod
    def set_debug(cls, v: str) -> str:
        if v == "production":
            cls.DEBUG = False
        return v

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Ensure production environment has proper configuration."""
        if self.ENVIRONMENT == "production":
            # Check for development defaults
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production")

            if "localhost" in self.db.URL:
                raise ValueError("Production database URL cannot be localhost")

            if "localhost" in self.redis.URL:
                raise ValueError("Production Redis URL cannot be localhost")

            if not self.ai.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY required in production")

            if len(self.ALLOWED_ORIGINS) == 0:
                raise ValueError("ALLOWED_ORIGINS must be set in production")

            if any("localhost" in origin for origin in self.ALLOWED_ORIGINS):
                raise ValueError("localhost not allowed in production CORS origins")

        return self


@lru_cache
def get_settings() -> Settings:
    """Singleton pattern for settings loading."""
    return Settings()


# Global settings instance
settings = get_settings()
