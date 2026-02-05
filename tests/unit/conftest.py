import pytest
from unittest.mock import MagicMock


@pytest.fixture(scope="session")
def postgres_container():
    return MagicMock()


@pytest.fixture(scope="session")
def redis_container():
    return MagicMock()


@pytest.fixture(scope="session")
def async_engine():
    return MagicMock()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    # Do nothing for unit tests
    yield
