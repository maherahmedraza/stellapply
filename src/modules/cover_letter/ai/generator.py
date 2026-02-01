import logging
import random
from typing import Any, cast

from pydantic import BaseModel, Field

from src.core.ai.gemini_client import GeminiClient
from src.modules.cover_letter.ai.prompts import (
    ADJUST_TONE_PROMPT,
    COVER_LETTER_PROMPT_V1,
    COVER_LETTER_PROMPT_V2,
    GET_ALTERNATIVES_PROMPT,
    REGENERATE_PARAGRAPH_PROMPT,
)
from src.modules.cover_letter.domain.models import Emphasis, Length, Tone
from src.modules.job_search.domain.models import Job
from src.modules.persona.domain.models import Persona

logger = logging.getLogger(__name__)


class CoverLetterPreferences(BaseModel):
    tone: Tone = Tone.PROFESSIONAL
    length: Length = Length.MEDIUM
    emphasis: list[Emphasis] = Field(default_factory=lambda: [Emphasis.SKILLS])
    include_company_research: bool = True


class AlternativesList(BaseModel):
    alternatives: list[str]


class CoverLetterGenerator:
    """Service to generate and refine cover letters using Gemini AI."""

    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client
        self.cache_ttl = 3600  # 1 hour for transient generation parts

    async def _extract_company_research(self, job: Job) -> str:
        """Parses the job description to extract company-specific context."""
        # This is a simplified version; in production, this would use a
        # separate AI call or a research service.
        prompt = f"""
        Extract company values, mission, or recent news from this job description:
        {job.description}
        
        Return a concise summary (100 words max).
        """
        try:
            return await self.client.generate_text(prompt)
        except Exception as e:
            logger.warning(f"Failed to extract company research: {str(e)}")
            return "Company values focus on innovation and excellence."

    def _summarize_persona(self, persona: Persona) -> str:
        """Synthesizes persona into a concise summary for the AI."""
        skills = ", ".join([str(s.name) for s in persona.skills])
        summary = f"Name: {persona.full_name}, Skills: {skills}. "
        if persona.experiences:
            exp = persona.experiences[0]
            summary += f"Recent Role: {exp.job_title} at {exp.company_name}."
        return summary

    def _score_quality(
        self, content: str, job: Job, preferences: CoverLetterPreferences
    ) -> dict[str, Any]:
        """Automated quality audit for the generated cover letter."""
        word_count = len(content.split())

        # Simple checks
        company_mentioned = job.company.lower() in content.lower()
        generic_p_count = content.lower().count("i am writing") + content.lower().count(
            "great fit"
        )

        target_words = {
            Length.SHORT: 150,
            Length.MEDIUM: 250,
            Length.COMPREHENSIVE: 400,
        }

        return {
            "word_count": word_count,
            "target_word_count": target_words.get(preferences.length),
            "company_mentioned": company_mentioned,
            "generic_phrases_count": generic_p_count,
            "quality_score": max(0, 100 - (generic_p_count * 10)),
        }

    async def generate(
        self, job: Job, persona: Persona, preferences: CoverLetterPreferences
    ) -> dict[str, Any]:
        """Main entry point for generating a personalized cover letter."""
        # A/B Testing Logic: Randomly select a prompt version
        prompt_version = random.choice(["v1", "v2"])
        prompt_template = (
            COVER_LETTER_PROMPT_V1 if prompt_version == "v1" else COVER_LETTER_PROMPT_V2
        )

        company_research = ""
        if preferences.include_company_research:
            company_research = await self._extract_company_research(job)

        prompt = prompt_template.format(
            persona_summary=self._summarize_persona(persona),
            company_name=job.company,
            job_title=job.title,
            job_description=job.description[:1000],  # Truncate to save tokens
            requirements=", ".join(job.raw_data.get("requirements", [])),
            company_research=company_research,
            tone=preferences.tone.value,
            length=preferences.length.value,
            emphasis=", ".join([e.value for e in preferences.emphasis]),
            matched_qualifications=(
                "High alignment with technical stack and leadership goals."
            ),
        )

        content = await self.client.generate_text(prompt)
        quality_metrics = self._score_quality(content, job, preferences)

        return {
            "content": content,
            "prompt_v": prompt_version,
            "quality_metrics": quality_metrics,
            "preferences": preferences.model_dump(),
        }

    async def regenerate_paragraph(
        self, full_content: str, paragraph_index: int, guidance: str, job: Job
    ) -> str:
        """Regenerates a specific part of the letter based on user guidance."""
        paragraphs = full_content.split("\n\n")
        if not (0 <= paragraph_index < len(paragraphs)):
            raise ValueError("Invalid paragraph index")

        prompt = REGENERATE_PARAGRAPH_PROMPT.format(
            paragraph=paragraphs[paragraph_index],
            guidance=guidance,
            job_title=job.title,
            company_name=job.company,
            full_content=full_content,
        )

        new_paragraph = await self.client.generate_text(prompt)
        paragraphs[paragraph_index] = new_paragraph
        return "\n\n".join(paragraphs)

    async def get_alternatives(self, sentence: str, count: int = 3) -> list[str]:
        """Provides multiple variations of a single sentence."""
        prompt = GET_ALTERNATIVES_PROMPT.format(sentence=sentence, count=count)
        result = cast(
            AlternativesList,
            await self.client.generate_structured(prompt, AlternativesList),
        )
        return result.alternatives

    async def adjust_tone(self, content: str, target_tone: Tone) -> str:
        """Shifts the tone of existing content."""
        # Tone shift also returns text
        prompt = ADJUST_TONE_PROMPT.format(
            content=content, target_tone=target_tone.value
        )
        return await self.client.generate_text(prompt)
