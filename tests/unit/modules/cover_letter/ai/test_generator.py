from unittest.mock import AsyncMock, MagicMock

import pytest

from src.modules.cover_letter.ai.generator import (
    AlternativesList,
    CoverLetterGenerator,
    CoverLetterPreferences,
)
from src.modules.cover_letter.domain.models import Emphasis, Length, Tone
from src.modules.job_search.domain.models import Job
from src.modules.persona.domain.models import Persona


@pytest.fixture
def mock_gemini_client():
    return AsyncMock()


@pytest.fixture
def generator(mock_gemini_client):
    return CoverLetterGenerator(mock_gemini_client)


@pytest.mark.asyncio
async def test_generate_success(generator, mock_gemini_client):
    mock_gemini_client.generate_text.side_effect = [
        "Dynamic Company Research",
        "Dear Hiring Manager, I am excited to apply for the role at Stellar Tech...",
    ]

    job = MagicMock(spec=Job)
    job.company = "Stellar Tech"
    job.title = "Software Engineer"
    job.description = "We need an engineer."
    job.raw_data = {"requirements": ["Python", "AWS"]}

    persona = MagicMock(spec=Persona)
    persona.full_name = "Jane Doe"

    mock_skill = MagicMock()
    mock_skill.name = "Python"
    persona.skills = [mock_skill]
    persona.experiences = []

    preferences = CoverLetterPreferences(
        tone=Tone.PROFESSIONAL, length=Length.MEDIUM, emphasis=[Emphasis.SKILLS]
    )

    result = await generator.generate(job, persona, preferences)

    assert "content" in result
    assert "prompt_v" in result
    assert result["quality_metrics"]["company_mentioned"] is True
    assert mock_gemini_client.generate_text.call_count == 2


@pytest.mark.asyncio
async def test_regenerate_paragraph(generator, mock_gemini_client):
    full_content = "Paragraph 1\n\nParagraph 2\n\nParagraph 3"
    mock_gemini_client.generate_text.return_value = "New Paragraph 2"

    job = MagicMock(spec=Job)
    job.title = "Engineer"
    job.company = "Tech"

    updated_content = await generator.regenerate_paragraph(
        full_content, 1, "Make it more technical", job
    )

    assert "New Paragraph 2" in updated_content
    assert "Paragraph 1" in updated_content
    assert "Paragraph 3" in updated_content


@pytest.mark.asyncio
async def test_get_alternatives(generator, mock_gemini_client):
    mock_result = AlternativesList(alternatives=["Alt 1", "Alt 2"])
    mock_gemini_client.generate_structured.return_value = mock_result

    alts = await generator.get_alternatives("Original sentence", count=2)

    assert len(alts) == 2
    assert alts[0] == "Alt 1"


@pytest.mark.asyncio
async def test_adjust_tone(generator, mock_gemini_client):
    mock_gemini_client.generate_text.return_value = "Enthusiastic version"

    result = await generator.adjust_tone("Original", Tone.ENTHUSIASTIC)

    assert result == "Enthusiastic version"
    mock_gemini_client.generate_text.assert_called_once()
