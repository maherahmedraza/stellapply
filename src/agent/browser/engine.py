import asyncio
import base64
import logging
from typing import Any

from playwright.async_api import BrowserContext, Page, Playwright, async_playwright

logger = logging.getLogger(__name__)


class BrowserEngine:
    """
    Wrapper around a Playwright Page/Context to provide agent-friendly methods.
    Handles anti-detection, screenshots, and robust interaction.
    """

    def __init__(self, context: BrowserContext, page: Page):
        self.context = context
        self.page = page

    @classmethod
    async def create(
        cls, playwright: Playwright, headless: bool = True
    ) -> "BrowserEngine":
        """
        Factory to create a new browser instance properly configured.
        """
        browser = await playwright.chromium.launch(headless=headless)
        # Anti-detection args would go here (user agent, viewport, etc)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
        )
        page = await context.new_page()
        return cls(context, page)

    async def navigate(self, url: str):
        """
        Robust navigation with error handling.
        """
        try:
            await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)  # Human-like pause
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            raise

    async def get_dom_snapshot(self) -> str:
        """
        Get a simplified DOM or accessibility tree for the Brain.
        """
        # Simplistic approach: get innerHTML of body
        # Better approach: traversing the accessibility tree or creating a simplified representation
        return await self.page.content()

    async def take_screenshot(self) -> str:
        """
        Return base64 screenshot.
        """
        image_bytes = await self.page.screenshot(format="jpeg", quality=60)
        return base64.b64encode(image_bytes).decode("utf-8")

    async def execute_action(
        self, action_type: str, selector: str | None = None, value: str | None = None
    ):
        """
        Execute an action decided by the Brain.
        """
        if action_type == "click" and selector:
            await self.page.click(selector)
        elif action_type == "type" and selector and value:
            await self.page.fill(selector, value)
        elif action_type == "navigate" and value:
            await self.navigate(value)
        elif action_type == "scroll":
            await self.page.evaluate("window.scrollBy(0, 500)")
        elif action_type == "wait":
            await asyncio.sleep(2)
        else:
            logger.warning(f"Unknown or incomplete action: {action_type}")

        # Human-like delay after action
        await asyncio.sleep(1)

    async def close(self):
        await self.context.close()
