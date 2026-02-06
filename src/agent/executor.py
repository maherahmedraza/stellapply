import asyncio
from typing import Any, Dict, Optional

import structlog
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from src.agent.brain import AgentAction
from src.agent.browser.stealth import StealthBrowser

logger = structlog.get_logger(__name__)


class ActionResult:
    def __init__(
        self,
        success: bool,
        error: Optional[str] = None,
        page_changed: bool = False,
        new_url: Optional[str] = None,
        screenshot: Optional[bytes] = None,
    ):
        self.success = success
        self.error = error
        self.page_changed = page_changed
        self.new_url = new_url
        self.screenshot = screenshot

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "error": self.error,
            "page_changed": self.page_changed,
            "new_url": self.new_url,
            # Screenshot bytes omitted for logging brevity
        }


class ActionExecutor:
    """
    Executes AgentAction objects on a Playwright Page with human-like behavior.
    """

    async def execute(
        self, page: Page, action: AgentAction, stealth: StealthBrowser
    ) -> ActionResult:
        """
        Execute a single action and return result.
        """
        logger.info(
            "Execute Action", action_type=action.action_type, selector=action.selector
        )

        try:
            start_url = page.url

            # 1. Validation & Pre-execution checks
            if action.action_type in ["click", "type", "select", "upload"]:
                if not action.selector:
                    return ActionResult(False, error="Missing selector for interaction")

                # Check visibility check with short timeout
                try:
                    is_visible = await page.is_visible(action.selector, timeout=5000)
                    if not is_visible:
                        # Try scrolling to it first
                        element = page.locator(action.selector).first
                        await element.scroll_into_view_if_needed()
                        await asyncio.sleep(0.5)
                except Exception:
                    pass  # Proceed to try action anyway, might be hidden but interactive

            # 2. Execution
            if action.action_type == "click":
                await stealth.human_click(page, action.selector)

            elif action.action_type == "type":
                await stealth.human_type(page, action.selector, action.value or "")

            elif action.action_type == "select":
                await page.select_option(action.selector, value=action.value)
                await asyncio.sleep(0.5)

            elif action.action_type == "upload":
                # file_path provided in value
                async with page.expect_file_chooser() as fc_info:
                    await page.click(action.selector)
                file_chooser = await fc_info.value
                await file_chooser.set_files(action.value)

            elif action.action_type == "scroll":
                direction = "down"
                if action.value and "up" in action.value.lower():
                    direction = "up"
                await stealth.human_scroll(page, direction=direction)

            elif action.action_type == "navigate":
                if not action.value:
                    return ActionResult(False, error="No URL provided for navigation")
                await page.goto(
                    action.value, wait_until="domcontentloaded", timeout=60000
                )

            elif action.action_type == "wait":
                # Value is seconds
                wait_time = 2.0
                try:
                    if action.value:
                        wait_time = float(action.value)
                except ValueError:
                    pass
                await asyncio.sleep(wait_time)

            elif action.action_type == "task_complete":
                # Logic handled by Orchestrator usually, but we ack success
                pass

            else:
                return ActionResult(
                    False, error=f"Unknown action type: {action.action_type}"
                )

            # 3. Post-Action Verification
            # Check if URL changed
            new_url = page.url
            page_changed = start_url != new_url

            # Check expected result logic if provided (simple version)
            # In advanced brain, we might re-observe the DOM.

            return ActionResult(
                success=True, page_changed=page_changed, new_url=new_url
            )

        except PlaywrightTimeoutError:
            return ActionResult(False, error="Timeout waiting for element or page load")
        except Exception as e:
            logger.error("Action execution failed", error=str(e))
            return ActionResult(False, error=str(e))

    async def verify_action(self, page: Page, expected: str) -> bool:
        """
        Verify that the action had its expected effect.
        Currently a placeholder for more complex verification logic.
        """
        return True
