import logging
import uuid
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from src.modules.profile.models import UserProfile
from src.modules.profile.schemas import (
    UserProfileUpdate,
    ProfileCompletenessResponse,
)

logger = logging.getLogger(__name__)


class ProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserProfile:
        """
        Fetch the user's profile. Creates a default empty profile if none exists.
        """
        query = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await self.db.execute(query)
        profile = result.scalars().first()

        if not profile:
            # Create default profile
            profile = UserProfile(
                user_id=user_id,
                personal_info="{}",
                search_preferences={},
                agent_rules={},
                application_answers="{}",
                resume_strategy={},
            )
            self.db.add(profile)
            await self.db.commit()
            await self.db.refresh(profile)

        return profile

    async def update_profile(
        self, user_id: uuid.UUID, data: UserProfileUpdate
    ) -> UserProfile:
        """
        Update parts of the profile.
        """
        profile = await self.get_by_user_id(user_id)

        if data.personal_info:
            profile.personal_info = data.personal_info.model_dump_json()

        if data.search_preferences:
            profile.search_preferences = data.search_preferences.model_dump()

        if data.agent_rules:
            profile.agent_rules = data.agent_rules.model_dump()

        if data.application_answers:
            profile.application_answers = data.application_answers.model_dump_json()

        if data.resume_strategy:
            profile.resume_strategy = data.resume_strategy.model_dump()

        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def get_completeness(self, user_id: uuid.UUID) -> ProfileCompletenessResponse:
        """
        Calculate profile completeness score.
        """
        profile = await self.get_by_user_id(user_id)

        # Load data. Encrypted fields are auto-decrypted to string by type decorator.
        personal_info = (
            json.loads(profile.personal_info) if profile.personal_info else {}
        )
        search_prefs = profile.search_preferences
        # rules = profile.agent_rules # Unused check
        answers = (
            json.loads(profile.application_answers)
            if profile.application_answers
            else {}
        )

        scores = {}
        missing = []

        # Personal Info (40%)
        # Critical: first_name, last_name, email
        pi_score = 0
        pi_total = 3
        if personal_info.get("first_name"):
            pi_score += 1
        else:
            missing.append("personal_info.first_name")
        if personal_info.get("last_name"):
            pi_score += 1
        else:
            missing.append("personal_info.last_name")
        if personal_info.get("email"):
            pi_score += 1
        else:
            missing.append("personal_info.email")
        scores["personal_info"] = (pi_score / pi_total) * 100

        # Search Prefs (30%)
        # Critical: target_roles, locations
        sp_score = 0
        sp_total = 2
        if search_prefs.get("target_roles"):
            sp_score += 1
        else:
            missing.append("search_preferences.target_roles")
        if search_prefs.get("locations"):
            sp_score += 1
        else:
            missing.append("search_preferences.locations")
        scores["search_preferences"] = (sp_score / sp_total) * 100

        # Agent Rules (10%)
        scores["agent_rules"] = 100.0

        # Application Answers (20%)
        aa_score = 0
        aa_total = 1
        if answers.get("why_interested_template"):
            aa_score += 1
        else:
            missing.append("application_answers.why_interested_template")
        scores["application_answers"] = (aa_score / aa_total) * 100

        # Weighted Total
        overall = (
            (scores["personal_info"] * 0.4)
            + (scores["search_preferences"] * 0.3)
            + (scores["agent_rules"] * 0.1)
            + (scores["application_answers"] * 0.2)
        )

        return ProfileCompletenessResponse(
            overall=round(overall, 1), sections=scores, missing_fields=missing
        )
