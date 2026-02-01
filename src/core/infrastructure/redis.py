import logging
from typing import Any

import redis.asyncio as redis

from src.core.config import settings

logger = logging.getLogger(__name__)


class RedisProvider:
    """Provider for Redis operations (caching, revocation, rate-limiting)."""

    def __init__(self) -> None:
        self._url = settings.redis.URL
        self._pool: redis.ConnectionPool | None = None
        self._client: redis.Redis | None = None

    async def connect(self) -> None:
        """Initialize the Redis connection pool."""
        try:
            self._pool = redis.ConnectionPool.from_url(
                self._url, decode_responses=True, ssl=settings.redis.USE_SSL
            )
            self._client = redis.Redis(connection_pool=self._pool)
            # Handle potential union type from ping() for Mypy
            await self._client.ping()  # type: ignore[misc]
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    async def disconnect(self) -> None:
        """Close the Redis connection pool."""
        if self._pool:
            await self._pool.disconnect()
            logger.info("Disconnected from Redis")

    async def get(self, key: str) -> Any:
        if not self._client:
            raise RuntimeError("Redis client not connected")
        return await self._client.get(key)

    async def set(self, key: str, value: Any, expire: int | None = None) -> None:
        if not self._client:
            raise RuntimeError("Redis client not connected")
        await self._client.set(key, value, ex=expire)

    async def delete(self, key: str) -> None:
        if not self._client:
            raise RuntimeError("Redis client not connected")
        await self._client.delete(key)

    async def exists(self, key: str) -> bool:
        if not self._client:
            raise RuntimeError("Redis client not connected")
        result = await self._client.exists(key)
        return bool(result > 0)


# Singleton instance
redis_provider = RedisProvider()
