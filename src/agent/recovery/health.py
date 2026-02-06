import logging
from dataclasses import dataclass
from playwright.async_api import Page

logger = logging.getLogger(__name__)


@dataclass
class PageHealth:
    is_error_page: bool
    is_captcha: bool
    is_login_wall: bool
    is_rate_limited: bool
    is_blocked: bool
    has_overlay: bool
    page_loaded: bool

    @property
    def is_healthy(self) -> bool:
        return not any(
            [
                self.is_error_page,
                self.is_captcha,
                self.is_login_wall,
                self.is_rate_limited,
                self.is_blocked,
            ]
        )

    @property
    def status_summary(self) -> str:
        issues = []
        if self.is_error_page:
            issues.append("Error Page")
        if self.is_captcha:
            issues.append("CAPTCHA")
        if self.is_login_wall:
            issues.append("Login Wall")
        if self.is_rate_limited:
            issues.append("Rate Limited")
        if self.is_blocked:
            issues.append("Blocked")
        return ", ".join(issues) if issues else "Healthy"


class PageHealthChecker:
    """Detect common page problems before agent acts."""

    async def check(self, page: Page) -> PageHealth:
        return PageHealth(
            is_error_page=await self._is_error_page(page),
            is_captcha=await self._is_captcha_page(page),
            is_login_wall=await self._is_login_wall(page),
            is_rate_limited=await self._is_rate_limited(page),
            is_blocked=await self._is_blocked(page),
            has_overlay=await self._has_blocking_overlay(page),
            page_loaded=await self._is_page_loaded(page),
        )

    async def _is_captcha_page(self, page: Page) -> bool:
        indicators = [
            "iframe[src*='recaptcha']",
            "iframe[src*='captcha']",
            "#captcha",
            ".g-recaptcha",
            "[class*='captcha']",
            "iframe[src*='hcaptcha']",
            "#cf-challenge-running",
            "iframe[title*='reCAPTCHA']",
        ]
        for selector in indicators:
            try:
                if await page.is_visible(selector, timeout=500):
                    return True
            except:
                continue

        # Also check page text
        try:
            text = await page.inner_text("body", timeout=500)
            text = text.lower()
            captcha_phrases = [
                "verify you are human",
                "are you a robot",
                "captcha",
                "security check",
                "bot detection",
            ]
            return any(phrase in text for phrase in captcha_phrases)
        except:
            return False

    async def _is_error_page(self, page: Page) -> bool:
        try:
            title = (await page.title()).lower()
            # url = page.url.lower()
            error_indicators = [
                "404",
                "not found",
                "error",
                "500",
                "forbidden",
                "403",
                "page not found",
                "seite nicht gefunden",
            ]
            return any(ind in title for ind in error_indicators)
        except:
            return False

    async def _is_rate_limited(self, page: Page) -> bool:
        try:
            text = (await page.inner_text("body", timeout=500)).lower()
            return any(
                phrase in text
                for phrase in [
                    "too many requests",
                    "rate limit",
                    "slow down",
                    "try again later",
                    "temporarily blocked",
                ]
            )
        except:
            return False

    async def _is_login_wall(self, page: Page) -> bool:
        try:
            url = page.url.lower()
            # If redirected to login page when not expecting it
            # Simple heuristic
            return "/login" in url or "signin" in url
        except:
            return False

    async def _is_blocked(self, page: Page) -> bool:
        try:
            title = (await page.title()).lower()
            if (
                "access denied" in title
                or "blocked" in title
                or "security check" in title
            ):
                return True
            text = (await page.inner_text("body", timeout=500)).lower()
            return "access denied" in text or "security challenge" in text
        except:
            return False

    async def _has_blocking_overlay(self, page: Page) -> bool:
        # Hard to robustly detect generic generic overlays without heuristics
        # This is a best-effort check for known blockers
        selectors = [
            ".modal-backdrop",
            ".overlay",
            ".popup-overlay",
            "[id*='modal']",
            "[role='dialog']",
        ]
        count = 0
        for s in selectors:
            try:
                if await page.is_visible(s, timeout=200):
                    count += 1
            except:
                pass
        return count > 0

    async def _is_page_loaded(self, page: Page) -> bool:
        # Check if basic tags exist
        try:
            return await page.evaluate("() => document.readyState === 'complete'")
        except:
            return False
