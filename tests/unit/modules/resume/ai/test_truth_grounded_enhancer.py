import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import date

from src.modules.persona.domain.models import (
    Persona,
    Experience,
    Skill,
    SkillCategory,
    SkillSource,
    DegreeType,
)
from src.modules.resume.ai.truth_grounded_enhancer import TruthGroundedEnhancer
from src.modules.resume.domain.truth_grounded_schemas import (
    EnhancementType,
    VerificationStatus,
    EnhancementSuggestionSchema,
    EnhancementResponse,
)


@pytest.fixture
def mock_gemini_client():
    return AsyncMock()


@pytest.fixture
def mock_persona_repo():
    return AsyncMock()


@pytest.fixture
def enhancer(mock_gemini_client, mock_persona_repo):
    return TruthGroundedEnhancer(mock_gemini_client, mock_persona_repo)


@pytest.fixture
def mock_persona():
    persona = MagicMock(spec=Persona)
    persona.id = uuid4()
    persona.user_id = uuid4()

    # Skills
    skill1 = MagicMock(spec=Skill)
    skill1.name = "Python"
    skill1.category = SkillCategory.TECHNICAL

    skill2 = MagicMock(spec=Skill)
    skill2.name = "Docker"
    skill2.category = SkillCategory.TOOL

    persona.skills = [skill1, skill2]

    # Experience
    exp1 = MagicMock(spec=Experience)
    exp1.company_name = "Tech Corp"
    exp1.job_title = "Senior Engineer"
    exp1.start_date = date(2020, 1, 1)
    exp1.end_date = date(2022, 1, 1)
    exp1.skills_used = ["Python", "AWS"]
    exp1.achievements = ["Led a team of 5", "Reduced costs by 20%"]
    exp1.description_active = "Managed software projects"

    persona.experiences = [exp1]
    persona.educations = []
    persona.certifications = []
    persona.projects = []

    return persona


@pytest.mark.asyncio
async def test_build_verification_context(enhancer, mock_persona):
    context = enhancer._build_verification_context(mock_persona)

    assert "python" in context["verified_skills"]
    assert "docker" in context["verified_tools"]
    assert "tech corp" in context["verified_companies"]
    assert "senior engineer" in context["verified_job_titles"]
    assert context["years_of_experience"]["python"] >= 2.0
    assert any("20%" in m for m in context["verified_metrics"])


@pytest.mark.asyncio
async def test_enhance_with_truth_verification_success(
    enhancer, mock_gemini_client, mock_persona_repo, mock_persona
):
    mock_persona_repo.get_by_user_id.return_value = mock_persona

    # Mock Gemini response
    # Note: Adding "5" will trigger NEEDS_CONFIRMATION because it's a new metric
    mock_suggestion = {
        "enhanced_text": "Led a cross-functional team of 5 to success",
        "enhancement_type": "action_verb",
        "confidence": 0.9,
        "changes_made": ["Changed managed to led"],
        "confirmation_question": "Was the team size exactly 5?",
    }

    mock_gemini_client.generate_structured.return_value = EnhancementResponse(
        enhancements=[
            EnhancementSuggestionSchema(
                original_text="Managed a team",
                enhanced_text=mock_suggestion["enhanced_text"],
                enhancement_type=EnhancementType.ACTION_VERB,
                verification_status=VerificationStatus.VERIFIED,  # Raw AI output might say verified
                confidence_score=0.9,
            )
        ]
    )

    # We need to mock the internal call to generate_structured to return what the AI would
    # But our enhancer will RE-VERIFY it.

    results = await enhancer.enhance_with_truth_verification(
        user_id=mock_persona.user_id,
        original_content="Managed a team",
        content_type="bullet_point",
    )

    assert len(results) == 1
    # It should be NEEDS_CONFIRMATION because "5" is a new metric
    assert results[0].verification_status == VerificationStatus.NEEDS_CONFIRMATION
    assert results[0].requires_confirmation is True


@pytest.mark.asyncio
async def test_verify_enhancement_rejects_fabrication(enhancer, mock_persona):
    context = enhancer._build_verification_context(mock_persona)

    # Enhancement adds a skill not in persona (Kubernetes)
    enhancement = {
        "enhanced_text": "Expertly managed Kubernetes clusters in production",
        "enhancement_type": "reword",
        "confidence": 0.9,
        "changes_made": ["Added k8s detail"],
    }

    result = await enhancer._verify_enhancement(
        enhancement=enhancement,
        original_text="Managed servers",
        persona=mock_persona,
        verification_context=context,
    )

    assert result.verification_status == VerificationStatus.REJECTED
    assert "Rejected" in result.verification_notes


@pytest.mark.asyncio
async def test_verify_enhancement_needs_confirmation_for_metrics(
    enhancer, mock_persona
):
    context = enhancer._build_verification_context(mock_persona)

    # Enhancement adds a metric not in persona (15%)
    enhancement = {
        "enhanced_text": "Improved system performance by 15% through optimization",
        "enhancement_type": "quantify",
        "confidence": 0.85,
        "changes_made": ["Added metric"],
        "confirmation_question": "Was the performance improvement exactly 15%?",
    }

    result = await enhancer._verify_enhancement(
        enhancement=enhancement,
        original_text="Improved system performance",
        persona=mock_persona,
        verification_context=context,
    )

    assert result.verification_status == VerificationStatus.NEEDS_CONFIRMATION
    assert result.requires_confirmation is True
    assert result.confirmation_prompt is not None


@pytest.mark.asyncio
async def test_generate_interview_talking_points(enhancer, mock_persona):
    context = enhancer._build_verification_context(mock_persona)
    enhanced_text = "Led development of high-scale python applications at Tech Corp"

    talking_points = enhancer._generate_interview_talking_points(
        enhanced_text, mock_persona, context
    )

    print(f"\nTALKING POINTS: {talking_points}")
    # Should contain points about Python experience or Tech Corp achievements
    assert len(talking_points) > 0
    # The skill name check used lower() in enhancer
    assert any("python" in tp.lower() for tp in talking_points)
