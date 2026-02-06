from typing import Any, Dict

from src.agent.agents.base import BaseAgent
from src.modules.profile.schemas import UserProfileResponse


class RegistrarAgent(BaseAgent):
    """
    Agent responsible for registering on job portals.
    """

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute portal registration.
        Payload expected: {
            "portal_url": "...",
            "credentials": {"email": "...", "password": "..."},
            "profile": UserProfileResponse
        }
        """
        await self.start()
        try:
            url = payload.get("portal_url")
            creds = payload.get("credentials", {})
            profile_data = payload.get("profile")

            # Validate/Create Profile Object
            if isinstance(profile_data, dict):
                try:
                    profile = UserProfileResponse(**profile_data)
                except Exception:
                    profile = UserProfileResponse.model_validate(profile_data)
            else:
                profile = profile_data

            await self.browser.navigate(url)

            goal = (
                f"Register or Sign Up on this portal using email '{creds.get('email')}' "
                f"and password '{creds.get('password')}'. "
                f"If asked for name use {profile.personal_info.first_name} {profile.personal_info.last_name}."
            )

            # In a real scenario, we might want to mask the password in logs/prompts
            # but provide it via value injection in the prompt if necessary.

            result = await self.autonomous_loop(goal, profile=profile, max_steps=15)

            # TODO: Verify registration success via screenshot or text check

            return result
        except Exception as e:
            return {"status": "failed", "error": str(e)}
        finally:
            await self.stop()
