from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user
from src.core.database.connection import get_db
from src.modules.identity.domain.models import User, UserSettings

router = APIRouter()


# ============= Schemas =============


class UserSettingsResponse(BaseModel):
    theme: str
    language: str
    timezone: str
    date_format: str
    email_notifications: bool
    push_notifications: bool
    sms_notifications: bool
    job_alerts: bool
    weekly_digest: bool
    quiet_hours_start: str | None
    quiet_hours_end: str | None
    match_threshold: int
    preferred_work_type: str
    salary_visible: bool
    auto_apply_enabled: bool
    auto_apply_limit: int
    auto_apply_min_match: int

    class Config:
        from_attributes = True


class UserSettingsUpdate(BaseModel):
    theme: str | None = None
    language: str | None = None
    timezone: str | None = None
    date_format: str | None = None
    email_notifications: bool | None = None
    push_notifications: bool | None = None
    sms_notifications: bool | None = None
    job_alerts: bool | None = None
    weekly_digest: bool | None = None
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None
    match_threshold: int | None = None
    preferred_work_type: str | None = None
    salary_visible: bool | None = None
    auto_apply_enabled: bool | None = None
    auto_apply_limit: int | None = None
    auto_apply_min_match: int | None = None


def get_user_id_from_token(current_user: dict[str, Any]) -> UUID:
    user_id_str = current_user.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )
    return UUID(user_id_str)


@router.get("/me", response_model=UserSettingsResponse)
async def get_my_settings(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserSettingsResponse:
    """Get current user's settings"""
    user_id = get_user_id_from_token(current_user)

    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    settings = result.scalar_one_or_none()

    if not settings:
        # Create default settings if they don't exist
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)

    return UserSettingsResponse.model_validate(settings)


@router.patch("/me", response_model=UserSettingsResponse)
async def update_my_settings(
    updates: UserSettingsUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserSettingsResponse:
    """Update current user's settings"""
    user_id = get_user_id_from_token(current_user)

    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    settings = result.scalar_one_or_none()

    if not settings:
        # Create settings if they don't exist
        settings = UserSettings(user_id=user_id)
        db.add(settings)

    # Apply updates
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)

    await db.commit()
    await db.refresh(settings)

    return UserSettingsResponse.model_validate(settings)
