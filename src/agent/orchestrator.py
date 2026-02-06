import asyncio
import logging
from datetime import datetime
from uuid import UUID
from typing import List, Optional

from src.agent.brain import AgentBrain
from src.agent.agents.scout import ScoutAgent
from src.agent.agents.registrar import RegistrarAgent
from src.agent.agents.applicant import ApplicantAgent
from src.agent.browser.pool import BrowserPool
from src.agent.models.pipeline import (
    PipelineConfig,
    PipelineResult,
    PipelineState,
    DiscoveredJob,
    ScoredJob,
    ApplicationAttempt,
)
from src.modules.profile.schemas import UserProfileResponse

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Coordinates the full autonomous job application pipeline for a user.
    Pipeline stages: DISCOVER -> FILTER -> PREPARE -> APPLY -> RECORD
    """

    def __init__(self, user_id: UUID, session_id: UUID, browser_pool: BrowserPool):
        self.user_id = user_id
        self.session_id = session_id
        self.brain = None  # Lazily loaded
        self.browser_pool = browser_pool
        self.state = PipelineState(
            session_id=session_id, stage="initialized", last_updated=datetime.now()
        )
        self._profile: Optional[UserProfileResponse] = None

    async def run_pipeline(
        self, config: PipelineConfig, profile: UserProfileResponse
    ) -> PipelineResult:
        """
        Full pipeline execution.
        """
        self._profile = profile
        self.brain = AgentBrain(profile)  # Instantiate Brain with profile
        self.state.stage = "running"
        self._update_state(
            stage="discovering", progress=0.1, action="Starting job discovery"
        )

        results = []
        discovered_jobs = []
        ranked_jobs = []

        try:
            # STAGE 1: DISCOVER
            discovered_jobs = await self._discover_jobs(config)
            self._update_state(
                stage="filtering",
                progress=0.3,
                action=f"Found {len(discovered_jobs)} jobs. Filtering...",
            )

            # STAGE 2: FILTER & RANK
            ranked_jobs = await self._filter_and_rank(discovered_jobs, config)
            self._update_state(
                stage="applying",
                progress=0.4,
                action=f"Applying to top {len(ranked_jobs[: config.max_applications])} jobs",
            )

            # STAGE 3: APPLY
            total_to_apply = min(len(ranked_jobs), config.max_applications)
            self.state.total_jobs = total_to_apply

            for i, job in enumerate(ranked_jobs[:total_to_apply]):
                self.state.current_job_index = i + 1
                self._update_state(
                    stage="applying",
                    progress=0.4 + (0.5 * (i / total_to_apply)),
                    action=f"Applying to {job.company}: {job.title}",
                )

                # 3a. APPROVAL GATE
                if config.require_approval:
                    approved = await self._request_approval(job)
                    if not approved:
                        results.append(
                            ApplicationAttempt(
                                job=job,
                                status="skipped_by_user",
                                started_at=datetime.now(),
                                completed_at=datetime.now(),
                                duration_seconds=0,
                            )
                        )
                        continue

                # 3b. CHECK REGISTRATION & REGISTER
                portal_domain = self._extract_domain(job.url)
                # For now assume we might need to register.
                # Optimization: Check if we have credentials or session cookies.
                # Here we skip granular check and let Registrar handle if needed or Applicant handle.
                # Ideally:
                # if not await self._has_portal_session(portal_domain):
                #      reg_result = await self._register_on_portal(job, portal_domain) ...

                # 3c. APPLY
                app_result = await self._apply_to_job(job, config.resume_file_path)
                results.append(app_result)

                # 3d. RECORD
                await self._record_application(job, app_result)

                # 3e. RATE LIMITING
                if i < total_to_apply - 1:
                    await self._pace_between_applications()

            self.state.stage = "completed"
            self._update_state(
                stage="completed", progress=1.0, action="Pipeline completed"
            )

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self.state.stage = "failed"
            self.state.errors.append(str(e))
            self._update_state(
                stage="failed",
                progress=self.state.progress_percentage,
                action="Pipeline failed",
            )

        return PipelineResult(
            session_id=self.session_id,
            total_discovered=len(discovered_jobs),
            total_matched=len(ranked_jobs),
            total_applied=sum(1 for r in results if r.status == "success"),
            total_failed=sum(1 for r in results if r.status == "failed"),
            total_skipped=sum(1 for r in results if r.status.startswith("skipped")),
            attempts=results,
            started_at=datetime.now(),  # Placeholder, track actual start
            completed_at=datetime.now(),
        )

    async def _discover_jobs(self, config: PipelineConfig) -> List[DiscoveredJob]:
        """
        Run ScoutAgent on each source.
        """
        jobs = []
        scout = ScoutAgent(self.user_id, self.browser_pool)

        for source in config.search_sources:
            result = await scout.run(
                {
                    "url": source.url,
                    "search_criteria": config.filters.model_dump(),
                    "profile": self._profile,
                }
            )

            if result.get("status") == "success":
                raw_data = result.get("data", {}).get("jobs", [])
                for j in raw_data:
                    # Convert raw dict to DiscoveredJob
                    # Basic validation/cleaning
                    jobs.append(
                        DiscoveredJob(
                            title=j.get("title", "Unknown"),
                            company=j.get("company", "Unknown"),
                            url=j.get("url", ""),
                            location=j.get("location"),
                            salary_range=j.get("salary"),
                            description_snippet=j.get("description_snippet", ""),
                            source_platform=source.platform,
                        )
                    )
        return jobs

    async def _filter_and_rank(
        self, jobs: List[DiscoveredJob], config: PipelineConfig
    ) -> List[ScoredJob]:
        """
        Filter jobs using brain and criteria.
        """
        scored_jobs = []
        # In a real impl, batch this or do it in parallel
        for job in jobs:
            # Brain power to score
            match_score = await self.brain.score_job(job, self._profile)

            if match_score >= config.filters.min_match_score:
                scored_jobs.append(
                    ScoredJob(
                        **job.model_dump(),
                        match_score=match_score,
                        match_reasons=["Matches skills"],
                        red_flags=[],
                    )
                )

        # Sort by score
        scored_jobs.sort(key=lambda x: x.match_score, reverse=True)
        return scored_jobs

    async def _request_approval(self, job: ScoredJob) -> bool:
        """
        Stub for approval gate.
        """
        # In real system: create DB record, wait for API call to approve
        # For autonomous mode without UI hooked up, we default True or use config
        return True

    async def _apply_to_job(
        self, job: ScoredJob, resume_path: str | None
    ) -> ApplicationAttempt:
        start_time = datetime.now()
        applicant = ApplicantAgent(self.user_id, self.browser_pool)

        payload = {
            "job_url": job.url,
            "resume_file": resume_path,
            "profile": self._profile,
        }

        result = await applicant.run(payload)

        status = "success" if result.get("status") == "success" else "failed"

        return ApplicationAttempt(
            job=job,
            status=status,
            error=result.get("error"),
            started_at=start_time,
            completed_at=datetime.now(),
            duration_seconds=(datetime.now() - start_time).total_seconds(),
            fields_filled=result.get("data"),
        )

    async def _record_application(self, job: ScoredJob, result: ApplicationAttempt):
        """
        Persist result to DB.
        """
        # Use a service or repository to save
        # ApplicationAttemptEntity and update Application table
        pass

    async def _pace_between_applications(self):
        import random

        delay = random.uniform(30, 60)
        logger.info(f"Pacing: Sleeping for {delay:.1f} seconds...")
        await asyncio.sleep(delay)

    def _update_state(self, stage: str, progress: float, action: str):
        self.state.stage = stage
        self.state.progress_percentage = progress
        self.state.current_action = action
        self.state.last_updated = datetime.now()
        # Trigger DB write or event emit
        logger.info(f"[{stage.upper()}] {action} ({progress * 100:.1f}%)")

    def _extract_domain(self, url: str) -> str:
        from urllib.parse import urlparse

        return urlparse(url).netloc
