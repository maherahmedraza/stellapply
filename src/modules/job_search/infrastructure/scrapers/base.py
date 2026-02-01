import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime

import aiohttp
from pydantic import BaseModel

from src.modules.job_search.infrastructure.scrapers.rate_limiter import RateLimiter


@dataclass
class RawJob:
    """Raw job data from scraper before normalization"""

    external_id: str
    source: str
    title: str
    company_name: str
    location: str
    description: str
    requirements: list[str]
    salary_range: str | None
    posted_date: datetime | None
    apply_url: str
    remote_type: str | None
    employment_type: str | None
    raw_data: dict  # Original response for debugging


class ScraperConfig(BaseModel):
    """Configuration for scrapers"""

    user_agent: str = (
        "Mozilla/5.0 (compatible; StellarApply/1.0; +http://stellarapply.com)"
    )
    timeout_seconds: int = 30
    proxy_url: str | None = None


class ScraperError(Exception):
    """Base exception for scraper errors"""

    pass


class BaseScraper(ABC):
    """Base class for all job scrapers"""

    def __init__(
        self,
        http_client: aiohttp.ClientSession,
        rate_limiter: RateLimiter,
        config: ScraperConfig,
    ):
        self.http = http_client
        self.rate_limiter = rate_limiter
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Unique identifier for this source"""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Base URL for API/scraping"""
        pass

    @abstractmethod
    async def search_jobs(
        self,
        keywords: list[str],
        location: str | None = None,
        remote_only: bool = False,
        posted_within_days: int = 7,
    ) -> AsyncIterator[RawJob]:
        """Search for jobs matching criteria"""
        pass

    @abstractmethod
    async def get_job_details(self, external_id: str) -> RawJob:
        """Get full details for a specific job"""
        pass

    async def _make_request(self, url: str, method: str = "GET", **kwargs) -> dict:
        """Make rate-limited HTTP request"""
        await self.rate_limiter.acquire(self.source_name)

        headers = kwargs.pop("headers", {})
        headers["User-Agent"] = self.config.user_agent

        kwargs["headers"] = headers

        # Merge proxy from config if not explicit
        if self.config.proxy_url and "proxy" not in kwargs:
            kwargs["proxy"] = self.config.proxy_url

        try:
            async with self.http.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            self.logger.error(f"Request failed: {url} - {e}")
            raise ScraperError(f"Failed to fetch {url}") from e

    def _normalize_location(self, raw_location: str) -> dict:
        """Normalize location string to structured data"""
        # Placeholder for normalization logic
        return {"raw": raw_location}

    def _parse_salary(self, raw_salary: str) -> dict | None:
        """Parse salary string to structured range"""
        # Placeholder
        _ = raw_salary
        return None
