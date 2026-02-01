import asyncio
import logging
import random
from enum import Enum
from typing import Any

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

logger = logging.getLogger(__name__)


class ATSPlatform(Enum):
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    WORKDAY = "workday"
    BAMBOOHR = "bamboohr"
    SMARTRECRUITERS = "smartrecruiters"
    CUSTOM = "custom"


STEALTH_CONFIG: dict[str, Any] = {
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "locale": "en-US",
    "timezone_id": "America/New_York",
    "geolocation": None,
    "permissions": [],
    "extra_http_headers": {"Accept-Language": "en-US,en;q=0.9"},
}


class BrowserAutomation:
    """
    Core browser automation engine using Playwright.
    Includes stealth usage patterns and human-like behaviors.
    """

    def __init__(self, headless: bool = True, proxy: str | None = None):
        self.headless = headless
        self.proxy = proxy
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    async def start(self) -> None:
        """Initializes the Playwright instance and browser."""
        if self._playwright:
            return

        self._playwright = await async_playwright().start()

        args = [
            "--disable-blink-features=AutomationControlled",
        ]

        launch_options: dict[str, Any] = {
            "headless": self.headless,
            "args": args,
        }

        if self.proxy:
            launch_options["proxy"] = {"server": self.proxy}

        self._browser = await self._playwright.chromium.launch(**launch_options)

    async def create_context(self) -> BrowserContext:
        """Creates a new browser context with stealth settings."""
        if not self._browser:
            await self.start()
            if not self._browser:  # Should be set by start()
                raise RuntimeError("Failed to start browser")

        context = await self._browser.new_context(
            viewport=STEALTH_CONFIG["viewport"],
            user_agent=str(STEALTH_CONFIG["user_agent"]),
            locale=str(STEALTH_CONFIG["locale"]),
            timezone_id=str(STEALTH_CONFIG["timezone_id"]),
            extra_http_headers=STEALTH_CONFIG["extra_http_headers"],
        )

        # Additional stealth scripts
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        self._context = context
        return context

    async def navigate_to_job(self, url: str) -> Page:
        """Navigates to a specific job URL safely."""
        if not self._context:
            await self.create_context()

        if not self._context:
            raise RuntimeError("Context not initialized")

        page = await self._context.new_page()
        try:
            # Random delay before navigation
            await asyncio.sleep(random.uniform(0.5, 1.5))

            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Mimic reading time
            await asyncio.sleep(random.uniform(1.0, 3.0))

            return page
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            await page.close()
            raise

    def detect_ats_platform(self, page: Page) -> ATSPlatform:
        """Detects the ATS platform from the current page URL."""
        url = page.url.lower()

        if "greenhouse.io" in url or "boards.greenhouse.io" in url:
            return ATSPlatform.GREENHOUSE
        if "lever.co" in url or "jobs.lever.co" in url:
            return ATSPlatform.LEVER
        if "workday" in url or "myworkdayjobs.com" in url:
            return ATSPlatform.WORKDAY
        if "bamboohr.com" in url:
            return ATSPlatform.BAMBOOHR
        if "smartrecruiters.com" in url:
            return ATSPlatform.SMARTRECRUITERS

        return ATSPlatform.CUSTOM

    async def human_type(self, page: Page, selector: str, text: str) -> None:
        """Types text into a selector with random delays between keystrokes."""
        element = await page.wait_for_selector(selector, state="visible", timeout=10000)
        if not element:
            raise ValueError(f"Element {selector} not found")

        await element.click()

        for char in text:
            await page.keyboard.type(char, delay=random.randint(50, 150))
            # Occasional pause
            if random.random() < 0.1:
                await asyncio.sleep(random.uniform(0.1, 0.4))

    async def human_scroll(self, page: Page) -> None:
        """Scrolls the page naturally with random pauses."""
        total_height = await page.evaluate("document.body.scrollHeight")
        current_scroll = 0

        while current_scroll < total_height:
            scroll_amount = random.randint(300, 700)
            current_scroll += scroll_amount

            await page.mouse.wheel(0, scroll_amount)

            # Pause to "read"
            await asyncio.sleep(random.uniform(0.5, 2.0))

            # Sometimes scroll back up slightly
            if random.random() < 0.2:
                await page.mouse.wheel(0, -random.randint(100, 300))
                await asyncio.sleep(random.uniform(0.5, 1.0))

            # Recalculate execution height just in case dynamic content loaded
            total_height = await page.evaluate("document.body.scrollHeight")

    async def random_mouse_movement(self, page: Page) -> None:
        """Moves the mouse randomly across the screen."""
        width = await page.evaluate("window.innerWidth")
        height = await page.evaluate("window.innerHeight")

        for _ in range(random.randint(3, 7)):
            x = random.randint(0, width)
            y = random.randint(0, height)

            await page.mouse.move(x, y, steps=random.randint(5, 25))
            await asyncio.sleep(random.uniform(0.1, 0.5))

    async def capture_screenshot(self, page: Page) -> bytes:
        """Captures a full page screenshot."""
        return await page.screenshot(full_page=True)

    async def close(self) -> None:
        """Cleans up browser resources."""
        if self._context:
            await self._context.close()
            self._context = None

        if self._browser:
            await self._browser.close()
            self._browser = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
