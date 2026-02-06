import asyncio
import random
from typing import Any, Dict

import structlog
from fake_useragent import UserAgent
from playwright.async_api import Browser, BrowserContext, Page

logger = structlog.get_logger(__name__)


class StealthBrowser:
    """
    Configures Playwright to evade common bot detection.
    """

    def __init__(self):
        self.ua_generator = UserAgent()

    async def create_stealth_context(
        self, browser: Browser, user_profile: Dict[str, Any] | None = None
    ) -> BrowserContext:
        """
        Create a context with all anti-detection measures applied.
        """
        # 1. Randomize User Agent (consistent for session)
        user_agent = self.ua_generator.random

        # 2. Viewport randomization (common desktop resolutions)
        viewports = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1440, "height": 900},
            {"width": 1536, "height": 864},
        ]
        viewport = random.choice(viewports)

        # 3. Timezone & Locale (match user profile if available)
        # Default to commonly accepted generic values if no profile
        timezone_id = "America/New_York"
        locale = "en-US"
        geolocation = None

        # Logic to infer from user_profile could go here...

        context = await browser.new_context(
            user_agent=user_agent,
            viewport=viewport,
            timezone_id=timezone_id,
            locale=locale,
            geolocation=geolocation,
            permissions=["geolocation"],
            has_touch=False,
            is_mobile=False,
            java_script_enabled=True,
            accept_downloads=True,
        )

        # 4. Inject Stealth Scripts
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // WebGL Spoofing (minimal)
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                // UNMASKED_VENDOR_WEBGL
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                // UNMASKED_RENDERER_WEBGL
                if (parameter === 37446) {
                    return 'Intel(R) Iris(TM) Plus Graphics 640';
                }
                return getParameter(parameter);
            };
        """)

        return context

    async def human_type(
        self, page: Page, selector: str, text: str, speed: str = "normal"
    ):
        """
        Type text with human-like patterns.
        """
        # Focus first
        await page.click(selector)

        base_delay = {"slow": 150, "normal": 80, "fast": 30}.get(speed, 80)

        for char in text:
            # Variable delay
            delay = random.gauss(base_delay, 20)  # slightly randomized distribution
            if delay < 10:
                delay = 10

            await page.keyboard.type(char, delay=delay)

            # Simulate occasional pauses
            if random.random() < 0.05:  # 5% chance of pause
                await asyncio.sleep(random.uniform(0.1, 0.4))

    async def human_click(self, page: Page, selector: str):
        """
        Move mouse to element with Bezier-like steps (simulated by Playwright mostly,
        but we add random delays).
        """
        box = await page.locator(selector).bounding_box()
        if not box:
            await page.click(selector)  # Fallback
            return

        # Randomize point within element
        x = box["x"] + box["width"] * random.uniform(0.2, 0.8)
        y = box["y"] + box["height"] * random.uniform(0.2, 0.8)

        # Move mouse
        await page.mouse.move(x, y, steps=random.randint(5, 15))
        await asyncio.sleep(random.uniform(0.05, 0.15))
        await page.mouse.down()
        await asyncio.sleep(random.uniform(0.05, 0.1))
        await page.mouse.up()

    async def human_scroll(
        self, page: Page, direction: str = "down", amount: str = "medium"
    ):
        """
        Scroll with variable speed.
        """
        delta_y = {"small": 300, "medium": 700, "large": 1200}.get(amount, 700)
        if direction == "up":
            delta_y = -delta_y

        # Break into chunks
        steps = random.randint(3, 7)
        chunk_size = delta_y / steps

        for _ in range(steps):
            await page.mouse.wheel(0, chunk_size)
            await asyncio.sleep(random.uniform(0.05, 0.2))

    async def random_delay(self, min_ms: int = 500, max_ms: int = 2000):
        """
        Wait a random human-plausible duration.
        """
        await asyncio.sleep(random.uniform(min_ms / 1000, max_ms / 1000))

    async def simulate_reading(self, page: Page, content_length: int):
        """
        Wait proportional to content length.
        Assume ~10 chars per second reading speed for skimming.
        """
        read_time = min(content_length / 20, 10)  # Cap at 10s max for now
        await asyncio.sleep(random.uniform(read_time * 0.8, read_time * 1.2))
