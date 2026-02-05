from typing import Any, Dict

from src.agent.agents.base import BaseAgent


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
            import json

            profile_str = json.dumps(profile_data, indent=2)

            enhanced_goal = (
                f"{apply_goal}\n\n"
                f"USER PROFILE DATA:\n"
                f"{profile_str}\n\n"
                "INSTRUCTIONS: Use the above profile data to fill out the form. "
                "If a field matches a profile attribute, use that value. "
                "For open-ended questions, use the 'application_answers' or 'personal_info'."
            )

            result = await self.autonomous_loop(enhanced_goal, max_steps=20)

            return result

        finally:
            await self.stop()
