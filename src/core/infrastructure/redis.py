import logging
from typing import Any

import redis.asyncio as redis

from src.core.config import settings

logger = logging.getLogger(__name__)


import logging
from typing import Any, Optional
from contextlib import asynccontextmanager

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from src.core.config import settings

logger = logging.getLogger(__name__)


class RedisProvider:
    """
    Async Redis provider with proper connection lifecycle.
    Implements health checks and graceful degradation.
    """

    def __init__(self) -> None:
        self._url = settings.redis.URL
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected and self._client is not None

    async def connect(self) -> None:
        """Initialize the Redis connection pool."""
        if self._connected and self._client:
            return

        try:
            self._pool = redis.ConnectionPool.from_url(
                self._url,
                decode_responses=True,
                max_connections=20,
                socket_timeout=settings.redis.TIMEOUT,
                socket_connect_timeout=settings.redis.TIMEOUT,
                retry_on_timeout=True,
                ssl=settings.redis.USE_SSL,
            )
            self._client = redis.Redis(connection_pool=self._pool)

            # Verify connection
            await self._client.ping()
            self._connected = True
            logger.info("Connected to Redis")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self._connected = False
            raise

    async def disconnect(self) -> None:
        """Close the Redis connection pool."""
        if self._pool:
            await self._pool.disconnect()
            self._connected = False
            logger.info("Disconnected from Redis")

    async def ensure_connected(self) -> None:
        """Ensure connection is established, reconnect if needed."""
        if not self.is_connected:
            await self.connect()

    async def get(self, key: str) -> Optional[str]:
        """Get a value, returns None if Redis unavailable."""
        try:
            await self.ensure_connected()
            if not self._client:
                return None
            return await self._client.get(key)  # type: ignore
        except Exception as e:
            logger.warning(f"Redis GET failed for {key}: {e}")
            return None

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a value, returns False if Redis unavailable."""
        try:
            await self.ensure_connected()
            if not self._client:
                return False
            await self._client.set(key, value, ex=expire)  # type: ignore
            return True
        except Exception as e:
            logger.warning(f"Redis SET failed for {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete a key, returns False if Redis unavailable."""
        try:
            await self.ensure_connected()
            if not self._client:
                return False
            await self._client.delete(key)  # type: ignore
            return True
        except Exception as e:
            logger.warning(f"Redis DELETE failed for {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists, returns False if Redis unavailable."""
        try:
            await self.ensure_connected()
            if not self._client:
                return False
            result = await self._client.exists(key)  # type: ignore
            return bool(result > 0)
        except Exception as e:
            logger.warning(f"Redis EXISTS failed for {key}: {e}")
            return False

    async def incr(self, key: str, expire: Optional[int] = None) -> int:
        """Increment a counter, returns 0 if Redis unavailable."""
        try:
            await self.ensure_connected()
            if not self._client:
                return 0
            result = await self._client.incr(key)  # type: ignore
            if expire and result == 1:  # First increment, set expiry
                await self._client.expire(key, expire)  # type: ignore
            return int(result)
        except Exception as e:
            logger.warning(f"Redis INCR failed for {key}: {e}")
            return 0

    async def health_check(self) -> bool:
        """Check Redis connectivity."""
        try:
            await self.ensure_connected()
            if not self._client:
                return False
            await self._client.ping()  # type: ignore
            return True
        except Exception:
            return False

    async def publish(self, channel: str, message: str) -> int:
        """Publish a message to a channel."""
        try:
            await self.ensure_connected()
            if not self._client:
                return 0
            return await self._client.publish(channel, message)  # type: ignore
        except Exception as e:
            logger.warning(f"Redis PUBLISH failed for {channel}: {e}")
            return 0


# Singleton instance
redis_provider = RedisProvider()


@asynccontextmanager
async def redis_lifespan():
    """Context manager for Redis lifecycle in FastAPI or background tasks."""
    await redis_provider.connect()
    try:
        yield
    finally:
        await redis_provider.disconnect()


# Singleton instance
redis_provider = RedisProvider()
