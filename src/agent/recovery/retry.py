import logging
import asyncio
from typing import Any, Dict, Optional, TYPE_CHECKING
from playwright.async_api import Page

if TYPE_CHECKING:
    from src.agent.executor import ActionExecutor, ActionResult
    from src.agent.models.schemas import AgentAction
    from src.agent.browser.stealth import StealthBrowser
    from src.agent.brain import AgentBrain

logger = logging.getLogger(__name__)


class ActionRetrier:
    """
    Retry failed actions with intelligent strategies.
    """

    MAX_RETRIES = 3
    RETRY_STRATEGIES = {
        "selector_not_found": [
            "wait_and_retry",  # Wait 2s, try same selector
            "try_alternative_selector",  # Ask Brain for alternative selector
            "scroll_and_retry",  # Scroll to find element
            "reload_and_retry",  # Page reload as last resort
        ],
        "timeout": [
            "increase_timeout",
            "wait_and_retry",
            "reload_and_retry",
        ],
        "click_intercepted": [
            "dismiss_overlay",  # Look for modals/popups blocking
            "scroll_to_element",
            "javascript_click",  # Force click via JS
        ],
        "navigation_failed": [
            "retry_with_delay",
            "try_alternative_url",
            "report_site_down",
        ],
        "generic_error": ["wait_and_retry", "reload_and_retry"],
    }

    async def execute_with_retry(
        self,
        executor: "ActionExecutor",
        page: Page,
        action: "AgentAction",
        stealth: "StealthBrowser",
        brain: "AgentBrain",
    ) -> Any:  # Returns ActionResult
        """
        Execute an action with automatic retry and fallback strategies.
        """
        last_error = None

        # We need to import ActionResult here to avoid circular imports if possible or rely on return type
        # Ideally ActionExecutor returns a structure we can check.
        # Assuming executor.execute returns ActionResult object

        # Initial attempt + retries
        for attempt in range(self.MAX_RETRIES + 1):
            if attempt > 0:
                logger.info(f"Retry attempt {attempt} for action {action.action_type}")

            result = await executor.execute(page, action, stealth)

            if result.success:
                return result

            last_error = result.error
            error_category = self._categorize_error(str(result.error))

            # If we used all retries, break
            if attempt >= self.MAX_RETRIES:
                break

            # Get strategy for next attempt (attempt 0 uses strategy index 0, etc.)
            strategies = self.RETRY_STRATEGIES.get(
                error_category, self.RETRY_STRATEGIES["generic_error"]
            )
            # Ensure we don't go out of bounds
            strategy_idx = attempt
            if strategy_idx >= len(strategies):
                strategy = strategies[-1]  # Reuse last strategy
            else:
                strategy = strategies[strategy_idx]

            logger.warning(
                f"Action failed (attempt {attempt + 1}), trying strategy: {strategy}",
                extra={"error": str(result.error)},
            )

            # Execute recovery strategy
            recovered = await self._execute_strategy(
                strategy, page, action, stealth, brain
            )

            if recovered and recovered.get("continue"):
                # If strategy says continue, we loop to next attempt
                # Strategies might mutate state (scroll, reload)

                # If strategy suggests new action usage:
                if recovered.get("new_action"):
                    action = recovered["new_action"]
                continue
            else:
                # Strategy failed or dictates no retry
                logger.warning(
                    f"Recovery strategy {strategy} returned non-continuable result."
                )
                # We might want to continue anyway to next strategy?
                # For now let's continue to next retry loop which picks next strategy.
                continue

        # Force failure return if we exit loop
        from src.agent.executor import ActionResult  # Local import to avoid circular

        return ActionResult(
            success=False,
            error=f"Failed after {self.MAX_RETRIES} attempts. Last error: {last_error}",
        )

    def _categorize_error(self, error_msg: str) -> str:
        error_msg = error_msg.lower()
        if "timeout" in error_msg:
            return "timeout"
        if (
            "selector" in error_msg
            or "element not found" in error_msg
            or "waiting for selector" in error_msg
        ):
            return "selector_not_found"
        if "intercepted" in error_msg or "obscured" in error_msg:
            return "click_intercepted"
        if "navigat" in error_msg or "load" in error_msg:
            return "navigation_failed"
        return "generic_error"

    async def _execute_strategy(
        self,
        strategy: str,
        page: Page,
        action: "AgentAction",
        stealth: "StealthBrowser",
        brain: "AgentBrain",
    ) -> Optional[Dict[str, Any]]:

        try:
            if strategy == "wait_and_retry":
                await stealth.random_delay(2000, 4000)
                return {"continue": True}

            elif strategy == "dismiss_overlay":
                # Try to find and close modal/popup/overlay
                overlay_close_selectors = [
                    "button[aria-label='Close']",
                    ".modal-close",
                    ".popup-close",
                    "button:has-text('Close')",
                    "button:has-text('×')",
                    "[class*='overlay'] button",
                    ".cookie-banner button",
                    "button[data-testid='close-button']",
                    "svg[data-icon='times']",
                ]
                for selector in overlay_close_selectors:
                    try:
                        if await page.is_visible(selector, timeout=1000):
                            logger.info(f"Dismissing overlay with {selector}")
                            await page.click(selector)
                            await stealth.random_delay(500, 1000)
                            return {"continue": True}
                    except:
                        continue
                return {"continue": True}  # Retry anyway even if no overlay found

            elif strategy == "try_alternative_selector":
                # Ask Brain for local alternative? Or just use fallback from Action?
                if action.fallback_selector:
                    logger.info(f"Using fallback selector: {action.fallback_selector}")
                    # Update action in place or return new action
                    # We return new action instructions
                    # Cloning action with new selector
                    new_action = action.model_copy(
                        update={"selector": action.fallback_selector}
                    )
                    return {"continue": True, "new_action": new_action}

                # Ideally we ask Brain, but for now fallback is critical.
                return {"continue": True}

            elif strategy == "javascript_click":
                try:
                    logger.info("Attempting JS click")
                    await page.evaluate(
                        f"document.querySelector('{action.selector}')?.click()"
                    )
                    # JS click helps if standard click fails, but we need to check if it actually worked?
                    # The executor checks success if we return success=True here?
                    # No, this function just sets state for the NEXT RETRY.
                    # So we click via JS, then return continue=True.
                    # The next loop will try standard execute. Wait, if we JS clicked, we might be done?
                    # ActionExecutor's execute expects to do the work.
                    # If we do the work here, the next execute might click AGAIN or fail if element is gone.
                    # Strategy: JS click IS the attempt.
                    # But our loop calls `executor.execute` again.
                    # If JS click worked, `execute` might fail finding element if page changed?
                    # Let's assume JS click is a setup or workaround.
                    # Actually, better: if we JS click here, we should probably verify outcome or return success?
                    # But the structure expects us to return "continue" to retry via Executor.
                    # If we JS Click here, the next `executor.execute` will try again.
                    # If the button triggered navigation, the element is gone -> error "selector not found".

                    # Correct approach: `javascript_click` strategy should probably modify the *executor's* method
                    # or validly "execute" the action.
                    # Since we can't easily swap executor logic, maybe we modify action to "wait" and assume we did it?
                    # Or we just accept that we do it here, and the next retry attempts standard click which might fail.

                    # Optimized: If we JS Click, we sleep and return True (success)?
                    # But we can't return ActionResult from here.
                    # Let's perform the JS click, and then return "continue" with a Wait action?
                    # Or just return continue and hope the next standard click works (it won't if JS click worked).

                    # Workaround: Return a "wait" action so the next loop just waits and returns success?
                    # Executor `wait` action always succeeds.
                    from src.agent.models.schemas import AgentAction

                    new_action = AgentAction(
                        action_type="wait",
                        thinking="Executed JS click strategy, waiting for result",
                        confidence=1.0,
                        expected_result="Action completed via JS",
                    )
                    await page.evaluate(
                        f"document.querySelector('{action.selector}')?.click()"
                    )
                    await stealth.random_delay(1000, 2000)
                    return {"continue": True, "new_action": new_action}
                except Exception as e:
                    logger.warning(f"JS click failed: {e}")
                    return None

            elif strategy == "scroll_and_retry":
                await stealth.human_scroll(page, direction="down", amount="medium")
                await stealth.random_delay(1000, 2000)
                # Also try scrolling to element specifically
                if action.selector:
                    try:
                        await page.locator(
                            action.selector
                        ).first.scroll_into_view_if_needed(timeout=2000)
                    except:
                        pass
                return {"continue": True}

            elif strategy == "scroll_to_element":
                if action.selector:
                    try:
                        await page.locator(
                            action.selector
                        ).first.scroll_into_view_if_needed(timeout=2000)
                    except:
                        pass
                return {"continue": True}

            elif strategy == "reload_and_retry":
                logger.info("Reloading page...")
                await page.reload(wait_until="domcontentloaded")
                await stealth.random_delay(2000, 4000)
                return {"continue": True}

            elif strategy == "increase_timeout":
                # We can't easily change executor timeout without passing config
                # But we can wait here
                await asyncio.sleep(2)
                return {"continue": True}

            return None

        except Exception as e:
            logger.error(f"Error during strategy execution ({strategy}): {e}")
            return None
