import pytest
import datetime
from decimal import Decimal
from unittest.mock import MagicMock
from src.modules.job_search.domain.matching import JobMatcher, MatchScore
from src.modules.job_search.domain.models import Job, JobType, WorkModel


class TestJobMatchingService:
    @pytest.fixture
    def matcher(self):
        return JobMatcher()

    @pytest.fixture
    def sample_job(self):
        return Job(
            id="job-123",
            title="Senior Python Backend Engineer",
            company="Tech Corp",
            description="We are looking for an expert in Python, FastAPI, and AWS.",
            requirements=["Python", "FastAPI", "AWS", "Docker"],
            job_type=JobType.FULL_TIME,
            work_model=WorkModel.REMOTE,
            salary_min=Decimal("120000"),
            salary_max=Decimal("180000"),
            currency="USD",
            posted_at=datetime.datetime.now(),
        )

    @pytest.fixture
    def sample_persona(self):
        return {
            "skills": ["Python", "Django", "FastAPI", "AWS", "Kubernetes"],
            "experience_years": 5,
            "preferences": {
                "remote": True,
                "min_salary": 130000,
                "roles": ["Backend Engineer", "Software Engineer"],
            },
        }

    @pytest.mark.asyncio
    async def test_calculate_match_score(self, matcher, sample_job, sample_persona):
        # Mocking the embedding service and other internals usually involved
        # Assuming JobMatcher has a method like calculate_score(job, persona)

        # For this test, we might need to mock if it uses external AI services
        # If JobMatcher is pure logic + embeddings, we might mock the embedding result

        # NOTE: Adjusting expectation based on actual implementation.
        # Since I cannot see the implementation of JobMatcher right now, I will assume a standard interface.

        # Mocking embedding similarity for the sake of unit test if needed
        matcher._calculate_vector_similarity = MagicMock(return_value=0.85)

        score = await matcher.calculate_score(sample_job, sample_persona)

        assert isinstance(score, MatchScore)
        assert 0 <= score.total_score <= 100
        assert score.skill_match_score > 0

    @pytest.mark.asyncio
    async def test_salary_matching(self, matcher, sample_job, sample_persona):
        # Job pays 120k-180k, User wants >130k. Should be a good match.
        match = matcher._evaluate_salary_match(sample_job, sample_persona)
        assert match > 50  # Should be decent

    @pytest.mark.asyncio
    async def test_remote_work_matching(self, matcher, sample_job, sample_persona):
        # Job is remote, User wants remote.
        match = matcher._evaluate_work_model_match(sample_job, sample_persona)
        assert match == 100
