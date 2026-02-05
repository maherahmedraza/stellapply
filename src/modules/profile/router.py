from typing import Any
import uuid
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user
from src.core.database.connection import get_db
from src.modules.profile.schemas import (
    UserProfileResponse,
    UserProfileUpdate,
    ProfileCompletenessResponse,
    PersonalInfoSchema,
    SearchPreferencesSchema,
    AgentRulesSchema,
    ApplicationAnswersSchema,
    ResumeStrategySchema,
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

    # We need to manually construct response because database fields are strings (JSON)
    # but schema expects objects. Pydantic from_attributes works if attributes match schema.
    # But profile.personal_info is a string (encrypted/decrypted), schema wants PersonalInfoSchema.

    # helper to parse if string
    def safe_load(val, schema):
        if isinstance(val, str):
            try:
                data = json.loads(val)
                return schema(**data)
            except Exception:
                return None  # Or default
        return schema(**val) if isinstance(val, dict) else None

    # We manually map to ensure types align
    # This is a bit verbose but necessary due to the EncryptedString abstraction mapping to Pydantic models

    return UserProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        personal_info=safe_load(profile.personal_info, PersonalInfoSchema)
        or PersonalInfoSchema(first_name="", last_name="", email=""),
        search_preferences=SearchPreferencesSchema(**profile.search_preferences),
        agent_rules=AgentRulesSchema(**profile.agent_rules),
        application_answers=safe_load(
            profile.application_answers, ApplicationAnswersSchema
        )
        or ApplicationAnswersSchema(),
        resume_strategy=ResumeStrategySchema(**profile.resume_strategy),
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.patch("/", response_model=UserProfileResponse)
async def update_profile(
    update_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_service),
) -> Any:
    """
    Update parts of the profile.
    """
    user_id = uuid.UUID(current_user["sub"])
    updated_profile = await service.update_profile(user_id, update_data)

    # Recursive call to get_profile to piggyback on response formatting logic?
    # Or duplication of formatting. Let's redirect logic internally.
    return await get_profile(current_user, service)


@router.get("/completeness", response_model=ProfileCompletenessResponse)
async def get_completeness(
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_service),
) -> Any:
    """
    Get profile completeness score.
    """
    user_id = uuid.UUID(current_user["sub"])
    return await service.get_completeness(user_id)
