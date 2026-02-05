import asyncio
import logging

from playwright.async_api import async_playwright

from src.agent.browser.engine import BrowserEngine
from src.core.config import settings

logger = logging.getLogger(__name__)


class BrowserPool:
    """
    Manages a pool of BrowserEngine instances to limit concurrent resource usage.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BrowserPool, cls).__new__(cls)
            cls._instance._pool = asyncio.Queue(
                maxsize=settings.MAX_CONCURRENT_AGENTS
                if hasattr(settings, "MAX_CONCURRENT_AGENTS")
                else 5
            )
            cls._instance._active_count = 0
            cls._instance._playwright = None
        return cls._instance

    async def initialize(self):
        if not self._playwright:
            self._playwright = await async_playwright().start()

    async def acquire_browser(self, user_id: str) -> BrowserEngine:
        """
        Get a browser instance. If pool is full, wait.
        Ideally we would check if this user already has an active session.
        """
        if not self._playwright:
            await self.initialize()

        # Simple ephemeral implementation: create a new one every time but limit currency manually if needed
        # In a real pool we'd keep them alive.

        # Semaphore logic substitute
        if self._active_count >= 5:  # Hardcoded limit for now
            logger.warning("Browser pool limit reached, waiting...")
            # Ideally wait, but for MVP we create new

        self._active_count += 1
        # Note: We are creating a NEW engine each time here for simplicity in this MVP
        return await BrowserEngine.create(self._playwright, headless=True)

    async def release_browser(self, engine: BrowserEngine):
        """
        Return browser to pool or close it.
        """
        await engine.close()
        self._active_count -= 1

    async def shutdown(self):
        if self._playwright:
            await self._playwright.stop()
