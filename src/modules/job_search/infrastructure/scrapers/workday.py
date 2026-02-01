from collections.abc import AsyncIterator

from src.modules.job_search.infrastructure.scrapers.base import (
    BaseScraper,
    RawJob,
    ScraperError,
)


class WorkdayScraper(BaseScraper):
    """
    Scraper for Workday.
    Note: Workday does not have a public unified API for job boards.
    Each company has a unique tenant URL and structure.
    This scraper is a stub/skeleton for tenant-specific implementations.
    """

    source_name = "workday"
    base_url = "https://wd5.myworkdaysite.com/recruiting"  # Example common base

    # Workday scraping is complex and often requires Selenium/Playwright
    # due to heavy JS and anti-bot.
    # This implementation is a placeholder.

    async def search_jobs(
        self,
        keywords: list[str],
        location: str | None = None,
        remote_only: bool = False,
        posted_within_days: int = 7,
    ) -> AsyncIterator[RawJob]:
        # Stub implementation
        _ = keywords
        _ = location
        _ = remote_only
        _ = posted_within_days
        self.logger.warning("Workday scraper is a stub. No jobs will be returned.")
        return
        yield  # Empty generator

    async def get_job_details(self, external_id: str) -> RawJob:
        _ = external_id
        raise ScraperError("Workday scraper not fully implemented")
