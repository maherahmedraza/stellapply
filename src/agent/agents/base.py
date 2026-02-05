import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from src.agent.brain import AgentBrain, PageContext
from src.agent.browser.pool import BrowserPool
from src.agent.models.schemas import AgentTaskCreate, TaskStatus

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all autonomous agents.
    Implements the core 'Observe -> Think -> Act' loop.
    """

    def __init__(self, user_id: uuid.UUID, task_id: uuid.UUID):
        self.user_id = user_id
        self.task_id = task_id
        self.brain = AgentBrain()
        self.browser_pool = BrowserPool()
        self.browser = None
        self.history: List[Dict[str, Any]] = []

    async def start(self):
        """
        Initialize resources.
        """
        self.browser = await self.browser_pool.acquire_browser(str(self.user_id))
        logger.info(f"Agent {self.__class__.__name__} started for user {self.user_id}")

    async def stop(self):
        """
        Cleanup resources.
        """
        if self.browser:
            await self.browser_pool.release_browser(self.browser)
        logger.info(f"Agent {self.__class__.__name__} stopped")

    @abstractmethod
    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution logic specific to the agent type.
        """
        pass

    async def autonomous_loop(self, goal: str, max_steps: int = 10):
        """
        Execute the Observe-Think-Act loop.
        """
        for step in range(max_steps):
            # 1. Observe
            page_context = await self._capture_context()

            # 2. Think
            action = await self.brain.decide_next_action(
                task_description=goal,
                page_context=page_context,
                previous_actions=self.history,
            )

            logger.info(
                f"Step {step}: Brain decided to {action.action_type} - {action.description}"
            )

            if action.action_type == "finish":
                return {"status": "success", "reason": action.description}

            if action.action_type == "fail":
                raise Exception(action.description)

            # 3. Act
            await self.browser.execute_action(
                action.action_type, action.selector, action.value
            )

            # Record history
            self.history.append(action.model_dump())

        return {"status": "timeout", "reason": "Max steps reached"}

    async def _capture_context(self) -> PageContext:
        """
        Gather current state from the browser.
        """
        return PageContext(
            url=self.browser.page.url,
            title=await self.browser.page.title(),
            dom_snippet=await self.browser.get_dom_snapshot(),
            # screenshot_b64=await self.browser.take_screenshot() # Optimization: enable only when needed
        )
