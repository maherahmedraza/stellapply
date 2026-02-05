from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user
from src.core.database.connection import get_db
from src.modules.persona.api.schemas import (
    PersonaResponse,
    PersonaUpdate,
    ExperienceCreate,
    ExperienceUpdate,
    ExperienceRead,
    EducationCreate,
    EducationUpdate,
    EducationRead,
    SkillCreate,
    SkillUpdate,
    SkillRead,
    CareerPreferenceUpdate,
    CareerPreferenceRead,
)
from src.modules.persona.domain.services import PersonaService
from src.modules.persona.infrastructure.repository import SQLAlchemyPersonaRepository

router = APIRouter()


async def get_persona_service(
    db: AsyncSession = Depends(get_db),
) -> PersonaService:
    repository = SQLAlchemyPersonaRepository(db)
    return PersonaService(repository)


def get_user_id_from_token(current_user: dict[str, Any]) -> UUID:
    user_id_str = current_user.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )
    return UUID(user_id_str)


# =============== Persona Endpoints ===============


@router.get("/me", response_model=PersonaResponse)
async def get_my_persona(
    current_user: dict[str, Any] = Depends(get_current_user),
    service: PersonaService = Depends(get_persona_service),
) -> PersonaResponse:
    user_id = get_user_id_from_token(current_user)
    persona = await service.get_persona_by_user_id(user_id)
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found"
        )
    return PersonaResponse.model_validate(persona)


@router.patch("/me", response_model=PersonaResponse)
async def update_my_persona(
    schema: PersonaUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: PersonaService = Depends(get_persona_service),
) -> PersonaResponse:
    user_id = get_user_id_from_token(current_user)
    persona = await service.update_persona(user_id, schema)
    return PersonaResponse.model_validate(persona)


# =============== Experience Endpoints ===============


@router.post(
    "/me/experiences",
    response_model=ExperienceRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_experience(
    schema: ExperienceCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: PersonaService = Depends(get_persona_service),
) -> ExperienceRead:
    user_id = get_user_id_from_token(current_user)
    experience = await service.add_experience(user_id, schema)
    return ExperienceRead.model_validate(experience)


@router.patch("/me/experiences/{experience_id}", response_model=ExperienceRead)
async def update_experience(
    experience_id: UUID,
    schema: ExperienceUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: PersonaService = Depends(get_persona_service),
) -> ExperienceRead:
    user_id = get_user_id_from_token(current_user)
    experience = await service.update_experience(user_id, experience_id, schema)
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found"
        )
    return ExperienceRead.model_validate(experience)


@router.delete(
    "/me/experiences/{experience_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_experience(
    experience_id: UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: PersonaService = Depends(get_persona_service),
) -> None:
    user_id = get_user_id_from_token(current_user)
    await service.delete_experience(user_id, experience_id)


# =============== Education Endpoints ===============


@router.post(
    "/me/educations", response_model=EducationRead, status_code=status.HTTP_201_CREATED
)
async def add_education(
    schema: EducationCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: PersonaService = Depends(get_persona_service),
) -> EducationRead:
    user_id = get_user_id_from_token(current_user)
    education = await service.add_education(user_id, schema)
    return EducationRead.model_validate(education)


@router.patch("/me/educations/{education_id}", response_model=EducationRead)
async def update_education(
    education_id: UUID,
    schema: EducationUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: PersonaService = Depends(get_persona_service),
) -> EducationRead:
    user_id = get_user_id_from_token(current_user)
    education = await service.update_education(user_id, education_id, schema)
    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Education not found"
        )
    return EducationRead.model_validate(education)


@router.delete("/me/educations/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(
    education_id: UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: PersonaService = Depends(get_persona_service),
) -> None:
    user_id = get_user_id_from_token(current_user)
    await service.delete_education(user_id, education_id)


# =============== Skills Endpoints ===============


@router.post(
    "/me/skills", response_model=SkillRead, status_code=status.HTTP_201_CREATED
)
async def add_skill(
    schema: SkillCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: PersonaService = Depends(get_persona_service),
) -> SkillRead:
    user_id = get_user_id_from_token(current_user)
    skill = await service.add_skill(user_id, schema)
    return SkillRead.model_validate(skill)


@router.patch("/me/skills/{skill_id}", response_model=SkillRead)
async def update_skill(
    skill_id: UUID,
    schema: SkillUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: PersonaService = Depends(get_persona_service),
) -> SkillRead:
    user_id = get_user_id_from_token(current_user)
    skill = await service.update_skill(user_id, skill_id, schema)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found"
        )
    return SkillRead.model_validate(skill)


@router.delete("/me/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: PersonaService = Depends(get_persona_service),
) -> None:
    user_id = get_user_id_from_token(current_user)
    await service.delete_skill(user_id, skill_id)


# =============== Career Preference Endpoints ===============


@router.get("/me/career-preference", response_model=CareerPreferenceRead | None)
async def get_career_preference(
    current_user: dict[str, Any] = Depends(get_current_user),
    service: PersonaService = Depends(get_persona_service),
) -> CareerPreferenceRead | None:
    user_id = get_user_id_from_token(current_user)
    preference = await service.get_career_preference(user_id)
    if not preference:
        return None
    return CareerPreferenceRead.model_validate(preference)


@router.patch("/me/career-preference", response_model=CareerPreferenceRead)
async def update_career_preference(
    schema: CareerPreferenceUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: PersonaService = Depends(get_persona_service),
) -> CareerPreferenceRead:
    user_id = get_user_id_from_token(current_user)
    preference = await service.update_career_preference(user_id, schema)
    return CareerPreferenceRead.model_validate(preference)
