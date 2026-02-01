from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import bs4

from src.modules.job_search.infrastructure.scrapers.base import (
    BaseScraper,
    RawJob,
    ScraperError,
)


class LeverScraper(BaseScraper):
    """Scraper for Lever ATS job boards"""

    source_name = "lever"
    base_url = "https://api.lever.co/v0/postings"

    # Known company boards on Lever
    COMPANY_BOARDS = [
        "netflix",
        "spotify",
        "twitch",
        "atlassian",
        "palantir",
        "affirm",
        "lyft",
        "benchling",
        "roblox",
        "udemy",
    ]

    async def search_jobs(
        self,
        keywords: list[str],
        location: str | None = None,
        remote_only: bool = False,
        posted_within_days: int = 7,
    ) -> AsyncIterator[RawJob]:
        cutoff_date = datetime.now(UTC) - timedelta(days=posted_within_days)

        for company in self.COMPANY_BOARDS:
            try:
                jobs = await self._get_company_jobs(company)
                for job in jobs:
                    if not self._matches_keywords(job, keywords):
                        continue
                    if location and not self._matches_location(job, location):
                        continue
                    if remote_only and not self._is_remote(job):
                        continue

                    # Lever timestamp is milliseconds integer
                    created_at = job.get("createdAt")
                    if created_at:
                        job_date = datetime.fromtimestamp(created_at / 1000, tz=UTC)
                        if job_date < cutoff_date:
                            continue

                    yield self._to_raw_job(job, company)
            except Exception as e:
                self.logger.warning(f"Failed to scrape {company}: {e}")
                continue

    async def _get_company_jobs(self, company: str) -> list[dict]:
        url = f"{self.base_url}/{company}?mode=json"
        try:
            data = await self._make_request(url)
            return data if isinstance(data, list) else []
        except ScraperError:
            return []
        except Exception:
            return []

    async def get_job_details(self, external_id: str) -> RawJob:
        company, job_id = external_id.split(":")
        url = f"{self.base_url}/{company}/{job_id}"
        data = await self._make_request(url)
        return self._to_raw_job(data, company)

    def _to_raw_job(self, data: dict, company: str) -> RawJob:
        return RawJob(
            external_id=f"{company}:{data['id']}",
            source=self.source_name,
            title=data["text"],
            company_name=company.title(),  # Lever JSON often omits company name
            location=data.get("categories", {}).get("location", ""),
            description=self._clean_html(
                data.get("descriptionPlain", data.get("description", ""))
            ),
            requirements=[],
            salary_range=None,
            posted_date=datetime.fromtimestamp(data["createdAt"] / 1000, tz=UTC)
            if data.get("createdAt")
            else None,
            apply_url=data.get("applyUrl", ""),
            remote_type=self._detect_remote(data),
            employment_type=data.get("categories", {}).get("commitment"),
            raw_data=data,
        )

    def _clean_html(self, html: str) -> str:
        if not html:
            return ""
        soup = bs4.BeautifulSoup(html, "html.parser")
        return soup.get_text(separator="\n", strip=True)

    def _matches_keywords(self, job: dict, keywords: list[str]) -> bool:
        title = job.get("text", "").lower()
        return any(k.lower() in title for k in keywords)

    def _matches_location(self, job: dict, location: str) -> bool:
        job_loc = job.get("categories", {}).get("location", "").lower()
        return location.lower() in job_loc

    def _is_remote(self, job: dict) -> bool:
        loc = job.get("categories", {}).get("location", "").lower()
        return "remote" in loc

    def _detect_remote(self, data: dict) -> str | None:
        return "remote" if self._is_remote(data) else "onsite"
