from typing import Any

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.modules.identity.infrastructure.keycloak import KeycloakProvider

security = HTTPBearer()
keycloak = KeycloakProvider()


async def get_current_user(
    auth: HTTPAuthorizationCredentials = Security(security),  # noqa: B008
) -> dict[str, Any]:
    try:
        token = auth.credentials
        # The keycloak-openid library handles verification if configured,
        # or we use decode_token with verification options.
        return keycloak.decode_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
