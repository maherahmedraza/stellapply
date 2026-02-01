from collections.abc import AsyncIterator

from src.modules.job_search.infrastructure.scrapers.base import (
    BaseScraper,
    RawJob,
    ScraperError,
)


class BambooHRScraper(BaseScraper):
    """Scraper for BambooHR job boards"""

    source_name = "bamboohr"
    base_url = "https://{company}.bamboohr.com/jobs/embed"

    COMPANY_BOARDS = [
        "change",
        "fabfitfun",
        "ziprecruiter",  # Examples
    ]

    async def search_jobs(
        self,
        keywords: list[str],
        location: str | None = None,
        remote_only: bool = False,
        posted_within_days: int = 7,
    ) -> AsyncIterator[RawJob]:
        _ = remote_only
        _ = posted_within_days

        for company in self.COMPANY_BOARDS:
            try:
                jobs = await self._get_company_jobs(company)
                for job in jobs:
                    if not self._matches_keywords(job, keywords):
                        continue
                    # BambooHR JSON is limited, location needs parsing
                    if location and not self._matches_location(job, location):
                        continue

                    # BambooHR public feed often lacks dates, assume recent?
                    # Or skip date check if missing.
                    if job.get("date"):
                        # Date parsing depends on format
                        pass

                    yield self._to_raw_job(job, company)
            except Exception as e:
                self.logger.warning(f"Failed to scrape {company}: {e}")
                continue

    async def _get_company_jobs(self, company: str) -> list[dict]:
        url = f"https://{company}.bamboohr.com/jobs/embed/?json=1"
        try:
            data = await self._make_request(url)
            return data.get("jobs", []) if isinstance(data, dict) else []
        except ScraperError:
            return []
        except Exception:
            return []

    async def get_job_details(self, external_id: str) -> RawJob:
        # BambooHR embed feed doesn't give full details easily
        # without scraping HTML page
        # external_id = "company:job_id"
        company, job_id = external_id.split(":")
        # We might need to fetch the HTML page for true details
        # For now, we reuse list data if stored or fail
        raise NotImplementedError(
            "BambooHR deep scrape requires HTML parsing of job page"
        )

    def _to_raw_job(self, data: dict, company: str) -> RawJob:
        return RawJob(
            external_id=f"{company}:{data['id']}",
            source=self.source_name,
            title=data["jobOpeningName"],
            company_name=company.title(),
            location=data.get("location", {}).get("city", "")
            + ", "
            + data.get("location", {}).get("state", ""),
            description="",  # Not in JSON embed
            requirements=[],
            salary_range=None,
            posted_date=None,  # Not consistently available in embed
            apply_url=f"https://{company}.bamboohr.com/jobs/view.php?id={data['id']}",
            remote_type=None,
            employment_type=None,
            raw_data=data,
        )

    def _matches_keywords(self, job: dict, keywords: list[str]) -> bool:
        title = job.get("jobOpeningName", "").lower()
        return any(k.lower() in title for k in keywords)

    def _matches_location(self, job: dict, location: str) -> bool:
        city = job.get("location", {}).get("city", "")
        return location.lower() in city.lower()
