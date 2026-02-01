import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.modules.persona.domain.models import Persona
from src.modules.resume.ai.gemini_enhancer import EnhancedBullet, ResumeEnhancer


@pytest.fixture
def mock_gemini_client():
    return AsyncMock()


@pytest.fixture
def enhancer(mock_gemini_client):
    return ResumeEnhancer(mock_gemini_client)


@pytest.mark.asyncio
async def test_enhance_bullet_point_success(enhancer, mock_gemini_client):
    mock_result = EnhancedBullet(
        enhanced="Enhanced bullet",
        action_verb="Managed",
        metrics_added=True,
        keywords_included=["Python"],
        confidence_score=0.9,
    )
    mock_gemini_client.generate_structured.return_value = mock_result

    with (
        patch(
            "src.modules.resume.ai.gemini_enhancer.redis_provider.get",
            return_value=None,
        ),
        patch(
            "src.modules.resume.ai.gemini_enhancer.redis_provider.set",
            return_value=None,
        ),
    ):
        result = await enhancer.enhance_bullet_point("Original bullet", "Context")

        assert isinstance(result, EnhancedBullet)
        assert result.enhanced == "Enhanced bullet"
        assert result.metrics_added is True


@pytest.mark.asyncio
async def test_enhance_bullet_point_fallback(enhancer, mock_gemini_client):
    mock_gemini_client.generate_structured.side_effect = Exception("AI Error")

    with patch(
        "src.modules.resume.ai.gemini_enhancer.redis_provider.get", return_value=None
    ):
        result = await enhancer.enhance_bullet_point("Original bullet")

        assert result.enhanced == "Original bullet"
        assert result.confidence_score == 0.0


@pytest.mark.asyncio
async def test_generate_professional_summary(enhancer, mock_gemini_client):
    mock_gemini_client.generate_text.return_value = "Experienced professional summary."

    persona = MagicMock(spec=Persona)
    persona.full_name = "John Doe"

    mock_skill1 = MagicMock()
    mock_skill1.name = "Python"
    mock_skill2 = MagicMock()
    mock_skill2.name = "AI"
    persona.skills = [mock_skill1, mock_skill2]

    mock_exp = MagicMock()
    mock_exp.company_name = "Tech Co"
    mock_exp.job_title = "Engineer"
    mock_exp.achievements = ["Did stuff"]
    persona.experiences = [mock_exp]

    persona.career_preference = MagicMock()
    persona.career_preference.target_titles = ["Senior Engineer"]
    persona.user_id = "user-123"

    with (
        patch(
            "src.modules.resume.ai.gemini_enhancer.redis_provider.get",
            return_value=None,
        ),
        patch(
            "src.modules.resume.ai.gemini_enhancer.redis_provider.set",
            return_value=None,
        ),
    ):
        summary = await enhancer.generate_professional_summary(persona)

        assert summary == "Experienced professional summary."
        mock_gemini_client.generate_text.assert_called_once()


@pytest.mark.asyncio
async def test_enhance_bullet_point_cached(enhancer, mock_gemini_client):
    cached_response = {
        "enhanced": "Cached bullet",
        "action_verb": "Led",
        "metrics_added": True,
        "keywords_included": [],
        "confidence_score": 1.0,
    }

    with patch(
        "src.modules.resume.ai.gemini_enhancer.redis_provider.get",
        return_value=json.dumps(cached_response),
    ):
        result = await enhancer.enhance_bullet_point("Original bullet")

        assert result.enhanced == "Cached bullet"
        mock_gemini_client.generate_structured.assert_not_called()
