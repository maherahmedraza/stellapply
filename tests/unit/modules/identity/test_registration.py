from unittest.mock import AsyncMock, MagicMock

import pytest

from src.modules.identity.api.schemas import UserCreate
from src.modules.identity.domain.models import User
from src.modules.identity.domain.repository import UserRepository
from src.modules.identity.domain.services import RegistrationService


@pytest.fixture
def mock_repository():
    repo = MagicMock(spec=UserRepository)
    repo.get_by_email_hash = AsyncMock(return_value=None)
    repo.save = AsyncMock(side_effect=lambda u: u)
    return repo


@pytest.fixture
def service(mock_repository):
    return RegistrationService(mock_repository)


async def test_register_user_success(service, mock_repository):
    # Arrange
    schema = UserCreate(email="test@example.com", password="password123")

    # Act
    user = await service.register_user(schema)

    # Assert
    assert user.email_hash is not None
    assert user.password_hash != "password123"
    assert user.status == "active"
    mock_repository.get_by_email_hash.assert_called_once()
    mock_repository.save.assert_called_once()


async def test_register_user_duplicate_email(service, mock_repository):
    # Arrange
    mock_repository.get_by_email_hash.return_value = MagicMock(spec=User)
    schema = UserCreate(email="duplicate@example.com", password="password123")

    # Act & Assert
    with pytest.raises(ValueError, match="User with this email already exists"):
        await service.register_user(schema)
