import pytest
import uuid
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock

from src.modules.job_search.domain.job_matching_framework import (
    JobMatchingFramework,
    JobMatchResult,
    MatchLevel,
)
from src.modules.persona.domain.models import Persona, Experience, Skill, SkillSource
from src.modules.job_search.domain.models import Job

# --- Mock Data ---


@pytest.fixture
def mock_embedding_service():
    service = MagicMock()
    # Return a fixed vector for simplicity
    service.embed_text = AsyncMock(return_value=[0.1] * 768)
    return service


@pytest.fixture
def mock_persona_repo():
    repo = MagicMock()
    return repo


@pytest.fixture
def mock_job_repo():
    repo = MagicMock()
    return repo


@pytest.fixture
def sample_persona():
    persona = Persona(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        full_name="Alice Test",
        email="alice@test.com",
        location_city="New York",
        # location_state="NY", # Assuming state exists, used country in failed test
        # work_authorization="Citizen", # This might also be missing or different, checking model below
        summary_active="Experienced Python Developer",
    )
    # Monkeypatch attributes that might be missing from __init__ but used in framework
    persona.location_country = "USA"
    persona.work_authorization = "Citizen"
    persona.willing_to_relocate = False
    # Skills
    persona.skills = [
        Skill(name="Python", proficiency_level=5, source=SkillSource.USER_DECLARED),
        Skill(name="FastAPI", proficiency_level=4, source=SkillSource.USER_DECLARED),
    ]
    # Experiences
    persona.experiences = [
        Experience(
            company_name="Tech Co",
            job_title="Senior Python Developer",
            description_active="Built backend systems with Python and FastAPI.",
            start_date=date(2020, 1, 1),
            end_date=date(2023, 1, 1),
        )
    ]
    return persona


@pytest.fixture
def sample_job():
    job = Job(
        id=uuid.uuid4(),
        title="Senior Python Engineer",
        company="Big Tech",
        location="New York",
        description="We are looking for a Python expert used to FastAPI. 3+ years experience required.",
        url="http://example.com",
        status="active",
    )
    return job


# --- Tests ---


@pytest.mark.asyncio
async def test_perfect_match(
    mock_embedding_service, mock_persona_repo, mock_job_repo, sample_persona, sample_job
):
    # Setup mocks
    mock_persona_repo.get_by_id = AsyncMock(return_value=sample_persona)
    mock_job_repo.get_by_id = AsyncMock(return_value=sample_job)

    framework = JobMatchingFramework(
        embedding_service=mock_embedding_service,
        persona_repository=mock_persona_repo,
        job_repository=mock_job_repo,
    )

    result = await framework.calculate_match(sample_persona.id, sample_job.id)

    assert result is not None
    assert result.match_level in [MatchLevel.EXCELLENT, MatchLevel.GOOD]
    assert result.score > 70
    assert "Python" in result.matching_skills


@pytest.mark.asyncio
async def test_dealbreaker_visa(
    mock_embedding_service, mock_persona_repo, mock_job_repo, sample_persona, sample_job
):
    # Modify job to require sponsorship while persona is NOT authorized (simulated)
    # But wait, logic says if "no sponsorship" in desc and persona NOT authorized -> dealbreaker.
    # Let's verify logic:
    # _check_visa_match: if "no sponsorship" in desc...

    sample_job.description = "Must be US Citizen. No sponsorship available."
    sample_persona.work_authorization = "Visa Holder"  # Not citizen/permanent

    mock_persona_repo.get_by_id = AsyncMock(return_value=sample_persona)
    mock_job_repo.get_by_id = AsyncMock(return_value=sample_job)

    framework = JobMatchingFramework(
        embedding_service=mock_embedding_service,
        persona_repository=mock_persona_repo,
        job_repository=mock_job_repo,
    )

    result = await framework.calculate_match(sample_persona.id, sample_job.id)

    # Should be heavily penalized
    assert result.score < 50
    # Check if "Work Authorization" is in gaps
    assert any("Work Authorization" in gap for gap in result.explanation.gaps)


@pytest.mark.asyncio
async def test_missing_skills(
    mock_embedding_service, mock_persona_repo, mock_job_repo, sample_persona, sample_job
):
    # Job requires Java, Persona has Python
    sample_job.description = "Looking for Java developer with Spring Boot experience."

    mock_persona_repo.get_by_id = AsyncMock(return_value=sample_persona)
    mock_job_repo.get_by_id = AsyncMock(return_value=sample_job)

    framework = JobMatchingFramework(
        embedding_service=mock_embedding_service,
        persona_repository=mock_persona_repo,
        job_repository=mock_job_repo,
    )

    result = await framework.calculate_match(sample_persona.id, sample_job.id)

    assert result.score < 80  # Should be lower than perfect match
    assert "Java" in result.missing_skills
