import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock

from src.agent.recovery.retry import ActionRetrier
from src.agent.recovery.health import PageHealthChecker, PageHealth
from src.agent.models.schemas import AgentAction
from src.agent.executor import ActionResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_action_retrier_logic():
    logger.info("Testing ActionRetrier Logic (Mocked)...")

    retrier = ActionRetrier()
    executor = MagicMock()
    page = MagicMock()
    stealth = MagicMock()
    brain = MagicMock()

    action = AgentAction(
        action_type="click",
        selector="#submit",
        thinking="Clicking submit",
        confidence=0.9,
        expected_result="Form submitted",
    )

    # Mock Executor to fail twice then succeed
    executor.execute = AsyncMock(
        side_effect=[
            ActionResult(
                success=False, error="TimeoutError: Waiting for selector #submit failed"
            ),
            ActionResult(
                success=False, error="TimeoutError: Waiting for selector #submit failed"
            ),
            ActionResult(success=True),
        ]
    )

    # Mock Strategy Execution
    # We must allow strategies to "work"
    retrier._execute_strategy = AsyncMock(return_value={"continue": True})

    result = await retrier.execute_with_retry(executor, page, action, stealth, brain)

    assert result.success is True
    assert executor.execute.call_count == 3
    # Check that strategies were called for the first two failures
    assert retrier._execute_strategy.call_count == 2

    logger.info("ActionRetrier Logic (Retry Success) PASSED ✅")

    # Test Max Retries Failure
    executor.execute = AsyncMock(
        return_value=ActionResult(success=False, error="Fatal Error")
    )
    retrier._execute_strategy = AsyncMock(return_value={"continue": True})

    result_fail = await retrier.execute_with_retry(
        executor, page, action, stealth, brain
    )
    assert result_fail.success is False
    # Max retries is 3, so call count should be 4 (initial + 3 retries)
    # Checking implementation: loop range(MAX_RETRIES + 1) -> 4 attempts.
    assert executor.execute.call_count == 4

    logger.info("ActionRetrier Logic (Max Retries) PASSED ✅")


async def test_page_health_checker():
    logger.info("Testing PageHealthChecker...")

    checker = PageHealthChecker()
    page = MagicMock()

    # Mock clean page
    page.is_visible = AsyncMock(return_value=False)
    page.inner_text = AsyncMock(return_value="Welcome to the job board")
    page.title = AsyncMock(return_value="Job Board Home")
    page.url = "https://example.com/jobs"
    page.evaluate = AsyncMock(return_value=True)

    health = await checker.check(page)
    assert health.is_healthy is True
    assert health.is_captcha is False

    # Mock CAPTCHA page
    page.is_visible = AsyncMock(
        side_effect=lambda s, **kw: "#captcha" in s
    )  # True if selector is #captcha
    health_captcha = await checker.check(page)
    assert health_captcha.is_captcha is True
    assert health_captcha.is_healthy is False

    # Mock 404 Page
    page.is_visible = AsyncMock(return_value=False)
    page.title = AsyncMock(return_value="404 Not Found")
    health_error = await checker.check(page)
    assert health_error.is_error_page is True
    assert health_error.is_healthy is False

    logger.info("PageHealthChecker Tests PASSED ✅")


if __name__ == "__main__":
    asyncio.run(test_action_retrier_logic())
    asyncio.run(test_page_health_checker())
