from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

from src.modules.job_search.infrastructure.scrapers.base import (
    BaseScraper,
    RawJob,
    ScraperError,
)


class SmartRecruitersScraper(BaseScraper):
    """Scraper for SmartRecruiters ATS job boards"""

    source_name = "smartrecruiters"
    base_url = "https://api.smartrecruiters.com/v1/companies"

    COMPANY_BOARDS = ["square", "visa", "ubisoft", "skechers"]

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

                    if job.get("releasedDate"):
                        try:
                            job_date = datetime.fromisoformat(
                                job["releasedDate"].replace("Z", "+00:00")
                            )
                            if job_date < cutoff_date:
                                continue
                        except ValueError:
                            pass

                    yield self._to_raw_job(job, company)
            except Exception as e:
                self.logger.warning(f"Failed to scrape {company}: {e}")
                continue

    async def _get_company_jobs(self, company: str) -> list[dict]:
        url = f"{self.base_url}/{company}/postings"
        try:
            data = await self._make_request(url)
            return data.get("content", [])
        except ScraperError:
            return []
        except Exception:
            return []

    async def get_job_details(self, external_id: str) -> RawJob:
        company, job_id = external_id.split(":")
        url = f"{self.base_url}/{company}/postings/{job_id}"
        data = await self._make_request(url)
        return self._to_raw_job(data, company)

    def _to_raw_job(self, data: dict, company: str) -> RawJob:
        return RawJob(
            external_id=f"{company}:{data['id']}",
            source=self.source_name,
            title=data["name"],
            company_name=data.get("company", {}).get("name", company.title()),
            location=data.get("location", {}).get("city", "")
            + ", "
            + data.get("location", {}).get("country", ""),
            description=data.get("jobAd", {})
            .get("sections", {})
            .get("jobDescription", {})
            .get("text", ""),  # Parsing required
            requirements=[],
            salary_range=data.get("compensation", {}).get("min", "")
            + "-"
            + data.get("compensation", {}).get("max", "")
            if data.get("compensation")
            else None,
            posted_date=datetime.fromisoformat(
                data["releasedDate"].replace("Z", "+00:00")
            )
            if data.get("releasedDate")
            else None,
            apply_url=f"https://jobs.smartrecruiters.com/{company}/{data['id']}",
            remote_type="remote"
            if data.get("location", {}).get("remote")
            else "onsite",
            employment_type=data.get("typeOfEmployment", {}).get("label"),
            raw_data=data,
        )

    def _matches_keywords(self, job: dict, keywords: list[str]) -> bool:
        title = job.get("name", "").lower()
        return any(k.lower() in title for k in keywords)

    def _matches_location(self, job: dict, location: str) -> bool:
        city = job.get("location", {}).get("city", "")
        return location.lower() in city.lower()

    def _is_remote(self, job: dict) -> bool:
        return job.get("location", {}).get("remote", False)
