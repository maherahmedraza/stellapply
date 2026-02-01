import uuid
from typing import Protocol, runtime_checkable

from src.modules.identity.domain.models import User


@runtime_checkable
class UserRepository(Protocol):
    async def get_by_email_hash(self, email_hash: str) -> User | None: ...

    async def get_by_id(self, user_id: uuid.UUID) -> User | None: ...

    async def save(self, user: User) -> User: ...
