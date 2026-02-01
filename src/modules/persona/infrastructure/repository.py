from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.persona.domain.models import Persona
from src.modules.persona.domain.repository import PersonaRepository


class SQLAlchemyPersonaRepository(PersonaRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, persona_id: UUID) -> Persona | None:
        result = await self._session.execute(
            select(Persona).where(
                Persona.id == persona_id, Persona.is_deleted.is_(False)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> Persona | None:
        result = await self._session.execute(
            select(Persona).where(
                Persona.user_id == user_id, Persona.is_deleted.is_(False)
            )
        )
        return result.scalar_one_or_none()

    async def save(self, persona: Persona) -> Persona:
        self._session.add(persona)
        await self._session.flush()  # Ensure ID is generated
        return persona

    async def delete(self, persona_id: UUID) -> None:
        persona = await self.get_by_id(persona_id)
        if persona:
            persona.soft_delete()
            self._session.add(persona)
