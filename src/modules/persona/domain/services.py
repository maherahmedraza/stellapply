from uuid import UUID

from src.modules.persona.domain.models import (
    CareerPreference,
    Education,
    Experience,
    Persona,
    RemotePreference,
    Skill,
    WorkAuthorization,
)
from src.modules.persona.domain.repository import PersonaRepository
from src.modules.persona.domain.schemas import (
    CareerPreferenceUpdate,
    EducationCreate,
    EducationUpdate,
    ExperienceCreate,
    ExperienceUpdate,
    PersonaUpdate,
    SkillCreate,
    SkillUpdate,
)


class PersonaService:
    def __init__(self, repository: PersonaRepository):
        self._repository = repository

    async def get_persona_by_user_id(self, user_id: UUID) -> Persona | None:
        return await self._repository.get_by_user_id(user_id)

    async def update_persona(self, user_id: UUID, schema: PersonaUpdate) -> Persona:
        persona = await self._repository.get_by_user_id(user_id)
        if not persona:
            # Ensure user exists in local database (for Keycloak users)
            email = schema.email or "user@example.com"
            await self._repository.ensure_user_exists(user_id, email)

            # Create a new persona if it doesn't exist
            persona = Persona(
                user_id=user_id,
                full_name=schema.full_name or "New User",
                email=email,
                work_authorization=(
                    schema.work_authorization or WorkAuthorization.NOT_REQUIRED
                ),
                remote_preference=(schema.remote_preference or RemotePreference.ANY),
            )
            # Set optional fields
            if schema.phone is not None:
                persona.phone = schema.phone
            if schema.location_city is not None:
                persona.location_city = schema.location_city
            if schema.location_state is not None:
                persona.location_state = schema.location_state
            if schema.location_country is not None:
                persona.location_country = schema.location_country
        else:
            # Update existing persona fields
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

        return await self._repository.save(persona)

    def _calculate_completeness(self, persona: Persona) -> float:
        score = 0.0
        if persona.full_name:
            score += 10
        if persona.email:
            score += 10
        if persona.location_city:
            score += 10
        if hasattr(persona, "experiences") and persona.experiences:
            score += 30
        if hasattr(persona, "educations") and persona.educations:
            score += 20
        if hasattr(persona, "skills") and persona.skills:
            score += 10
        if hasattr(persona, "career_preference") and persona.career_preference:
            score += 10
        return float(min(score, 100))

    # =============== Experience Methods ===============

    async def add_experience(
        self, user_id: UUID, schema: ExperienceCreate
    ) -> Experience:
        persona = await self._repository.get_by_user_id(user_id)
        if not persona:
            raise ValueError(
                "Persona not found. Please create a persona first by saving Basic Info."
            )

        experience = Experience(
            persona_id=persona.id,
            company_name=schema.company_name,
            job_title=schema.job_title,
            start_date=schema.start_date,
            end_date=schema.end_date,
            description_original=schema.description,
            description_active=schema.description,
            achievements=schema.achievements,
            skills_used=schema.skills_used,
            experience_embedding=schema.experience_embedding,
        )
        exp = await self._repository.add_experience(experience)

        # Recalculate completeness
        persona.completeness_score = self._calculate_completeness(persona)
        await self._repository.save(persona)

        return exp

    async def update_experience(
        self, user_id: UUID, experience_id: UUID, schema: ExperienceUpdate
    ) -> Experience | None:
        persona = await self._repository.get_by_user_id(user_id)
        if not persona:
            return None
        return await self._repository.update_experience(
            persona.id, experience_id, schema
        )

    async def delete_experience(self, user_id: UUID, experience_id: UUID) -> None:
        persona = await self._repository.get_by_user_id(user_id)
        if persona:
            await self._repository.delete_experience(persona.id, experience_id)
            # Recalculate completeness
            persona.completeness_score = self._calculate_completeness(persona)
            await self._repository.save(persona)

    # =============== Education Methods ===============

    async def add_education(self, user_id: UUID, schema: EducationCreate) -> Education:
        persona = await self._repository.get_by_user_id(user_id)
        if not persona:
            raise ValueError(
                "Persona not found. Please create a persona first by saving Basic Info."
            )

        education = Education(
            persona_id=persona.id,
            institution_name=schema.institution_name,
            degree_type=schema.degree_type,
            field_of_study=schema.field_of_study,
            graduation_date=schema.graduation_date,
            gpa=schema.gpa,
        )
        edu = await self._repository.add_education(education)

        # Recalculate completeness
        persona.completeness_score = self._calculate_completeness(persona)
        await self._repository.save(persona)

        return edu

    async def update_education(
        self, user_id: UUID, education_id: UUID, schema: EducationUpdate
    ) -> Education | None:
        persona = await self._repository.get_by_user_id(user_id)
        if not persona:
            return None
        return await self._repository.update_education(persona.id, education_id, schema)

    async def delete_education(self, user_id: UUID, education_id: UUID) -> None:
        persona = await self._repository.get_by_user_id(user_id)
        if persona:
            await self._repository.delete_education(persona.id, education_id)
            # Recalculate completeness
            persona.completeness_score = self._calculate_completeness(persona)
            await self._repository.save(persona)

    # =============== Skill Methods ===============

    async def add_skill(self, user_id: UUID, schema: SkillCreate) -> Skill:
        persona = await self._repository.get_by_user_id(user_id)
        if not persona:
            raise ValueError(
                "Persona not found. Please create a persona first by saving Basic Info."
            )

        skill = Skill(
            persona_id=persona.id,
            name=schema.name,
            category=schema.category,
            proficiency_level=schema.proficiency_level,
        )
        s = await self._repository.add_skill(skill)

        # Recalculate completeness
        persona.completeness_score = self._calculate_completeness(persona)
        await self._repository.save(persona)

        return s

    async def update_skill(
        self, user_id: UUID, skill_id: UUID, schema: SkillUpdate
    ) -> Skill | None:
        persona = await self._repository.get_by_user_id(user_id)
        if not persona:
            return None
        return await self._repository.update_skill(persona.id, skill_id, schema)

    async def delete_skill(self, user_id: UUID, skill_id: UUID) -> None:
        persona = await self._repository.get_by_user_id(user_id)
        if persona:
            await self._repository.delete_skill(persona.id, skill_id)
            # Recalculate completeness
            persona.completeness_score = self._calculate_completeness(persona)
            await self._repository.save(persona)

    # =============== Career Preference Methods ===============

    async def get_career_preference(self, user_id: UUID) -> CareerPreference | None:
        persona = await self._repository.get_by_user_id(user_id)
        if not persona:
            return None
        return await self._repository.get_career_preference(persona.id)

    async def update_career_preference(
        self, user_id: UUID, schema: CareerPreferenceUpdate
    ) -> CareerPreference:
        persona = await self._repository.get_by_user_id(user_id)
        if not persona:
            raise ValueError(
                "Persona not found. Please create a persona first by saving Basic Info."
            )
        pref = await self._repository.update_career_preference(persona.id, schema)

        # Recalculate completeness
        persona.completeness_score = self._calculate_completeness(persona)
        await self._repository.save(persona)

        return pref
