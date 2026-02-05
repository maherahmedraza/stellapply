from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import bs4

from src.modules.job_search.infrastructure.scrapers.base import (
    BaseScraper,
    RawJob,
    ScraperError,
)


class GreenhouseScraper(BaseScraper):
    """Scraper for Greenhouse ATS job boards"""

    source_name = "greenhouse"
    base_url = "https://boards-api.greenhouse.io/v1/boards"

    # Known company boards on Greenhouse (Example list)
    COMPANY_BOARDS = [
        "openai",
        "stripe",
        "figma",
        "notion",
        "airbnb",
        "coinbase",
        "doordash",
        "instacart",
        "robinhood",
        "ramp",
        "brex",
        "plaid",
        "gusto",
        "discord",
    ]

    async def search_jobs(
        self,
        keywords: list[str],
        location: str | None = None,
        remote_only: bool = False,
        posted_within_days: int = 7,
    ) -> AsyncIterator[RawJob]:
        """Search across all known Greenhouse boards"""

        cutoff_date = datetime.now(UTC) - timedelta(days=posted_within_days)

        for company in self.COMPANY_BOARDS:
            try:
                jobs = await self._get_company_jobs(company)

                for job in jobs:
                    # Filter by keywords
                    if not self._matches_keywords(job, keywords):
                        continue

                    # Filter by location
                    if location and not self._matches_location(job, location):
                        continue

                    # Filter by remote
                    if remote_only and not self._is_remote(job):
                        continue

                    # Filter by date (Greenhouse 'updated_at' is robust)
                    if job.get("updated_at"):
                        # Handle varied formats if needed, but usually ISO
                        try:
                            job_date = datetime.fromisoformat(
                                job["updated_at"].replace("Z", "+00:00")
                            )
                            if job_date < cutoff_date:
                                continue
                        except ValueError:
                            pass  # Skip date check if format fails

                    yield self._to_raw_job(job, company)

            except Exception as e:
                self.logger.warning(f"Failed to scrape {company}: {e}")
                continue

    async def _get_company_jobs(self, company: str) -> list[dict]:
        """Get all jobs for a specific company board"""
        url = f"{self.base_url}/{company}/jobs"

        try:
            data = await self._make_request(url)
            return data.get("jobs", [])
        except ScraperError:
            return []
        # Greenhouse sometimes wraps differently or returns 404 if company invalid
        except Exception:
            return []

    async def get_job_details(self, external_id: str) -> RawJob:
        """Get full job details including description"""
        # external_id format: "company_id:job_id"
        try:
            company, job_id = external_id.split(":")
        except ValueError as e:
            raise ScraperError(f"Invalid external_id format: {external_id}") from e

        url = f"{self.base_url}/{company}/jobs/{job_id}"
        data = await self._make_request(url)

        return self._to_raw_job(data, company)

    def _to_raw_job(self, data: dict, company: str) -> RawJob:
        """Convert Greenhouse API response to RawJob"""
        content = data.get("content", "")
        clean_desc = self._clean_html(content)
        return RawJob(
            external_id=f"{company}:{data['id']}",
            source=self.source_name,
            title=data["title"],
            company_name=data.get("company", {}).get("name", company.title()),
            location=data.get("location", {}).get("name", ""),
            description=clean_desc,
            requirements=self._extract_requirements(content),
            tech_stack=self._detect_tech_stack(clean_desc),
            salary_range=None,  # Greenhouse doesn't expose salary in API
            posted_date=datetime.fromisoformat(
                data["updated_at"].replace("Z", "+00:00")
            )
            if data.get("updated_at")
            else None,
            apply_url=data.get("absolute_url", ""),
            remote_type=self._detect_remote(data),
            employment_type=data.get("employment_type"),
            raw_data=data,
        )

    def _clean_html(self, html: str) -> str:
        """Strip HTML tags and clean whitespace"""
        if not html:
            return ""
        soup = bs4.BeautifulSoup(html, "html.parser")
        return soup.get_text(separator="\n", strip=True)

    def _extract_requirements(self, content: str) -> list[str]:
        """Extract requirements from job description"""
        # Look for sections like "Requirements", "Qualifications", etc.
        # This is a naive implementation; usually requires NLP or regex
        _ = content
        return []

    def _matches_keywords(self, job: dict, keywords: list[str]) -> bool:
        """Check if job title matches any keywords"""
        title = job.get("title", "").lower()
        return any(k.lower() in title for k in keywords)

    def _matches_location(self, job: dict, location: str) -> bool:
        """Check if job location matches"""
        job_loc = job.get("location", {}).get("name", "").lower()
        return location.lower() in job_loc

    def _is_remote(self, job: dict) -> bool:
        """Check if job is remote"""
        loc = job.get("location", {}).get("name", "").lower()
        # Greenhouse often puts 'Remote' in location
        return "remote" in loc

    def _detect_remote(self, data: dict) -> str | None:
        if self._is_remote(data):
            return "remote"
        return "onsite"
