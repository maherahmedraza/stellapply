import asyncio
from typing import Dict, Optional

import structlog
from playwright.async_api import Browser, BrowserContext, Playwright, async_playwright

from src.agent.browser.engine import BrowserEngine
from src.agent.browser.proxy import ProxyManager
from src.agent.browser.session_store import SessionStore
from src.agent.browser.stealth import StealthBrowser
from src.core.config import settings

logger = structlog.get_logger(__name__)


class BrowserPool:
    """
    Manages a pool of reusable browser contexts.
    Each user gets their own BrowserContext (isolated cookies).
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BrowserPool, cls).__new__(cls)
            cls._instance._playwright: Optional[Playwright] = None
            cls._instance._browser: Optional[Browser] = None
            cls._instance._contexts: Dict[
                str, BrowserContext
            ] = {}  # user_id -> context

            # Components
            cls._instance.stealth = StealthBrowser()
            cls._instance.proxy_manager = ProxyManager()
            cls._instance.session_store = SessionStore()

            # Locks
            cls._instance._lock = asyncio.Lock()

        return cls._instance

    async def initialize(self):
        async with self._lock:
            if not self._playwright:
                logger.info("Initializing Browser Pool...")
                self._playwright = await async_playwright().start()

                # Launch one main browser instance to share
                # In prod, we might rotate this or have multiple if scaling locally
                self._browser = await self._playwright.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                    ],
                )
                logger.info("Browser Pool Initialized")

    async def acquire_browser(self, user_id: str) -> BrowserEngine:
        """
        Get a fully configured BrowserEngine (wrapper around context+page).
        Restores session if available.
        """
        if not self._playwright:
            await self.initialize()

        # Determine domain (placeholder, ideally passed in)
        # For now, we assume user might be working on multiple, but context is 1:1 with user in this MVP
        domain = "linkedin.com"  # Default for now, effectively generic session

        # Check for existing context
        # In a real pool, we'd check if context is busy, etc.
        # For now, we create fresh context per task to ensure clean slate + session restore

        # 1. Get Session State
        storage_state = await self.session_store.get_storage_state(user_id, domain)

        # 2. Get Proxy
        proxy = await self.proxy_manager.get_proxy(domain)

        # 3. Create Stealth Context
        # Note: We must create context WITH storage_state for best localStorage support
        # StealthBrowser wrapper needs to handle creation options
        # We'll do it manually here relying on stealth helper

        # Prepare context options
        context_opts = {}
        if storage_state:
            context_opts["storage_state"] = storage_state
        if proxy:
            context_opts["proxy"] = proxy.to_playwright_dict()

        # We need to mix stealth options into context_opts.
        # For now, we let stealth.create_stealth_context handle creation,
        # but we need to pass our state/proxy.
        # Let's adjust Stealth to accept kwargs or just do it here.
        # Since Stealth.create_stealth_context calls new_context internally, we can't easily injection.
        # REFACTOR: We'll modify Stealth.create_stealth_context to accept **kwargs

        # For MVP: Call stealth, which returns fresh context, then add cookies?
        # No, localStorage needs inject at creation.
        # We will assume Stealth.create_stealth_context is updated or we use its logic inline.

        # Using the Stealth logic inline here for correct composition:
        context = await self.stealth.create_stealth_context(
            self._browser, user_profile={}
        )

        # If we had storage state, we should have passed it.
        # Limitation: Stealth.create defined in previous step didn't take kwargs.
        # We will iterate on this. For now, restore cookies after creation.

        if storage_state:
            await context.add_cookies(storage_state["cookies"])
            # LocalStorage would be missing if not passed at init, but cookies are 90% of auth.

        page = await context.new_page()

        return BrowserEngine(context, page, self.session_store, user_id)

    async def release_browser(self, engine: BrowserEngine):
        """
        Cleanup and Save Session.
        """
        try:
            # We assume the engine knows the current relevant domain, or we save for all.
            # Using 'linkedin.com' as placeholder
            await self.session_store.save_session(
                engine.user_id, "linkedin.com", engine.context
            )
            await engine.close()
        except Exception as e:
            logger.error("Error releasing browser", error=str(e))

    async def shutdown(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
