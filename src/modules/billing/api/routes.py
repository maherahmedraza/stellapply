from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user
from src.core.database.connection import get_db
from src.modules.identity.domain.models import User, SubscriptionTier

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


class Invoice(BaseModel):
    id: str
    date: str
    amount: float
    status: str


class BillingResponse(BaseModel):
    current_plan: SubscriptionInfo
    available_plans: list[PlanInfo]
    invoices: list[Invoice]
    payment_method: dict | None


class ChangePlanRequest(BaseModel):
    new_tier: str


# Plan definitions
PLANS = {
    "free": {
        "name": "Free",
        "price": 0.0,
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
        "features": [
            "Unlimited job applications",
            "Auto-apply to matching jobs",
            "Multiple resume versions",
            "Advanced AI insights",
            "Interview preparation",
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


@router.get("/", response_model=BillingResponse)
async def get_billing_info(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BillingResponse:
    """Get billing information for current user"""
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
        next_billing_date="2026-02-15" if current_tier != "free" else None,
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
        )
        for tier, info in PLANS.items()
    ]

    # Mock invoices (in real app, would come from payment provider like Stripe)
    invoices = []
    if current_tier != "free":
        invoices = [
            Invoice(
                id="INV-001",
                date="2026-01-15",
                amount=plan_info["price"],
                status="paid",
            ),
            Invoice(
                id="INV-002",
                date="2025-12-15",
                amount=plan_info["price"],
                status="paid",
            ),
        ]

    return BillingResponse(
        current_plan=current_plan,
        available_plans=available_plans,
        invoices=invoices,
        payment_method={"type": "visa", "last4": "4242", "expiry": "12/2027"}
        if current_tier != "free"
        else None,
    )


@router.post("/change-plan")
async def change_plan(
    request: ChangePlanRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Change subscription plan (mock - in real app would integrate with Stripe)"""
    user_id = get_user_id_from_token(current_user)

    new_tier = request.new_tier.lower()
    if new_tier not in PLANS:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {new_tier}")

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
    """Cancel subscription (downgrade to free)"""
    user_id = get_user_id_from_token(current_user)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.tier = SubscriptionTier.FREE
    await db.commit()

    return {
        "success": True,
        "message": "Subscription cancelled. You are now on the Free plan.",
    }
