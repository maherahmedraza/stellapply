from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.modules.profile.models import UserProfile
from src.modules.profile.schemas import UserProfileResponse


async def get_user_profile_schema(
    db: AsyncSession, user_id: UUID
) -> UserProfileResponse | None:
    """
    Fetch UserProfile model and convert to UserProfileResponse schema.
    """
    # Fetch from DB
    stmt = select(UserProfile).where(UserProfile.user_id == user_id)
    result = await db.execute(stmt)
    profile_model = result.scalars().first()

    if not profile_model:
        return None

    try:
        return UserProfileResponse.model_validate(profile_model)
    except Exception:
        # Fallback if direct validation fails
        return None
