import os
from typing import Any, Dict, Optional

import structlog
from pydantic import BaseModel, HttpUrl

logger = structlog.get_logger(__name__)


class ProxyConfig(BaseModel):
    server: str
    username: Optional[str] = None
    password: Optional[str] = None

    def to_playwright_dict(self) -> Dict[str, str]:
        """Convert to format expected by Playwright launch options."""
        return {
            "server": self.server,
            "username": self.username,
            "password": self.password,
        }


class ProxyManager:
    """
    Manages proxy rotation for IP diversity.
    """

    def __init__(self):
        self.provider = os.getenv("PROXY_PROVIDER", "none").lower()
        self.server_url = os.getenv("PROXY_URL")
        self.username = os.getenv("PROXY_USERNAME")
        self.password = os.getenv("PROXY_PASSWORD")

        # Simple stats tracking in-memory for now
        self.stats: Dict[
            str, Dict[str, int]
        ] = {}  # proxy_id -> {success: int, block: int}

    async def get_proxy(
        self, target_domain: str, user_location: str | None = None
    ) -> ProxyConfig | None:
        """
        Get a proxy configuration for the session.
        """
        if self.provider == "none" or not self.server_url:
            logger.info("No proxy configured, using direct connection")
            return None

        # Logic to append location/session params to proxy string if using SmartProxy/BrightData
        # Example for many providers: http://user-country-us-session-xyz:pass@host:port

        # Construct proxy config
        # This is generic; real implementation depends on provider API format
        return ProxyConfig(
            server=self.server_url, username=self.username, password=self.password
        )

    async def report_blocked(self, proxy_id: str, domain: str):
        """Track blocked IPs to rotate."""
        logger.warning("Proxy blocked", proxy_id=proxy_id, domain=domain)
        # In real impl, would update stats and avoid this proxy/IP

    async def get_stats(self) -> Dict[str, Any]:
        return self.stats
