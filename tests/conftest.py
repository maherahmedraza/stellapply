import pytest
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from src.core.config import Settings
from src.core.database.connection import get_db
from src.api.main import app
from src.core.database.base_model import Base


# Test settings — uses env vars because Settings has nested BaseSettings models
# with env prefixes (DB_, SECURITY_, AI_, etc.)
@pytest.fixture(scope="session")
def settings(monkeypatch_session) -> Settings:
    """Create test settings via environment variables.

    Settings uses composed sub-models (DatabaseSettings, SecuritySettings, etc.)
    that each read from prefixed env vars. We set those env vars here.
    """
    env_overrides = {
        "ENVIRONMENT": "development",  # test is not a valid Literal value
        # Database — prefix DB_
        "DB_URL": "postgresql+asyncpg://test:test@localhost:5432/test_db",
        # Security — prefix SECURITY_
        "SECURITY_SECRET_KEY": "test-only-not-for-production-key-min32chars!!",
        "SECURITY_ENCRYPTION_KEY": "test-only-not-for-production-enc-min32chars!!",
        # AI — prefix AI_
        "AI_GEMINI_API_KEY": "test-api-key-not-real",
        # Redis — prefix REDIS_
        "REDIS_URL": "redis://localhost:6379/1",
    }
    for key, value in env_overrides.items():
        monkeypatch_session.setenv(key, value)

    return Settings()


@pytest.fixture(scope="session")
def monkeypatch_session():
    """Session-scoped monkeypatch for env var overrides."""
    from _pytest.monkeypatch import MonkeyPatch

    mp = MonkeyPatch()
    yield mp
    mp.undo()


# PostgreSQL test container
@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    with PostgresContainer("postgres:16-alpine") as postgres:
        postgres.with_env("POSTGRES_DB", "test_db")
        yield postgres


# Redis test container
@pytest.fixture(scope="session")
def redis_container() -> Generator[RedisContainer, None, None]:
    with RedisContainer("redis:7-alpine") as redis:
        yield redis


# Async engine
@pytest.fixture(scope="session")
def async_engine(postgres_container: PostgresContainer):
    connection_url = postgres_container.get_connection_url()
    # Convert to async URL
    async_url = connection_url.replace("postgresql://", "postgresql+asyncpg://")

    engine = create_async_engine(async_url, echo=True)
    return engine


# Create tables
@pytest.fixture(scope="session", autouse=True)
async def setup_database(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Session factory
@pytest.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


# Test client
@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    # Override dependency
    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# Authenticated client
@pytest.fixture
async def auth_client(client: AsyncClient, test_user: dict) -> AsyncClient:
    # Login to get token
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]},
    )
    token = response.json()["access_token"]

    client.headers["Authorization"] = f"Bearer {token}"
    return client


# Test user fixture
@pytest.fixture
async def test_user(db_session: AsyncSession) -> dict:
    from src.modules.identity.domain.services import UserService

    user_service = UserService(db_session)
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    }

    user = await user_service.create_user(**user_data)

    return {**user_data, "id": str(user.id)}


# Mock Gemini responses
@pytest.fixture
def mock_gemini(mocker):
    mock_response = mocker.patch("src.core.ai.gemini_client.GeminiClient.generate_text")
    mock_response.return_value = "Enhanced bullet point with metrics"
    return mock_response
