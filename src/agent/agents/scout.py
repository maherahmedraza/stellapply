import json
import logging
from typing import Any, Dict, List, Set

from src.agent.agents.base import BaseAgent
from src.agent.agents.scout_helpers import SearchURLBuilder
from src.agent.models.entities import DiscoveredJob
from src.modules.profile.schemas import UserProfileResponse

logger = logging.getLogger(__name__)


class ScoutAgent(BaseAgent):
    """
    Discovers jobs by navigating real job board websites.
    Supports multiple platforms with platform-specific strategies.
    """

    def __init__(self, user_id, task_id):
        super().__init__(user_id, task_id)
        self.discovered_jobs: List[DiscoveredJob] = []
        self.max_jobs_per_source = 20
        self.visited_urls: Set[str] = set()

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute job discovery.

        payload: {
            "sources": [
                {"platform": "linkedin", "search_url": "..."},
                ...
            ],
            "profile": {...},  # UserProfileResponse dict
            "max_results": 50
        }
        """
        await self.start()
        try:
            profile_data = payload.get("profile")

            # Validate/Create Profile Object
            if isinstance(profile_data, dict):
                try:
                    profile = UserProfileResponse(**profile_data)
                except Exception:
                    profile = UserProfileResponse.model_validate(profile_data)
            else:
                profile = profile_data

            # Use SearchURLBuilder if sources not provided or empty
            sources = payload.get("sources", [])
            if not sources and profile:
                sources = SearchURLBuilder.build_urls(profile.search_preferences)
                logger.info(
                    f"Generated {len(sources)} search sources from profile preferences."
                )

            max_results = payload.get("max_results", 50)

            for source in sources:
                try:
                    jobs = await self._scout_source(source)
                    self.discovered_jobs.extend(jobs)
                    logger.info(
                        f"Discovered {len(jobs)} jobs from {source['platform']}"
                    )

                    if len(self.discovered_jobs) >= max_results:
                        break
                except Exception as e:
                    logger.error(
                        f"Scout failed for {source.get('platform', 'unknown')}",
                        exc_info=True,
                    )
                    continue

            # Deduplicate locally (Note: DB persistence handles uniqueness via external_id/url usually)
            # But let's return unique list for this run
            seen_urls = set()
            unique_jobs = []
            for job in self.discovered_jobs:
                if job.url not in seen_urls:
                    seen_urls.add(job.url)
                    unique_jobs.append(job)

            return {
                "status": "success",
                "jobs_found": len(unique_jobs),
                "data": {
                    "jobs": [
                        j.model_dump() if hasattr(j, "model_dump") else j
                        for j in unique_jobs
                    ]
                },
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
        finally:
            await self.stop()

    async def _scout_source(self, source: dict) -> List[DiscoveredJob]:
        """Navigate to a job board and extract listings."""
        platform = source["platform"]
        url = source["search_url"]

        logger.info(f"Navigating to {platform}: {url}")
        await self.browser.navigate(url)
        await self.browser.stealth.random_delay(2000, 4000)

        # Check for cookie consent banners and dismiss
        await self._handle_cookie_banner()

        # Check if login is required
        if await self._is_login_required():
            # Try to restore session (Placeholder for session logic)
            # restored = await self._try_restore_session(platform)
            # if not restored:

            # Request human intervention for login
            response = await self.request_human_help(
                "login_required",
                {"platform": platform, "message": f"Please log in to {platform}"},
            )
            # If user solved it or we proceed anyway (sometimes login covers only part of screen?)
            # Re-check URL or state?
            if not response:
                logger.warning(
                    f"Skipping {platform} - login required / no user response"
                )
                return []

        # Extract job listings from current page
        jobs = await self._extract_jobs_from_page()

        # Pagination: Load more results
        pages_loaded = 1
        max_pages = 3  # Don't go too deep

        while pages_loaded < max_pages and len(jobs) < self.max_jobs_per_source:
            # Look for matching generic 'Next' buttons
            has_next = await self._go_to_next_page()
            if not has_next:
                break

            await self.browser.stealth.random_delay(2000, 5000)
            new_jobs = await self._extract_jobs_from_page()

            if not new_jobs:
                break

            jobs.extend(new_jobs)
            pages_loaded += 1

        return jobs[: self.max_jobs_per_source]

    async def _extract_jobs_from_page(self) -> List[DiscoveredJob]:
        """
        Use Brain to identify and extract job listings from current page.
        """
        # Get DOM + screenshot for the Brain
        dom = await self.browser.get_dom_snapshot()
        # screenshot = await self.browser.take_screenshot() # Captured in memory if needed by brain, but extract_data uses text usually

        # Ask Gemini to extract structured job data
        # We construct a prompt but use the brain's existing extract_data method which wraps the call
        # Or we use a direct generate because extraction prompt is specific.
        # The Brain has `extract_data` which takes content + schema. Let's use that but we might need more context in prompt.
        # `extract_data` is generic. Let's use `extract_data` for now.

        schema = {
            "jobs": [
                {
                    "title": "Job Title",
                    "company": "Company Name",
                    "location": "City, Country or Remote",
                    "url": "Direct URL to the job posting (absolute URL)",
                    "salary_range": "if visible, otherwise null",
                    "job_type": "full_time/part_time/contract or null",
                    "posted_date": "if visible, otherwise null",
                    "description_snippet": "First 200 chars of description if visible",
                }
            ]
        }

        # We need to pass the base URL to help the brain resolve relative links?
        # Actually Brain doesn't resolve links, it sees text. The DOM we send has attributes.
        # Ideally we'd optimize the DOM snippet to include hrefs clearly.
        # Our `get_dom_snapshot` returns a simplified structure.

        extracted_data = await self.brain.extract_data(dom, schema)

        raw_jobs = extracted_data.get("jobs", [])

        # Convert to DiscoveredJob objects
        discovered_jobs = []
        base_url = self.browser.page.url

        for rj in raw_jobs:
            # Normalize URL
            job_url = rj.get("url")
            if job_url:
                if not job_url.startswith("http"):
                    # Handle relative
                    from urllib.parse import urljoin

                    job_url = urljoin(base_url, job_url)

            # Simple deduplication check against current run or session
            if job_url in self.visited_urls:
                continue

            if job_url:
                self.visited_urls.add(job_url)

            # Map to DiscoveredJob (Entity)
            # Note: DiscoveredJob is an SQLAlchemy model in entities.py, but we might want a Pydantic schema here for internal use
            # OR we populate the DB model directly?
            # The run method returns dicts. Let's use specific Pydantic schema if available, or just dicts for now
            # and let the caller handle persistence.
            # The requirements said `self.discovered_jobs: list[DiscoveredJob] = []`
            # Let's instantiate the model. DiscoveredJob is from entities.py (DB model).
            # Ideally we decouple, but let's follow the implied pattern.

            # We need a session_id? ScoutAgent doesn't necessarily know the session_id unless passed in payload or managed?
            # BaseAgent doesn't inherently track a DB session ID.
            # For this MVP, we create an object that *looks* like DiscoveredJob but might not be attached to DB yet.
            # Or simpler: use a Pydantic model for data transport.

            # Let's assume we return a simple object or dict for now,
            # as DiscoveredJob requires session_id etc which might not be ready.
            # But wait, signature is `list[DiscoveredJob]`.
            # I'll create a simple data holder class or use the entity with None for IDs?

            # To be safe and avoid DB dependency issues here, I will use a Pydantic model for internal representation
            # inside the agent, or just plain objects.
            # However the requirement specifically typed it as `DiscoveredJob`.
            # Let's assign attributes to a simple class or dict wrapper if entities.py model is strict.
            # Checking Entities.py: `DiscoveredJob` is a generic BaseModel (likely SQLAlchemy).

            # Let's use a dict-like object for result compatible with the return type hint `DiscoveredJob`.
            # Actually, let's look at `DiscoveredJob` from `src.agent.models.entities`.
            # It inherits from `BaseModel` (SQLAlchemy).
            # We can instantiate it without session_id for temporary storage, but save will fail.

            job = DiscoveredJob(
                title=rj.get("title", "Unknown"),
                company=rj.get("company", "Unknown"),
                url=job_url or "",
                location=rj.get("location"),
                description_snippet=rj.get("description_snippet"),
                source_platform=self.browser.page.url.split("/")[2],  # naive host
                # session_id, match_score, etc. to be filled later
            )
            discovered_jobs.append(job)

        return discovered_jobs

    async def _handle_cookie_banner(self):
        """Dismiss cookie consent popups."""
        cookie_selectors = [
            "button[id*='accept']",
            "button[class*='accept']",
            "button:has-text('Accept')",
            "button:has-text('Akzeptieren')",
            "button:has-text('Accept All')",
            "button:has-text('Alle akzeptieren')",
            "#onetrust-accept-btn-handler",
            ".cookie-consent-accept",
            "[data-testid='cookie-accept']",
            "//button[contains(text(), 'Accept')]",
            "//button[contains(text(), 'Agree')]",
        ]

        # Helper to try clicking
        for selector in cookie_selectors:
            try:
                # Playwright specific: use page.locator or $, verify visibility
                if await self.browser.page.is_visible(selector, timeout=500):
                    logger.info(f"Dismissing cookie banner with selector: {selector}")
                    await self.browser.page.click(selector)
                    await self.browser.stealth.random_delay(500, 1000)
                    return  # Assume one main banner
            except Exception:
                continue

    async def _is_login_required(self) -> bool:
        """Check if current page is a login wall."""
        try:
            url = self.browser.page.url.lower()
            title = await self.browser.page.title()
            title = title.lower()

            indicators = [
                "login",
                "sign in",
                "anmelden",
                "log in",
                "signin",
            ]  # "Einloggen"

            # Simple check
            if any(
                ind in url.split("?")[0] for ind in indicators
            ):  # check usage in path
                return True

            if any(ind in title for ind in indicators):
                # Ensure it's not "Login to Apply" button but actual page title "Login | LinkedIn"
                # Heuristic: Title is usually short on login pages
                if len(title) < 50:
                    return True

            # Check for generic login forms
            # login_form = await self.browser.page.is_visible("input[type='password']")
            # if login_form:
            #     return True

            return False
        except Exception:
            return False

    async def _go_to_next_page(self) -> bool:
        """Find and click 'Next page' or 'Load more' button."""
        next_selectors = [
            "button:has-text('Next')",
            "a:has-text('Next')",
            "button:has-text('Weiter')",
            "a:has-text('Weiter')",
            "[aria-label='Next']",
            "[aria-label='next page']",
            "button:has-text('Load more')",
            "button:has-text('Mehr laden')",
            "button:has-text('Show more')",
            ".pagination-next",
            ".next-page",
            "a[rel='next']",
        ]

        for selector in next_selectors:
            try:
                if await self.browser.page.is_visible(selector, timeout=2000):
                    logger.info(f"Navigating to next page using: {selector}")
                    # Scroll into view
                    element = self.browser.page.locator(selector).first
                    await element.scroll_into_view_if_needed()
                    await self.browser.stealth.random_delay(500, 1000)
                    await element.click()
                    await self.browser.page.wait_for_load_state(
                        "networkidle", timeout=10000
                    )
                    return True
            except Exception:
                continue

        return False
