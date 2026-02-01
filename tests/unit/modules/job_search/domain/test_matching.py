from unittest.mock import AsyncMock
from uuid import uuid4

from src.modules.job_search.domain.matching import JobMatcher, MatchScore
from src.modules.persona.domain.models import (
    Persona,
    WorkAuthorization,
    RemotePreference,
    Skill,
    CareerPreference,
    SkillCategory,
)
from src.modules.job_search.domain.models import Job


@pytest.fixture
def mock_embedding_service():
    service = AsyncMock()
    service.embed_text.return_value = [0.1] * 768
    return service


@pytest.fixture
def mock_persona_repo():
    return AsyncMock()


@pytest.fixture
def mock_job_repo():
    return AsyncMock()


@pytest.fixture
def job_matcher(mock_embedding_service, mock_persona_repo, mock_job_repo):
    return JobMatcher(
        embedding_service=mock_embedding_service,
        persona_repository=mock_persona_repo,
        job_repository=mock_job_repo,
    )


@pytest.fixture
def sample_user_id():
    return uuid4()


@pytest.fixture
def sample_job_id():
    return uuid4()


@pytest.fixture
def sample_persona(sample_user_id):
    persona = Persona(
        user_id=sample_user_id,
        full_name="John Doe",
        email="john@example.com",
        location_city="San Francisco",
        location_country="US",
        work_authorization=WorkAuthorization.CITIZEN,
        remote_preference=RemotePreference.HYBRID,
    )
    # Add skills
    persona.skills = [
        Skill(name="Python", proficiency_level=5, category=SkillCategory.TECHNICAL),
        Skill(name="FastAPI", proficiency_level=4, category=SkillCategory.TECHNICAL),
    ]
    # Add preferences
    persona.career_preference = CareerPreference(
        target_titles=["Software Engineer"],
    )
    return persona


@pytest.fixture
def sample_job(sample_job_id):
    job = Job(
        id=sample_job_id,
        title="Senior Software Engineer",
        company="Tech Corp",
        description="We need a Python expert with FastAPI experience.",
        location="San Francisco",
        url="http://example.com/job",
        raw_data={"skills": ["Python", "FastAPI", "Docker"]},
        status="active",
    )
    # Mock dynamic attributes often used in matching not strictly in model definition if needed
    # But here logic uses raw_data for skills
    job.is_remote = False
    return job


@pytest.mark.asyncio
async def test_calculate_match_happy_path(
    job_matcher,
    mock_persona_repo,
    mock_job_repo,
    sample_user_id,
    sample_job_id,
    sample_persona,
    sample_job,
):
    mock_persona_repo.get_by_user_id.return_value = sample_persona
    mock_job_repo.get_by_id.return_value = sample_job

    match_score = await job_matcher.calculate_match(sample_user_id, sample_job_id)

    assert isinstance(match_score, MatchScore)
    assert match_score.overall_score > 0
    assert "matched based on skills" in match_score.explanation[0].lower()
    assert "Python" in match_score.matching_skills


@pytest.mark.asyncio
async def test_calculate_match_skills_scoring(
    job_matcher,
    mock_persona_repo,
    mock_job_repo,
    sample_user_id,
    sample_job_id,
    sample_persona,
    sample_job,
):
    mock_persona_repo.get_by_user_id.return_value = sample_persona
    mock_job_repo.get_by_id.return_value = sample_job

    # User has Python (5/5) and FastAPI (4/5)
    # Job requires Python, FastAPI, Docker
    # Match: Python + FastAPI
    # Missing: Docker

    match_score = await job_matcher.calculate_match(sample_user_id, sample_job_id)

    assert "Docker" in match_score.missing_skills
    assert "Python" in match_score.matching_skills
    assert match_score.skills_score > 0


@pytest.mark.asyncio
async def test_preference_mismatch_penalty(
    job_matcher,
    mock_persona_repo,
    mock_job_repo,
    sample_user_id,
    sample_job_id,
    sample_persona,
    sample_job,
):
    # Set user preference to REMOTE only
    sample_persona.remote_preference = RemotePreference.REMOTE
    # Job is NOT remote (default mock setup)

    mock_persona_repo.get_by_user_id.return_value = sample_persona
    mock_job_repo.get_by_id.return_value = sample_job

    match_score = await job_matcher.calculate_match(sample_user_id, sample_job_id)

    # Preference score should be lower due to remote mismatch penalty
    assert match_score.preferences_score < 100


@pytest.mark.asyncio
async def test_hard_requirement_bypass(
    job_matcher,
    mock_persona_repo,
    mock_job_repo,
    sample_user_id,
    sample_job_id,
    sample_persona,
    sample_job,
):
    # Current implementation stub returns 0 penalty, so this tests logic flow works
    # If we implemented visa check, we'd test it here.

    mock_persona_repo.get_by_user_id.return_value = sample_persona
    mock_job_repo.get_by_id.return_value = sample_job

    match_score = await job_matcher.calculate_match(sample_user_id, sample_job_id)

    # Asserting no crash and valid score
    assert match_score.overall_score >= 0
