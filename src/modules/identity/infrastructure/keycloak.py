from typing import Any

from keycloak import KeycloakAdmin, KeycloakOpenID

from src.core.config import settings


class KeycloakProvider:
    def __init__(self) -> None:
        # Keycloak 24+ doesn't use /auth path
        server_url = settings.keycloak.URL.rstrip("/")

        self.openid = KeycloakOpenID(
            server_url=server_url,
            client_id=settings.keycloak.CLIENT_ID,
            realm_name=settings.keycloak.REALM,
            client_secret_key=settings.keycloak.CLIENT_SECRET,
        )

    def get_admin_client(self) -> KeycloakAdmin:
        server_url = settings.keycloak.URL.rstrip("/")

        return KeycloakAdmin(
            server_url=server_url,
            username=settings.keycloak.ADMIN_USER,
            password=settings.keycloak.ADMIN_PASSWORD,
            realm_name=settings.keycloak.REALM,
            user_realm_name="master",
            verify=True,
        )

    def get_token(self, username: str, password: str) -> dict[str, Any]:
        return self.openid.token(username, password)

    def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        return self.openid.refresh_token(refresh_token)

    def logout(self, refresh_token: str) -> None:
        self.openid.logout(refresh_token)

    def create_user(self, email: str, password: str, full_name: str = "") -> str:
        admin = self.get_admin_client()
        # Split full name
        names = full_name.split(" ", 1)
        first_name = names[0]
        last_name = names[1] if len(names) > 1 else ""

        return admin.create_user(
            {
                "email": email,
                "username": email,
                "enabled": True,
                "firstName": first_name,
                "lastName": last_name,
                "emailVerified": True,
                "credentials": [
                    {"value": password, "type": "password", "temporary": False}
                ],
                "requiredActions": [],  # Clear all required actions so user can login immediately
            },
            exist_ok=False,
        )

    def decode_token(self, token: str) -> dict[str, Any]:
        # Verification is handled by keycloak library
        # or manual JWT verification with public keys
        return self.openid.decode_token(token)
