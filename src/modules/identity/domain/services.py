import hashlib
import uuid

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
        self._keycloak = KeycloakProvider()

    async def register_user(self, schema: UserCreate) -> User:
        # 1. Check if user already exists
        email_hash = hashlib.sha256(schema.email.lower().encode()).hexdigest()
        existing_user = await self._repository.get_by_email_hash(email_hash)
        if existing_user:
            raise ValueError("User with this email already exists")

        # 2. Create user in Keycloak first
        keycloak_admin = self._keycloak.get_admin_client()
        keycloak_user_id = keycloak_admin.create_user(
            {
                "email": schema.email,
                "username": schema.email,
                "firstName": schema.name.split()[0] if schema.name else "User",
                "lastName": " ".join(schema.name.split()[1:])
                if schema.name and len(schema.name.split()) > 1
                else "",
                "enabled": True,
                "emailVerified": True,  # For dev, skip email verification
                "credentials": [
                    {"type": "password", "value": schema.password, "temporary": False}
                ],
            }
        )

        # 3. Prepare local user data
        password_hash = get_password_hash(schema.password)
        # encrypt_data returns a str (base64 encoded), store it as bytes in BYTEA column
        email_encrypted = encrypt_data(schema.email).encode()

        # 4. Create user entity in local DB
        user = User(
            id=uuid.UUID(keycloak_user_id),
            email_encrypted=email_encrypted,
            email_hash=email_hash,
            password_hash=password_hash,
            status="active",
            governance_metadata={
                "classification": DataClassification.RESTRICTED.value,
                "retention": RetentionPolicy.PERMANENT.value,
                "consent_version": "1.0",
                "consent_date": None,  # Will be set on registration complete
                "keycloak_id": keycloak_user_id,
            },
        )

        # 5. Save and return
        saved_user = await self._repository.save(user)
        saved_user.email = (
            schema.email
        )  # Set temporary attribute for Pydantic validation
        return saved_user


class AuthService:
    def __init__(self) -> None:
        self.keycloak = KeycloakProvider()

    def login(self, username: str, password: str) -> TokenResponse:
        token_data = self.keycloak.get_token(username, password)
        return TokenResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            expires_in=token_data["expires_in"],
            refresh_expires_in=token_data["refresh_expires_in"],
            token_type=token_data["token_type"],
        )

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
