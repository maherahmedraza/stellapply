import logging
from typing import Any, Dict

from src.agent.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class ApplicantAgent(BaseAgent):
    """
    Agent responsible for submitting job applications.
    """

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute job application.
        Payload expected: {
            "job_url": "...",
            "persona_data": {...},
            "answers": {...}
        }
        """
        await self.start()
        try:
            job_url = payload.get("job_url")

            # Initial navigation
            await self.browser.navigate(job_url)

            # Goal: Apply for the job
            # The autonomous loop will handle finding the "Apply" button,
            # filling forms (using Brain to map persona data to fields),
            # and submitting.

            # Note: For complex forms, we might need a dedicated FormFiller helper
            # that the agent delegates to, or the prompt in autonomous_loop needs to be robust.

            apply_goal = "Find the apply button, fill out the application form with the provided persona data, and submit."

            # We inject profile data into the prompt context via the goal description.
            # The Brain uses this to decide what values to type into fields.

            profile_data = payload.get("profile_data", {})
            # Fallback to legacy persona_data if profile_data is empty
            if not profile_data:
                profile_data = payload.get("persona_data", {})

            # Format profile data for the prompt
            from src.modules.profile.schemas import (
                UserProfileResponse,
                PersonalInfoSchema,
                SearchPreferencesSchema,
                AgentRulesSchema,
                ApplicationAnswersSchema,
                ResumeStrategySchema,
            )

            if isinstance(profile_data, dict):
                try:
                    # Validate and create strict UserProfileResponse
                    # We assume the payload matches the schema structure
                    user_profile = UserProfileResponse.model_validate(profile_data)
                except Exception as e:
                    logger.warning(
                        f"Failed to validate profile data strict: {e}. Attempting construct."
                    )
                    # Fallback construction if strict validation fails (e.g. extra fields)
                    # Or re-raise if critical.
                    # For now, let's try to construct it manually or re-raise
                    raise e
            else:
                user_profile = profile_data

            result = await self.autonomous_loop(
                apply_goal, profile=user_profile, max_steps=20
            )

            return result

        finally:
            await self.stop()
