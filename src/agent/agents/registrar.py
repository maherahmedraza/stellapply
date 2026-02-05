from typing import Any, Dict

from src.agent.agents.base import BaseAgent


class RegistrarAgent(BaseAgent):
    """
    Agent responsible for registering on job portals.
    """

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute portal registration.
        Payload expected: {
            "portal_url": "...",
            "credentials": {"email": "...", "password": "..."}
        }
        """
        await self.start()
        try:
            url = payload.get("portal_url")
            creds = payload.get("credentials", {})

            await self.browser.navigate(url)

            goal = f"Register or Sign Up on this portal using email '{creds.get('email')}' and the provided password."

            # In a real scenario, we might want to mask the password in logs/prompts
            # but provide it via value injection.

            result = await self.autonomous_loop(goal, max_steps=10)
            return result

        finally:
            await self.stop()
