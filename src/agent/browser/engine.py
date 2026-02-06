import asyncio
import base64
import random
from typing import Any, Dict, Optional

import structlog
from playwright.async_api import BrowserContext, Page, Playwright

from src.agent.browser.capture import PageCapture
from src.agent.browser.session_store import SessionStore
from src.agent.browser.stealth import StealthBrowser

logger = structlog.get_logger(__name__)


class BrowserEngine:
    """
    Wrapper around a Playwright Page/Context to provide agent-friendly methods.
    Handles anti-detection, screenshots, and robust interaction.
    """

    def __init__(
        self,
        context: BrowserContext,
        page: Page,
        session_store: SessionStore,
        user_id: str,
    ):
        self.context = context
        self.page = page
        self.session_store = session_store
        self.user_id = user_id

        self.stealth = StealthBrowser()
        self.capture = PageCapture()

    @classmethod
    async def create(
        cls, playwright: Playwright, headless: bool = True
    ) -> "BrowserEngine":
        """
        Legacy factory - used by pool mostly but pool does custom creation now.
        kept for compatibility during refactor.
        """
        # This shouldn't be called directly ideally
        raise NotImplementedError("Use BrowserPool.acquire_browser()")

    async def navigate(self, url: str):
        """
        Robust navigation with error handling.
        """
        try:
            logger.info("Navigate", url=url)
            await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await self.stealth.random_delay(2000, 4000)
        except Exception as e:
            logger.error("Navigation failed", url=url, error=str(e))
            raise

    async def get_dom_snapshot(self) -> Dict[str, Any]:
        """
        Get a simplified DOM for the Brain.
        """
        return await self.capture.extract_dom(self.page)

    async def take_screenshot(self) -> str:
        """
        Return base64 screenshot.
        """
        bytes_data = await self.capture.screenshot(self.page)
        return base64.b64encode(bytes_data).decode("utf-8")

    async def execute_action(
        self, action_type: str, selector: str | None = None, value: str | None = None
    ):
        """
        Execute an action decided by the Brain.
        """
        logger.info(
            "Executing action", type=action_type, selector=selector, value=value
        )

        try:
            if action_type == "click" and selector:
                await self.stealth.human_click(self.page, selector)

            elif action_type == "type" and selector and value:
                await self.stealth.human_type(self.page, selector, value)

            elif action_type == "navigate" and value:
                await self.navigate(value)

            elif action_type == "scroll":
                await self.stealth.human_scroll(self.page)

            elif action_type == "wait":
                await self.stealth.random_delay(2000, 5000)

            elif action_type == "finish":
                logger.info("Agent finished task")

            elif action_type == "fail":
                logger.error("Agent reported failure")

            else:
                logger.warning("Unknown action", action=action_type)

            # Post-action stability delay
            await self.stealth.random_delay(1000, 2000)

        except Exception as e:
            logger.error("Action execution failed", action=action_type, error=str(e))
            raise

    async def close(self):
        await self.context.close()
