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

            # We inject persona data into the prompt context via the autonomous loop's brain call needs.
            # Currently BaseAgent.autonomous_loop calls brain.decide_next_action which primarily takes page context.
            # We should enhance BaseAgent or override autonomous_loop to include persona data in the prompt.
            # For this MVP, we will assume the Brain can "see" the persona data if we pass it in the task description
            # or if we subclass the autonomous loop.

            # Let's verify if we need to enhance the BaseAgent's separate brain method...
            # The BaseAgent calls `self.brain.decide_next_action(goal, ...)`
            # We can bake the persona data into the `goal` string for the Brain to know what values to use.

            persona_summary = str(payload.get("persona_data", {}))
            enhanced_goal = f"{apply_goal} Use this data: {persona_summary}"

            result = await self.autonomous_loop(enhanced_goal, max_steps=15)

            return result

        finally:
            await self.stop()
