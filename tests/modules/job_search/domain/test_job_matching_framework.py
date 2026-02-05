import pytest
import uuid
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock

from src.modules.job_search.domain.job_matching_framework import (
    JobMatchingFramework,
    MatchLevel,
)
from src.modules.job_search.domain.models import Job
from src.modules.persona.domain.models import (
    Persona,
    Experience,
    Skill,
    WorkAuthorization,
    RemotePreference,
)


@pytest.fixture
def mock_embedding_service():
    service = MagicMock()
    service.embed_text = AsyncMock(return_value=[0.1] * 768)
    return service


@pytest.fixture
def mock_persona_repo():
    return AsyncMock()


@pytest.fixture
def mock_job_repo():
    return AsyncMock()


@pytest.fixture
def framework(mock_embedding_service, mock_persona_repo, mock_job_repo):
    return JobMatchingFramework(
        embedding_service=mock_embedding_service,
        persona_repository=mock_persona_repo,
        job_repository=mock_job_repo,
    )


@pytest.fixture
def sample_persona():
    persona_id = uuid.uuid4()
    persona = Persona(
        id=persona_id,
        user_id=uuid.uuid4(),
        full_name="John Doe",
        email="john@example.com",
        location_city="San Francisco",
        work_authorization=WorkAuthorization.CITIZEN,
        remote_preference=RemotePreference.REMOTE,
        summary_embedding=[0.1] * 768,
    )

    # Add experience
    persona.experiences = [
        Experience(
            id=uuid.uuid4(),
            persona_id=persona_id,
            company_name="Tech Corp",
            job_title="Software Engineer",
            start_date=date(2020, 1, 1),
            end_date=date(2023, 1, 1),
            description="Working with Python and React",
            experience_embedding=[0.1] * 768,
        )
    ]

    # Add skills
    persona.skills = [
        Skill(
            id=uuid.uuid4(), persona_id=persona_id, name="Python", proficiency_level=5
        ),
        Skill(
            id=uuid.uuid4(), persona_id=persona_id, name="React", proficiency_level=4
        ),
    ]

    persona.behavioral_answers = []

    return persona


@pytest.fixture
def sample_job():
    job_id = uuid.uuid4()
    return Job(
        id=job_id,
        title="Senior Python Developer",
        company="Innovation Labs",
        location="San Francisco",
        description="We are looking for a Senior Python Developer with 5+ years of experience. Skills: Python, AWS, SQL.",
        description_embedding=[0.1] * 768,
        work_setting="remote",
        url="https://example.com/job",
    )


@pytest.mark.asyncio
async def test_calculate_match_excellent(
    framework, mock_persona_repo, mock_job_repo, sample_persona, sample_job
):
    # Setup mocks
    mock_persona_repo.get_by_id.return_value = sample_persona
    mock_job_repo.get_by_id.return_value = sample_job

    # Run matching
    result = await framework.calculate_match(sample_persona.id, sample_job.id)

    # Verify
    assert result.job_id == sample_job.id
    assert result.score > 0
    assert isinstance(result.match_level, MatchLevel)
    assert len(result.explanation.strengths) > 0
    assert "python" in [s.lower() for s in result.matching_skills]


@pytest.mark.asyncio
async def test_hard_requirement_location_mismatch(
    framework, mock_persona_repo, mock_job_repo, sample_persona, sample_job
):
    # Setup mismatch: Persona wants onsite, Job is remote but in different city
    sample_persona.remote_preference = RemotePreference.ONSITE
    sample_persona.location_city = "New York"
    sample_job.work_setting = "onsite"
    sample_job.location = "San Francisco"

    mock_persona_repo.get_by_id.return_value = sample_persona
    mock_job_repo.get_by_id.return_value = sample_job

    result = await framework.calculate_match(sample_persona.id, sample_job.id)

    # Should have a lower score due to location mismatch
    # Find the location requirement match
    loc_match = next(
        rm
        for rm in result.explanation.requirement_matches
        if rm.requirement_name == "Location"
    )
    assert loc_match.is_met is False


@pytest.mark.asyncio
async def test_skill_matching_exact_and_semantic(
    framework, mock_persona_repo, mock_job_repo, sample_persona, sample_job
):
    # Job requires Python (exact) and FastAPI (semantic via SkillTaxonomy)
    sample_job.description = "Required: Python, FastAPI"

    mock_persona_repo.get_by_id.return_value = sample_persona
    mock_job_repo.get_by_id.return_value = sample_job

    result = await framework.calculate_match(sample_persona.id, sample_job.id)

    # Python should be exact
    python_match = next(
        sm
        for sm in result.explanation.skill_matches
        if sm.skill_name.lower() == "python"
    )
    assert python_match.match_type == "exact"

    # FastAPI should be semantic (linked to Python in our mock SkillTaxonomy)
    fastapi_match = next(
        sm
        for sm in result.explanation.skill_matches
        if sm.skill_name.lower() == "fastapi"
    )
    assert fastapi_match.match_type == "semantic"
