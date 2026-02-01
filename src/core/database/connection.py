from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.core.database.base_model import Base

# Update DATABASE_URL to use asyncpg if not already
async_db_url = settings.db.URL.replace("postgresql+psycopg://", "postgresql+asyncpg://")

engine = create_async_engine(
    async_db_url,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)

# Reference Base to satisfy imports without unused warnings.
__all__ = ["engine", "AsyncSessionLocal", "get_db", "Base"]


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
