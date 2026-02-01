from typing import Protocol, runtime_checkable
from uuid import UUID

from src.modules.persona.domain.models import Persona


@runtime_checkable
class PersonaRepository(Protocol):
    async def get_by_id(self, persona_id: UUID) -> Persona | None: ...

    async def get_by_user_id(self, user_id: UUID) -> Persona | None: ...

    async def save(self, persona: Persona) -> Persona: ...

    async def delete(self, persona_id: UUID) -> None: ...
