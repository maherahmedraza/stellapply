import logging
import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from src.core.config import settings
from src.core.infrastructure.redis import redis_provider

logger = logging.getLogger(__name__)


# OIDC standard claims + custom claims
class TokenPayload(BaseModel):
    sub: str  # user_id
    exp: datetime
    iat: datetime
    jti: str
    roles: list[str] = []
    tier: str = "free"


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


import os
import uuid
import logging
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from src.core.config import settings
from src.core.infrastructure.redis import redis_provider

logger = logging.getLogger(__name__)


class JWTHandler:
    """Enterprise JWT handler with RS256 asymmetric signing."""

    def __init__(self) -> None:
        self.algorithm = settings.security.ALGORITHM
        self.access_expire = settings.security.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_expire_days = settings.security.REFRESH_TOKEN_EXPIRE_DAYS

        # Load keys based on algorithm
        if self.algorithm.startswith("RS"):
            self._load_rsa_keys()
        else:
            # Fallback to symmetric for HS256
            self.secret_key = settings.security.SECRET_KEY.get_secret_value()
            self.public_key = self.secret_key

    def _load_rsa_keys(self) -> None:
        """Load RSA keys from files or environment."""
        private_key_path = os.getenv("JWT_PRIVATE_KEY_PATH", "keys/private.pem")
        public_key_path = os.getenv("JWT_PUBLIC_KEY_PATH", "keys/public.pem")

        # Try loading from files
        try:
            if os.path.exists(private_key_path):
                with open(private_key_path, "rb") as f:
                    self.secret_key = serialization.load_pem_private_key(
                        f.read(), password=None, backend=default_backend()
                    )
            else:
                # Fallback to environment variable
                private_key_pem = os.getenv("JWT_PRIVATE_KEY")
                if not private_key_pem:
                    # For dev, we might want a warning or a default,
                    # but the review says "no default" for production.
                    # We'll use the SECRET_KEY as a placeholder IF NOT PRODUCTION,
                    # but let's follow the review's strictness.
                    raise ValueError(
                        "RS256 algorithm requires private key. "
                        "Set JWT_PRIVATE_KEY_PATH or JWT_PRIVATE_KEY environment variable."
                    )
                self.secret_key = serialization.load_pem_private_key(
                    private_key_pem.encode(), password=None, backend=default_backend()
                )

            if os.path.exists(public_key_path):
                with open(public_key_path, "rb") as f:
                    self.public_key = serialization.load_pem_public_key(
                        f.read(), backend=default_backend()
                    )
            else:
                public_key_pem = os.getenv("JWT_PUBLIC_KEY")
                if not public_key_pem:
                    # Try to derive public key from private key if not provided
                    self.public_key = self.secret_key.public_key()
                else:
                    self.public_key = serialization.load_pem_public_key(
                        public_key_pem.encode(), backend=default_backend()
                    )
        except Exception as e:
            logger.error(f"Failed to load RSA keys: {e}")
            # If in development, maybe generate or fallback, but let's be strict for now
            raise

    def _create_token(self, data: dict[str, Any], expires_delta: timedelta) -> str:
        to_encode = data.copy()
        now = datetime.now(UTC)
        expire = now + expires_delta

        to_encode.update(
            {"exp": expire, "iat": now, "jti": str(uuid.uuid4()), "nbf": now}
        )

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_access_token(self, user_id: str, roles: list[str], tier: str) -> str:
        payload: dict[str, Any] = {"sub": user_id, "roles": roles, "tier": tier}
        return self._create_token(payload, timedelta(minutes=self.access_expire))

    def create_refresh_token(self, user_id: str) -> str:
        payload: dict[str, Any] = {"sub": user_id, "type": "refresh"}
        return self._create_token(payload, timedelta(days=self.refresh_expire_days))

    async def verify_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                options={
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                    "require": ["exp", "iat", "sub", "jti"],
                },
            )
            token_data = TokenPayload(**payload)

            # Check revocation in Redis
            if await redis_provider.exists(f"blacklist:{token_data.jti}"):
                raise JWTError("Token has been revoked")

            return token_data

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except JWTError as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e

    async def revoke_token(self, jti: str, expires_at: datetime) -> None:
        """Add token JTI to Redis blacklist until it naturally expires."""
        now = datetime.now(UTC)
        ttl = int((expires_at - now).total_seconds())
        if ttl > 0:
            await redis_provider.set(f"blacklist:{jti}", "revoked", expire=ttl)

    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        # 1. Verify refresh token
        payload = await self.verify_token(refresh_token)

        # 2. Check if it's actually a refresh token
        # We need to decode again to check 'type' as TokenPayload doesn't have it
        raw_payload = jwt.decode(
            refresh_token, self.public_key, algorithms=[self.algorithm]
        )
        if raw_payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")

        # 3. Rate limiting for refresh (5 per hour per user)
        rate_key = f"rate_limit:refresh:{payload.sub}"
        current = await redis_provider.get(rate_key)
        if current and int(current) >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Refresh token rate limit exceeded. Try again later.",
            )

        if not current:
            await redis_provider.set(rate_key, 1, expire=3600)
        else:
            await redis_provider.set(rate_key, int(current) + 1, expire=3600)

        # 4. Issue new pair
        return TokenPair(
            access_token=self.create_access_token(
                payload.sub, payload.roles, payload.tier
            ),
            refresh_token=self.create_refresh_token(payload.sub),
        )


# Global instances
jwt_handler = JWTHandler()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


# Dependencies
async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    return await jwt_handler.verify_token(token)


def require_roles(allowed_roles: list[str]) -> Callable[..., Any]:
    # ruff: noqa: B008
    async def role_checker(
        current_user: TokenPayload = Depends(get_current_user),
    ) -> TokenPayload:
        if not any(role in allowed_roles for role in current_user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
            )
        return current_user

    return role_checker


def require_tier(min_tier: str) -> Callable[..., Any]:
    # ruff: noqa: B008
    tiers = {"free": 0, "pro": 1, "enterprise": 2}

    async def tier_checker(
        current_user: TokenPayload = Depends(get_current_user),
    ) -> TokenPayload:
        if tiers.get(current_user.tier, 0) < tiers.get(min_tier, 0):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Subscription tier '{min_tier}' required",
            )
        return current_user

    return tier_checker
