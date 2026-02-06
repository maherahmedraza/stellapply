import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from src.agent.brain import AgentBrain
from src.agent.browser.pool import BrowserPool
from src.agent.executor import ActionExecutor
from src.agent.hitl.schemas import InterventionContext, InterventionType
from src.agent.hitl.service import InterventionService
from src.agent.models.schemas import PageContext
from src.agent.recovery.health import PageHealthChecker
from src.agent.recovery.retry import ActionRetrier
from src.modules.profile.schemas import UserProfileResponse

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all autonomous agents.
    Implements the core 'Observe -> Think -> Act' loop.
    """

    def __init__(self, user_id: uuid.UUID, task_id: uuid.UUID):
        self.user_id = user_id
        self.task_id = task_id
        self.brain = None  # Lazily initialized with profile
        self.browser_pool = BrowserPool()
        self.browser = None
        self.hitl_service = InterventionService()
        self.history: List[Dict[str, Any]] = []

        # New Recovery Components
        self.health_checker = PageHealthChecker()
        self.retrier = ActionRetrier()
        self.executor = ActionExecutor()

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

    async def request_human_help(
        self, intervention_type: str, context: dict
    ) -> Dict[str, Any] | None:
        """
        Pause agent, request human help, wait for response.
        """
        # Take screenshot for context
        screenshot = await self.browser.take_screenshot()
        context["screenshot_b64"] = screenshot
        context["url"] = self.browser.page.url
        context["page_title"] = await self.browser.page.title()

        intervention_ctx = InterventionContext(**context)

        intervention = await self.hitl_service.request_intervention(
            session_id=self.task_id,
            user_id=self.user_id,
            intervention_type=intervention_type,
            context=intervention_ctx,
        )

        logger.info(
            f"Intervention {intervention.id} requested. Waiting for response..."
        )

        # Wait for user response (blocks this agent task)
        response = await self.hitl_service.wait_for_response(
            intervention.id, timeout_seconds=1800
        )

        if response is None:
            logger.warning("Intervention timed out.")
            return None

        logger.info(f"Received human response: {response.action}")
        return response

    async def autonomous_loop(
        self, goal: str, profile: UserProfileResponse, max_steps: int = 10
    ):
        """
        Execute the Observe-Think-Act loop with Health Checks and Action Retries.
        """
        # Initialize Brain if strictly necessary or update its profile context
        if not self.brain:
            self.brain = AgentBrain(profile)

        for step in range(max_steps):
            # 0. Health Check
            try:
                health = await self.health_checker.check(self.browser.page)
                if not health.is_healthy:
                    logger.warning(f"Unhealthy page state: {health.status_summary}")

                    if health.is_captcha or health.is_blocked:
                        # Immediate blocking issue -> Request Manual Help or Fail
                        response = await self.request_human_help(
                            InterventionType.CAPTCHA
                            if health.is_captcha
                            else InterventionType.CUSTOM,
                            {
                                "problem": "Page blocked or CAPTCHA detected",
                                "details": health.status_summary,
                            },
                        )
                        if not response:
                            return {
                                "status": "failed",
                                "reason": f"Unresolved page health issue: {health.status_summary}",
                            }
                        # If resolved, loop continues
            except Exception as e:
                logger.warning(f"Health check failed: {e}")

            # 1. Observe
            page_context = await self._capture_context()

            # 2. Think
            try:
                action = await self.brain.decide_next_action(
                    goal=goal, page_context=page_context
                )
            except Exception as e:
                logger.error(f"Brain decision failed: {e}")
                raise e

            logger.info(
                f"Step {step}: Brain decided to {action.action_type} - {action.thinking}"
            )

            if action.action_type == "task_complete":
                return {"status": "success", "reason": action.expected_result}

            if action.action_type == "human_handoff":
                response = await self.request_human_help(
                    intervention_type=InterventionType.UNKNOWN_QUESTION,  # Default classification
                    context={
                        "agent_thinking": action.thinking,
                        "question": action.expected_result,
                        "field_selector": action.selector,
                    },
                )

                if not response:
                    return {
                        "status": "failed",
                        "reason": "User did not respond to intervention",
                    }

                if response.action == "abort_application":
                    return {"status": "aborted_by_user"}

                if response.action == "provide_answer":
                    # Inject the human's answer and continue
                    if action.selector and response.value:
                        await self.browser.execute_action(
                            "type", action.selector, response.value
                        )

                    # Continue to next step
                    self.history.append(action.model_dump())
                    continue

                if response.action == "skip_field":
                    # Just continue loop without action
                    self.history.append(action.model_dump())
                    continue

            if action.action_type == "fail":
                return {"status": "failed", "reason": action.thinking}

            # 3. Act with Retry
            # Use retrier to execute the action via our Executor
            # Note: browser.execute_action (old way) logic is now inside Executor + Retrier

            # Since browser.execute_action was just a wrapper, we use retrier directly
            # providing the executor, page, and action.
            result = await self.retrier.execute_with_retry(
                executor=self.executor,
                page=self.browser.page,
                action=action,
                stealth=self.browser.stealth,
                brain=self.brain,
            )

            if not result.success:
                # If action critically failed after retries, we might want to handoff instead of fail immediately?
                # For now, let's log and maybe fail or ask brain again?
                # If action failed, brain needs to know.
                # Current loop implementation: Brain sees history.
                # We should probably inject the error into next brain prompt.
                # The BaseAgent helper `decide_next_action` supports `error_context`.
                # We need to store this error for next loop iteration
                logger.error(f"Action failed definitively: {result.error}")
                # TODO: Pass this error to next Brain cycle

                # For this MVP, if action failed, we return failed or try one last handoff?
                return {"status": "failed", "reason": str(result.error)}

            # Record history
            self.history.append(action.model_dump())

        return {"status": "timeout", "reason": "Max steps reached"}

    async def _capture_context(self) -> PageContext:
        """
        Gather current state from the browser.
        """
        snapshot = await self.browser.get_dom_snapshot()
        screenshot = await self.browser.take_screenshot()

        return PageContext(
            url=self.browser.page.url,
            title=await self.browser.page.title(),
            dom_snippet=snapshot,
            screenshot_b64=screenshot,
        )
