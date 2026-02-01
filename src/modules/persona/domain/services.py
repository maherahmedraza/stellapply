from uuid import UUID

from src.modules.persona.domain.models import (
    Persona,
)
from src.modules.persona.domain.repository import PersonaRepository
from src.modules.persona.domain.schemas import PersonaUpdate


class PersonaService:
    def __init__(self, repository: PersonaRepository):
        self._repository = repository

    async def get_persona_by_user_id(self, user_id: UUID) -> Persona | None:
        return await self._repository.get_by_user_id(user_id)

    async def update_persona(self, user_id: UUID, schema: PersonaUpdate) -> Persona:
        persona = await self._repository.get_by_user_id(user_id)
        if not persona:
            persona = Persona(user_id=user_id)

        # Update core fields
        if schema.full_name is not None:
            persona.full_name = schema.full_name
        if schema.email is not None:
            persona.email = schema.email
        if schema.phone is not None:
            persona.phone = schema.phone
        if schema.location_city is not None:
            persona.location_city = schema.location_city
        if schema.location_state is not None:
            persona.location_state = schema.location_state
        if schema.location_country is not None:
            persona.location_country = schema.location_country
        if schema.work_authorization is not None:
            persona.work_authorization = schema.work_authorization
        if schema.remote_preference is not None:
            persona.remote_preference = schema.remote_preference

        # Summary embedding
        if schema.summary_embedding is not None:
            persona.summary_embedding = schema.summary_embedding

        # Recalculate completeness
        persona.completeness_score = self._calculate_completeness(persona)

        # Trigger embedding update (placeholder for now)
        # TODO: Integrate with AI worker/service

        return await self._repository.save(persona)

    def _calculate_completeness(self, persona: Persona) -> float:
        score = 0.0
        if persona.full_name:
            score += 10
        if persona.email:
            score += 10
        if persona.location_city:
            score += 10
        if persona.experiences:
            score += 30
        if persona.educations:
            score += 20
        if persona.skills:
            score += 10
        if persona.career_preference:
            score += 10
        return float(min(score, 100))
