import json
import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user
from src.core.database.connection import get_db
from src.modules.profile.schemas import (
    AgentRulesSchema,
    ApplicationAnswersSchema,
    CertificationSchema,
    EducationSchema,
    ExperienceSchema,
    FullProfile,
    LanguageSchema,
    PersonalInfoSchema,
    ProfileCompletenessReport,
    ResumeStrategySchema,
    SearchPreferencesSchema,
    UserProfileResponse,
    UserProfileUpdate,
)
from src.modules.profile.service import ProfileService

router = APIRouter()


async def get_service(db: AsyncSession = Depends(get_db)) -> ProfileService:
    return ProfileService(db)


@router.get("/", response_model=UserProfileResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_service),
) -> Any:
    """
    Get the full user profile.
    """
    user_id = uuid.UUID(current_user["sub"])
    profile = await service.get_by_user_id(user_id)

    # Helper to parse JSON fields safely
    def parse(val, schema, is_list=False):
        if not val:
            return [] if is_list else None
        try:
            data = json.loads(val) if isinstance(val, str) else val
            if is_list:
                return [schema(**item) for item in data]
            return schema(**data)
        except Exception:
            return [] if is_list else None  # Fallback

    return UserProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        personal_info=parse(profile.personal_info, PersonalInfoSchema)
        or PersonalInfoSchema(first_name="", last_name="", email=""),
        search_preferences=SearchPreferencesSchema(
            **(profile.search_preferences or {})
        ),
        agent_rules=AgentRulesSchema(**(profile.agent_rules or {})),
        application_answers=parse(profile.application_answers, ApplicationAnswersSchema)
        or ApplicationAnswersSchema(),
        resume_strategy=ResumeStrategySchema(**(profile.resume_strategy or {})),
        # New sections
        experience=parse(profile.experience, ExperienceSchema, is_list=True),
        education=parse(profile.education, EducationSchema, is_list=True),
        skills=parse(profile.skills, str, is_list=False)
        or [],  # skills is list[str] already or json list
        languages=parse(profile.languages, LanguageSchema, is_list=True),
        certifications=parse(profile.certifications, CertificationSchema, is_list=True),
        created_at=profile.created_at.date(),  # Convert to date as per schema
        updated_at=profile.updated_at.date(),
    )


@router.put("/", response_model=UserProfileResponse)
async def update_profile_full(
    update_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_service),
) -> Any:
    """
    Update entire profile or parts of it via PUT/PATCH logic (using UserProfileUpdate).
    """
    user_id = uuid.UUID(current_user["sub"])
    await service.update_profile(user_id, update_data)
    return await get_profile(current_user, service)


@router.patch("/personal-info", response_model=UserProfileResponse)
async def update_personal_info(
    data: PersonalInfoSchema,
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_service),
) -> Any:
    user_id = uuid.UUID(current_user["sub"])
    await service.update_profile(user_id, UserProfileUpdate(personal_info=data))
    return await get_profile(current_user, service)


@router.patch("/experience", response_model=UserProfileResponse)
async def update_experience(
    data: list[ExperienceSchema],
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_service),
) -> Any:
    user_id = uuid.UUID(current_user["sub"])
    await service.update_profile(user_id, UserProfileUpdate(experience=data))
    return await get_profile(current_user, service)


@router.patch("/education", response_model=UserProfileResponse)
async def update_education(
    data: list[EducationSchema],
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_service),
) -> Any:
    user_id = uuid.UUID(current_user["sub"])
    await service.update_profile(user_id, UserProfileUpdate(education=data))
    return await get_profile(current_user, service)


@router.patch("/skills", response_model=UserProfileResponse)
async def update_skills(
    data: list[str],
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_service),
) -> Any:
    user_id = uuid.UUID(current_user["sub"])
    await service.update_profile(user_id, UserProfileUpdate(skills=data))
    return await get_profile(current_user, service)


@router.patch("/search-preferences", response_model=UserProfileResponse)
async def update_search_preferences(
    data: SearchPreferencesSchema,
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_service),
) -> Any:
    user_id = uuid.UUID(current_user["sub"])
    await service.update_profile(user_id, UserProfileUpdate(search_preferences=data))
    return await get_profile(current_user, service)


@router.patch("/agent-rules", response_model=UserProfileResponse)
async def update_agent_rules(
    data: AgentRulesSchema,
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_service),
) -> Any:
    user_id = uuid.UUID(current_user["sub"])
    await service.update_profile(user_id, UserProfileUpdate(agent_rules=data))
    return await get_profile(current_user, service)


@router.patch("/answers", response_model=UserProfileResponse)
async def update_answers(
    data: ApplicationAnswersSchema,
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_service),
) -> Any:
    user_id = uuid.UUID(current_user["sub"])
    await service.update_profile(user_id, UserProfileUpdate(application_answers=data))
    return await get_profile(current_user, service)


@router.get("/completeness", response_model=ProfileCompletenessReport)
async def get_completeness(
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_service),
) -> Any:
    user_id = uuid.UUID(current_user["sub"])
    return await service.get_completeness(user_id)


@router.post("/import-resume", response_model=FullProfile)
async def import_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_service),
) -> Any:
    """
    Extract profile data from uploaded resume.
    """
    content = await file.read()
    content_type = file.content_type or "application/octet-stream"

    try:
        extracted_profile = await service.import_resume(content, content_type)
        return extracted_profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume extraction failed: {str(e)}",
        )
