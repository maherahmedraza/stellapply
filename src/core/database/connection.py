from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool
import logging

from src.core.config import settings
from src.core.database.base_model import Base

logger = logging.getLogger(__name__)


# Build async URL properly
def _build_async_url(url: str) -> str:
    """Convert sync URL to async URL if needed."""
    if "postgresql+psycopg://" in url:
        return url.replace("postgresql+psycopg://", "postgresql+asyncpg://")
    elif "postgresql://" in url and "+asyncpg" not in url:
        return url.replace("postgresql://", "postgresql+asyncpg://")
    return url


async_db_url = _build_async_url(settings.db.URL)

engine = create_async_engine(
    async_db_url,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,  # Verify connections before use
    pool_size=settings.db.POOL_SIZE,
    max_overflow=settings.db.MAX_OVERFLOW,
    pool_timeout=settings.db.POOL_TIMEOUT,
    pool_recycle=1800,  # Recycle connections every 30 minutes
    poolclass=AsyncAdaptedQueuePool,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

# Reference Base to satisfy imports without unused warnings.
__all__ = [
    "engine",
    "AsyncSessionLocal",
    "get_db",
    "get_db_context",
    "check_db_health",
    "Base",
]


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.

    DOES NOT auto-commit - caller is responsible for committing.
    This allows read-only operations to not trigger commits.
    """
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions outside of FastAPI dependencies.
    Use this in Celery tasks, scripts, etc.
    """
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def check_db_health() -> bool:
    """Health check for database connectivity."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
