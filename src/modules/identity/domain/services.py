import hashlib

from src.core.database.governance import DataClassification, RetentionPolicy
from src.core.security.encryption import encrypt_data
from src.core.security.hashing import get_password_hash
from src.modules.identity.api.schemas import TokenResponse, UserCreate
from src.modules.identity.domain.models import User
from src.modules.identity.domain.repository import UserRepository
from src.modules.identity.infrastructure.keycloak import KeycloakProvider


class RegistrationService:
    def __init__(self, repository: UserRepository):
        self._repository = repository

    async def register_user(self, schema: UserCreate) -> User:
        # 0. Sync with Keycloak first (if success, proceed to DB)
        keycloak = KeycloakProvider()
        try:
            keycloak.create_user(
                email=schema.email,
                password=schema.password,
                full_name=schema.full_name or "",
            )
        except Exception as e:
            # If user already exists in Keycloak but not in DB, we'll hit this
            # For now, let's assume if KC fails, we fail (unless user already exists)
            if "already exists" not in str(e).lower():
                raise ValueError(f"Identity provider error: {str(e)}")
        # 1. Check if user already exists
        email_hash = hashlib.sha256(schema.email.lower().encode()).hexdigest()
        existing_user = await self._repository.get_by_email_hash(email_hash)
        if existing_user:
            raise ValueError("User with this email already exists")

        # 2. Prepare user data
        password_hash = get_password_hash(schema.password)
        # encrypt_data returns a str (base64 encoded), store it as bytes in BYTEA column
        email_encrypted = encrypt_data(schema.email).encode()

        # 3. Create user entity
        user = User(
            email_encrypted=email_encrypted,
            email_hash=email_hash,
            password_hash=password_hash,
            status="active",
            governance_metadata={
                "classification": DataClassification.RESTRICTED.value,
                "retention": RetentionPolicy.PERMANENT.value,
                "consent_version": "1.0",
                "consent_date": None,  # Will be set on registration complete
            },
        )

        # 4. Save and return
        return await self._repository.save(user)


class AuthService:
    def __init__(self) -> None:
        self.keycloak = KeycloakProvider()

    def login(self, username: str, password: str) -> TokenResponse:
        try:
            token_data = self.keycloak.get_token(username, password)
            return TokenResponse(
                access_token=token_data["access_token"],
                refresh_token=token_data["refresh_token"],
                expires_in=token_data["expires_in"],
                refresh_expires_in=token_data["refresh_expires_in"],
                token_type=token_data["token_type"],
            )
        except Exception as e:
            import logging

            logging.getLogger(__name__).error(f"Login failed for {username}: {str(e)}")
            raise

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        token_data = self.keycloak.refresh_token(refresh_token)
        return TokenResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            expires_in=token_data["expires_in"],
            refresh_expires_in=token_data["refresh_expires_in"],
            token_type=token_data["token_type"],
        )

    def logout(self, refresh_token: str) -> None:
        self.keycloak.logout(refresh_token)
