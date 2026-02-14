"""
Admin API routes for system configuration, analytics, and user management.
Restricted to admin users with elevated privileges.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user
from src.core.database.connection import get_db

router = APIRouter()


# ============= Schemas =============


class AIModelConfig(BaseModel):
    """Current AI model configuration."""

    gemini_model: str
    embedding_model: str
    rate_limit_rpm: int
    available_models: list[str]


class UpdateAIModelRequest(BaseModel):
    """Request to update AI model settings."""

    gemini_model: str = Field(
        ...,
        description="Gemini model to use for generation",
    )


class SystemStatus(BaseModel):
    """System-wide status overview."""

    environment: str
    ai_model: str
    features: dict[str, bool]
    total_users: int
    total_applications: int
    agent_sessions_active: int


class PlatformAnalytics(BaseModel):
    """Platform-wide analytics for admin dashboard."""

    total_users: int
    new_users_this_month: int
    users_by_tier: dict[str, int]
    total_applications: int
    applications_this_week: int
    applications_by_status: dict[str, int]
    total_resumes: int
    active_agent_sessions: int


class AdminUserItem(BaseModel):
    """User item for admin user list."""

    id: str
    email: str
    tier: str
    status: str
    created_at: str
    application_count: int


class AdminUserListResponse(BaseModel):
    """Paginated user list response."""

    items: list[AdminUserItem]
    total: int
    page: int
    per_page: int


class UpdateUserRequest(BaseModel):
    """Request to update user properties."""

    tier: str | None = None
    status: str | None = None


class UpdateFeaturesRequest(BaseModel):
    """Request to toggle feature flags."""

    feature_name: str
    enabled: bool


# Known valid Gemini models
VALID_MODELS = [
    "gemini-3.0-flash",
    "gemini-3.0-pro",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-pro",
]


def _require_admin(
    current_user: dict[str, Any],
) -> dict[str, Any]:
    """Check that the current user has admin role."""
    roles = current_user.get("realm_access", {}).get("roles", [])
    if "admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


# ============= AI Config Endpoints =============


@router.get("/ai-config", response_model=AIModelConfig)
async def get_ai_config(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> AIModelConfig:
    """Get current AI model configuration."""
    _require_admin(current_user)

    from src.core.config import settings

    return AIModelConfig(
        gemini_model=settings.ai.GEMINI_MODEL,
        embedding_model=settings.ai.EMBEDDING_MODEL,
        rate_limit_rpm=settings.ai.RATE_LIMIT_RPM,
        available_models=VALID_MODELS,
    )


@router.put("/ai-config", response_model=AIModelConfig)
async def update_ai_config(
    request: UpdateAIModelRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> AIModelConfig:
    """
    Update AI model configuration at runtime.

    Note: This updates the in-memory settings only.
    For persistence across restarts, update the .env file
    or environment variables.
    """
    _require_admin(current_user)

    if request.gemini_model not in VALID_MODELS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid model: {request.gemini_model}. "
                f"Valid: {', '.join(VALID_MODELS)}"
            ),
        )

    from src.core.config import settings

    # Update the runtime settings
    settings.ai.GEMINI_MODEL = request.gemini_model

    return AIModelConfig(
        gemini_model=settings.ai.GEMINI_MODEL,
        embedding_model=settings.ai.EMBEDDING_MODEL,
        rate_limit_rpm=settings.ai.RATE_LIMIT_RPM,
        available_models=VALID_MODELS,
    )


# ============= System Status =============


@router.get("/status", response_model=SystemStatus)
async def get_system_status(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SystemStatus:
    """Get system-wide status for admin dashboard."""
    _require_admin(current_user)

    from sqlalchemy import func, select

    from src.core.config import settings
    from src.modules.applications.models import Application
    from src.modules.identity.domain.models import User

    user_count = await db.execute(select(func.count(User.id)))
    app_count = await db.execute(select(func.count(Application.id)))

    return SystemStatus(
        environment=settings.ENVIRONMENT,
        ai_model=settings.ai.GEMINI_MODEL,
        features={
            "ai_matching": settings.features.ENABLE_AI_MATCHING,
            "resume_parsing": (settings.features.ENABLE_RESUME_PARSING),
            "beta_ui": settings.features.ENABLE_BETA_UI,
        },
        total_users=user_count.scalar() or 0,
        total_applications=app_count.scalar() or 0,
        agent_sessions_active=0,  # TODO: query Redis for active sessions
    )


# ============= Platform Analytics =============


@router.get("/analytics", response_model=PlatformAnalytics)
async def get_platform_analytics(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PlatformAnalytics:
    """Get platform-wide analytics for admin dashboard."""
    _require_admin(current_user)

    from src.modules.applications.models import Application
    from src.modules.identity.domain.models import SubscriptionTier, User
    from src.modules.resume.domain.models import Resume

    # Total users
    user_count_result = await db.execute(select(func.count(User.id)))
    total_users = user_count_result.scalar() or 0

    # New users this month
    month_start = datetime.now(timezone.utc).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    new_users_result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= month_start)
    )
    new_users_this_month = new_users_result.scalar() or 0

    # Users by tier
    tier_results = await db.execute(
        select(User.tier, func.count(User.id)).group_by(User.tier)
    )
    users_by_tier = {}
    for tier, count in tier_results.all():
        tier_name = tier.value if isinstance(tier, SubscriptionTier) else str(tier)
        users_by_tier[tier_name] = count

    # Total applications
    app_count_result = await db.execute(select(func.count(Application.id)))
    total_applications = app_count_result.scalar() or 0

    # Applications this week (last 7 days)
    from datetime import timedelta

    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    weekly_apps_result = await db.execute(
        select(func.count(Application.id)).where(Application.created_at >= week_ago)
    )
    applications_this_week = weekly_apps_result.scalar() or 0

    # Applications by status
    status_results = await db.execute(
        select(Application.status, func.count(Application.id)).group_by(
            Application.status
        )
    )
    applications_by_status = {}
    for app_status, count in status_results.all():
        status_name = (
            app_status.value if hasattr(app_status, "value") else str(app_status)
        )
        applications_by_status[status_name] = count

    # Total resumes
    total_resumes = 0
    try:
        resume_count_result = await db.execute(select(func.count(Resume.id)))
        total_resumes = resume_count_result.scalar() or 0
    except Exception:
        pass  # Resume table might not exist yet

    return PlatformAnalytics(
        total_users=total_users,
        new_users_this_month=new_users_this_month,
        users_by_tier=users_by_tier,
        total_applications=total_applications,
        applications_this_week=applications_this_week,
        applications_by_status=applications_by_status,
        total_resumes=total_resumes,
        active_agent_sessions=0,
    )


# ============= User Management =============


@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    tier: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = None,
) -> AdminUserListResponse:
    """List all users with filtering and pagination."""
    _require_admin(current_user)

    from src.modules.applications.models import Application
    from src.modules.identity.domain.models import SubscriptionTier, User

    query = select(User)

    # Filter by tier
    if tier:
        try:
            tier_enum = SubscriptionTier(tier.lower())
            query = query.where(User.tier == tier_enum)
        except ValueError:
            pass

    # Filter by status
    if status_filter:
        query = query.where(User.status == status_filter)

    # Count total before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page).order_by(User.created_at.desc())

    result = await db.execute(query)
    users = result.scalars().all()

    # Get application counts per user
    items = []
    for user in users:
        app_count_result = await db.execute(
            select(func.count(Application.id)).where(Application.user_id == user.id)
        )
        app_count = app_count_result.scalar() or 0

        try:
            email = user.email
        except Exception:
            email = "<encrypted>"

        items.append(
            AdminUserItem(
                id=str(user.id),
                email=email,
                tier=user.tier.value
                if isinstance(user.tier, SubscriptionTier)
                else str(user.tier),
                status=user.status or "active",
                created_at=user.created_at.isoformat() if user.created_at else "",
                application_count=app_count,
            )
        )

    return AdminUserListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.patch("/users/{user_id}")
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Update user tier or status (admin only)."""
    _require_admin(current_user)

    from src.modules.identity.domain.models import SubscriptionTier, User

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if request.tier:
        try:
            user.tier = SubscriptionTier(request.tier.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid tier: {request.tier}. Valid: {[t.value for t in SubscriptionTier]}",
            )

    if request.status:
        if request.status not in ("active", "suspended", "banned"):
            raise HTTPException(
                status_code=400,
                detail="Invalid status. Valid: active, suspended, banned",
            )
        user.status = request.status

    await db.commit()
    return {"message": f"User {user_id} updated successfully"}


# ============= Feature Flags =============


@router.patch("/features")
async def update_feature(
    request: UpdateFeaturesRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Toggle a feature flag at runtime."""
    _require_admin(current_user)

    from src.core.config import settings

    feature_map = {
        "ai_matching": "ENABLE_AI_MATCHING",
        "resume_parsing": "ENABLE_RESUME_PARSING",
        "beta_ui": "ENABLE_BETA_UI",
    }

    attr_name = feature_map.get(request.feature_name)
    if not attr_name:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown feature: {request.feature_name}. Valid: {list(feature_map.keys())}",
        )

    setattr(settings.features, attr_name, request.enabled)

    return {
        "feature": request.feature_name,
        "enabled": request.enabled,
        "message": f"Feature '{request.feature_name}' {'enabled' if request.enabled else 'disabled'}",
    }
