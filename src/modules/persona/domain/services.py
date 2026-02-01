from uuid import UUID

from src.modules.persona.api.schemas import PersonaUpdate
from src.modules.persona.domain.models import Persona
from src.modules.persona.domain.repository import PersonaRepository


class PersonaService:
    def __init__(self, repository: PersonaRepository):
        self._repository = repository

    async def get_persona_by_user_id(self, user_id: UUID) -> Persona | None:
        return await self._repository.get_by_user_id(user_id)

    async def update_persona(self, user_id: UUID, schema: PersonaUpdate) -> Persona:
        persona = await self._repository.get_by_user_id(user_id)
        if not persona:
            persona = Persona(user_id=user_id)

        # Update fields
        if schema.preferred_name is not None:
            persona.preferred_name = schema.preferred_name
        if schema.pronouns is not None:
            persona.pronouns = schema.pronouns
        if schema.location is not None:
            persona.location = schema.location
        if schema.experience is not None:
            persona.experience = [item.model_dump() for item in schema.experience]
        if schema.education is not None:
            persona.education = [item.model_dump() for item in schema.education]
        if schema.skills is not None:
            persona.skills = schema.skills

        # Recalculate completeness
        persona.completeness_score = self._calculate_completeness(persona)

        # Trigger embedding update (placeholder for now)
        # TODO: Integrate with AI worker/service

        return await self._repository.save(persona)

    def _calculate_completeness(self, persona: Persona) -> int:
        score = 0
        if persona.preferred_name:
            score += 10
        if persona.location:
            score += 10
        if persona.experience:
            score += 30
        if persona.education:
            score += 20
        if persona.skills:
            score += 20
        if persona.pronouns:
            score += 10
        return min(score, 100)
