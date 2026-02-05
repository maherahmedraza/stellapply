from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.persona.domain.models import (
    CareerPreference,
    Education,
    Experience,
    Persona,
    Skill,
)
from src.modules.persona.domain.repository import PersonaRepository
from src.modules.persona.domain.schemas import (
    CareerPreferenceUpdate,
    EducationUpdate,
    ExperienceUpdate,
    SkillUpdate,
)


class SQLAlchemyPersonaRepository(PersonaRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, persona_id: UUID) -> Persona | None:
        result = await self._session.execute(
            select(Persona)
            .options(
                selectinload(Persona.experiences),
                selectinload(Persona.educations),
                selectinload(Persona.skills),
                selectinload(Persona.certifications),
                selectinload(Persona.projects),
                selectinload(Persona.career_preference),
            )
            .where(Persona.id == persona_id, Persona.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> Persona | None:
        result = await self._session.execute(
            select(Persona)
            .options(
                selectinload(Persona.experiences),
                selectinload(Persona.educations),
                selectinload(Persona.skills),
                selectinload(Persona.certifications),
                selectinload(Persona.projects),
                selectinload(Persona.career_preference),
            )
            .where(Persona.user_id == user_id, Persona.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def save(self, persona: Persona) -> Persona:
        self._session.add(persona)
        await self._session.flush()
        await self._session.commit()
        # Re-fetch with relationships to avoid MissingGreenlet errors
        result = await self._session.execute(
            select(Persona)
            .options(
                selectinload(Persona.experiences),
                selectinload(Persona.educations),
                selectinload(Persona.skills),
                selectinload(Persona.certifications),
                selectinload(Persona.projects),
                selectinload(Persona.career_preference),
            )
            .where(Persona.id == persona.id)
        )
        return result.scalar_one()

    async def ensure_user_exists(self, user_id: UUID, email: str) -> None:
        """Ensure a user record exists in the local database for Keycloak users."""
        from hashlib import sha256

        from src.modules.identity.domain.models import User

        # Check if user already exists by ID
        result = await self._session.execute(select(User).where(User.id == user_id))
        existing = result.scalar_one_or_none()
        if existing:
            return

        # Check if user exists by email_hash
        email_hash = sha256(email.lower().encode()).hexdigest()
        result = await self._session.execute(
            select(User).where(User.email_hash == email_hash)
        )
        existing_by_email = result.scalar_one_or_none()
        if existing_by_email:
            # User exists with same email but different ID
            # Update the user_id to match Keycloak (this shouldn't normally happen)
            # For safety, we'll just update the existing user's ID
            existing_by_email.id = user_id
            self._session.add(existing_by_email)
            await self._session.flush()
            await self._session.commit()
            return

        # Create a placeholder user for the Keycloak user
        user = User(
            id=user_id,
            email_encrypted=email.encode(),  # Simple encoding for Keycloak users
            email_hash=email_hash,
            password_hash="keycloak_managed",  # Placeholder
            status="active",
        )
        self._session.add(user)
        await self._session.flush()
        await self._session.commit()

    async def delete(self, persona_id: UUID) -> None:
        persona = await self.get_by_id(persona_id)
        if persona:
            persona.soft_delete()
            self._session.add(persona)
            await self._session.commit()

    # =============== Experience CRUD ===============

    async def add_experience(self, experience: Experience) -> Experience:
        self._session.add(experience)
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(experience)
        return experience

    async def update_experience(
        self, persona_id: UUID, experience_id: UUID, schema: ExperienceUpdate
    ) -> Experience | None:
        result = await self._session.execute(
            select(Experience).where(
                Experience.id == experience_id,
                Experience.persona_id == persona_id,
            )
        )
        experience = result.scalar_one_or_none()
        if not experience:
            return None

        for field, value in schema.model_dump(exclude_unset=True).items():
            setattr(experience, field, value)

        await self._session.commit()
        await self._session.refresh(experience)
        return experience

    async def delete_experience(self, persona_id: UUID, experience_id: UUID) -> None:
        result = await self._session.execute(
            select(Experience).where(
                Experience.id == experience_id,
                Experience.persona_id == persona_id,
            )
        )
        experience = result.scalar_one_or_none()
        if experience:
            await self._session.delete(experience)
            await self._session.commit()

    # =============== Education CRUD ===============

    async def add_education(self, education: Education) -> Education:
        self._session.add(education)
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(education)
        return education

    async def update_education(
        self, persona_id: UUID, education_id: UUID, schema: EducationUpdate
    ) -> Education | None:
        result = await self._session.execute(
            select(Education).where(
                Education.id == education_id,
                Education.persona_id == persona_id,
            )
        )
        education = result.scalar_one_or_none()
        if not education:
            return None

        for field, value in schema.model_dump(exclude_unset=True).items():
            setattr(education, field, value)

        await self._session.commit()
        await self._session.refresh(education)
        return education

    async def delete_education(self, persona_id: UUID, education_id: UUID) -> None:
        result = await self._session.execute(
            select(Education).where(
                Education.id == education_id,
                Education.persona_id == persona_id,
            )
        )
        education = result.scalar_one_or_none()
        if education:
            await self._session.delete(education)
            await self._session.commit()

    # =============== Skill CRUD ===============

    async def add_skill(self, skill: Skill) -> Skill:
        self._session.add(skill)
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(skill)
        return skill

    async def update_skill(
        self, persona_id: UUID, skill_id: UUID, schema: SkillUpdate
    ) -> Skill | None:
        result = await self._session.execute(
            select(Skill).where(
                Skill.id == skill_id,
                Skill.persona_id == persona_id,
            )
        )
        skill = result.scalar_one_or_none()
        if not skill:
            return None

        for field, value in schema.model_dump(exclude_unset=True).items():
            setattr(skill, field, value)

        await self._session.commit()
        await self._session.refresh(skill)
        return skill

    async def delete_skill(self, persona_id: UUID, skill_id: UUID) -> None:
        result = await self._session.execute(
            select(Skill).where(
                Skill.id == skill_id,
                Skill.persona_id == persona_id,
            )
        )
        skill = result.scalar_one_or_none()
        if skill:
            await self._session.delete(skill)
            await self._session.commit()

    # =============== Career Preference CRUD ===============

    async def get_career_preference(self, persona_id: UUID) -> CareerPreference | None:
        result = await self._session.execute(
            select(CareerPreference).where(CareerPreference.persona_id == persona_id)
        )
        return result.scalar_one_or_none()

    async def update_career_preference(
        self, persona_id: UUID, schema: CareerPreferenceUpdate
    ) -> CareerPreference:
        result = await self._session.execute(
            select(CareerPreference).where(CareerPreference.persona_id == persona_id)
        )
        preference = result.scalar_one_or_none()

        if not preference:
            preference = CareerPreference(persona_id=persona_id)
            self._session.add(preference)

        for field, value in schema.model_dump(exclude_unset=True).items():
            setattr(preference, field, value)

        await self._session.commit()
        await self._session.refresh(preference)
        return preference
