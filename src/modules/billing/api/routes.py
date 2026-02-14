from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user
from src.core.database.connection import get_db
from src.modules.applications.models import Application
from src.modules.billing.domain.models import UsageRecord
from src.modules.identity.domain.models import SubscriptionTier, User

router = APIRouter()


# ============= Schemas =============


class SubscriptionInfo(BaseModel):
    tier: str
    tier_display: str
    price_monthly: float
    next_billing_date: str | None
    features: list[str]


class PlanInfo(BaseModel):
    tier: str
    name: str
    price_monthly: float
    features: list[str]
    is_current: bool
    app_limit: int | None  # None = unlimited


class UsageInfo(BaseModel):
    """Current billing period usage."""

    billing_period: str  # e.g. "2026-02"
    applications_submitted: int
    agent_applications: int
    manual_applications: int
    application_limit: int | None  # None = unlimited
    resumes_generated: int
    cover_letters_generated: int
    ai_calls_made: int


class Invoice(BaseModel):
    id: str
    date: str
    amount: float
    status: str


class BillingResponse(BaseModel):
    current_plan: SubscriptionInfo
    available_plans: list[PlanInfo]
    usage: UsageInfo
    invoices: list[Invoice]
    payment_method: dict | None


class ChangePlanRequest(BaseModel):
    new_tier: str


# Plan definitions — application limits enforce the vision
PLANS = {
    "free": {
        "name": "Free",
        "price": 0.0,
        "app_limit": 5,
        "features": [
            "5 job applications per month",
            "Basic resume builder",
            "Job matching (limited)",
            "Email support",
        ],
    },
    "plus": {
        "name": "Plus",
        "price": 9.99,
        "app_limit": 50,
        "features": [
            "50 job applications per month",
            "Advanced resume builder",
            "AI-powered job matching",
            "AI cover letter generation",
            "Application tracking",
            "Priority email support",
        ],
    },
    "pro": {
        "name": "Pro",
        "price": 19.99,
        "app_limit": None,  # Unlimited
        "features": [
            "Unlimited job applications",
            "Auto-apply to matching jobs",
            "Multiple resume versions",
            "Advanced AI insights",
            "Truth-grounded resume enhancement",
            "Salary negotiation tips",
            "24/7 priority support",
        ],
    },
}


def get_user_id_from_token(current_user: dict[str, Any]) -> UUID:
    user_id_str = current_user.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )
    return UUID(user_id_str)


def _current_billing_period() -> str:
    """Return the current billing period as YYYY-MM."""
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m")


async def _get_usage(db: AsyncSession, user_id: UUID) -> UsageInfo:
    """Get real usage data for the current billing period."""
    period = _current_billing_period()

    # Try to load the UsageRecord for this period
    result = await db.execute(
        select(UsageRecord).where(
            UsageRecord.user_id == user_id,
            UsageRecord.billing_period == period,
        )
    )
    record = result.scalar_one_or_none()

    # Also count actual applications this month as ground truth
    month_start = datetime.now(timezone.utc).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    app_count_result = await db.execute(
        select(func.count(Application.id)).where(
            Application.user_id == user_id,
            Application.created_at >= month_start,
        )
    )
    actual_app_count = app_count_result.scalar() or 0

    agent_count_result = await db.execute(
        select(func.count(Application.id)).where(
            Application.user_id == user_id,
            Application.created_at >= month_start,
            Application.is_agent_applied.is_(True),
        )
    )
    actual_agent_count = agent_count_result.scalar() or 0

    # Load user tier for limit
    user_result = await db.execute(select(User.tier).where(User.id == user_id))
    tier = user_result.scalar() or SubscriptionTier.FREE
    tier_key = tier.value if hasattr(tier, "value") else str(tier)
    plan = PLANS.get(tier_key, PLANS["free"])

    return UsageInfo(
        billing_period=period,
        applications_submitted=actual_app_count,
        agent_applications=actual_agent_count,
        manual_applications=actual_app_count - actual_agent_count,
        application_limit=plan["app_limit"],
        resumes_generated=(record.resumes_generated if record else 0),
        cover_letters_generated=(record.cover_letters_generated if record else 0),
        ai_calls_made=record.ai_calls_made if record else 0,
    )


@router.get("/", response_model=BillingResponse)
async def get_billing_info(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BillingResponse:
    """Get billing information for current user."""
    user_id = get_user_id_from_token(current_user)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_tier = user.tier.value if user.tier else "free"
    plan_info = PLANS.get(current_tier, PLANS["free"])

    # Build current plan info
    current_plan = SubscriptionInfo(
        tier=current_tier,
        tier_display=plan_info["name"],
        price_monthly=plan_info["price"],
        next_billing_date=None,  # TODO: populate from Stripe
        features=plan_info["features"],
    )

    # Build available plans
    available_plans = [
        PlanInfo(
            tier=tier,
            name=info["name"],
            price_monthly=info["price"],
            features=info["features"],
            is_current=(tier == current_tier),
            app_limit=info["app_limit"],
        )
        for tier, info in PLANS.items()
    ]

    # Get real usage data
    usage = await _get_usage(db, user_id)

    # TODO: fetch real invoices from Stripe
    invoices: list[Invoice] = []

    return BillingResponse(
        current_plan=current_plan,
        available_plans=available_plans,
        usage=usage,
        invoices=invoices,
        payment_method=None,  # TODO: from Stripe
    )


@router.get("/usage", response_model=UsageInfo)
async def get_usage(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UsageInfo:
    """Get current billing period usage for the user."""
    user_id = get_user_id_from_token(current_user)
    return await _get_usage(db, user_id)


@router.post("/change-plan")
async def change_plan(
    request: ChangePlanRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Change subscription plan."""
    # TODO: integrate with Stripe for payment processing
    user_id = get_user_id_from_token(current_user)

    new_tier = request.new_tier.lower()
    if new_tier not in PLANS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid plan: {new_tier}",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user tier
    user.tier = SubscriptionTier(new_tier)
    await db.commit()

    return {
        "success": True,
        "message": f"Plan changed to {PLANS[new_tier]['name']}",
        "new_tier": new_tier,
    }


@router.post("/cancel")
async def cancel_subscription(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Cancel subscription (downgrade to free)."""
    # TODO: integrate with Stripe for cancellation
    user_id = get_user_id_from_token(current_user)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.tier = SubscriptionTier.FREE
    await db.commit()

    return {
        "success": True,
        "message": ("Subscription cancelled. You are now on the Free plan."),
    }
