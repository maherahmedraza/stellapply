from typing import Any

from keycloak import KeycloakAdmin, KeycloakOpenID

from src.core.config import settings


class KeycloakProvider:
    def __init__(self) -> None:
        self.openid = KeycloakOpenID(
            server_url=settings.keycloak.URL + "/auth"
            if "/auth" not in settings.keycloak.URL
            else settings.keycloak.URL,
            client_id=settings.keycloak.CLIENT_ID,
            realm_name=settings.keycloak.REALM,
            client_secret_key=settings.keycloak.CLIENT_SECRET,
        )

    def get_admin_client(self) -> KeycloakAdmin:
        return KeycloakAdmin(
            server_url=settings.keycloak.URL + "/auth"
            if "/auth" not in settings.keycloak.URL
            else settings.keycloak.URL,
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

    def decode_token(self, token: str) -> dict[str, Any]:
        # Verification is handled by keycloak library
        # or manual JWT verification with public keys
        return self.openid.decode_token(token)
