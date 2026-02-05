from typing import Any, Dict

from src.agent.agents.base import BaseAgent


class ScoutAgent(BaseAgent):
    """
    Agent responsible for discovering jobs on a specific portal.
    """

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute job discovery.
        Payload expected: {"url": "...", "search_criteria": {...}}
        """
        await self.start()
        try:
            url = payload.get("url")
            criteria = payload.get("search_criteria", {})

            # Initial navigation
            await self.browser.navigate(url)

            # Use the autonomous loop to perform search
            search_goal = (
                f"Search for jobs matching {criteria} and go to the results page."
            )
            result = await self.autonomous_loop(search_goal, max_steps=5)

            if result.get("status") != "success":
                return result

            # Once on results page, extract data
            # Typically tailored extraction logic or another brain call
            content = await self.browser.get_dom_snapshot()
            extracted_jobs = await self.brain.extract_data(
                content, schema={"jobs": [{"title": "str", "url": "str"}]}
            )

            return {
                "status": "success",
                "jobs_found": len(extracted_jobs.get("jobs", [])),
                "data": extracted_jobs,
            }

        finally:
            await self.stop()
