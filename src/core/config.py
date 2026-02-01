from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Stellapply"
    APP_ENV: str = "dev"
    SECRET_KEY: str = "change-me-in-production"

    # Database Settings
    DATABASE_URL: str = (
        "postgresql+asyncpg://stellapply:password@localhost:5432/stellapply"
    )

    # JWT Settings
    JWT_ALGORITHM: str = "RS256"  # Keycloak uses RS256 by default
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Keycloak Settings
    KC_URL: str = "http://localhost:8081"
    KC_REALM: str = "stellapply"
    KC_CLIENT_ID: str = "stellapply-backend"
    KC_CLIENT_SECRET: str | None = None  # Needed if client is confidential
    KC_ADMIN_USER: str = "admin"
    KC_ADMIN_PASSWORD: str = "admin"

    # AI Settings
    GEMINI_API_KEY: str | None = None

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
