import json
import logging
from typing import Any, TypeVar, cast

from pydantic import BaseModel, Field

from src.core.ai.gemini_client import GeminiClient
from src.core.infrastructure.redis import redis_provider
from src.modules.persona.domain.models import Persona
from src.modules.resume.ai.prompts import (
    ATS_OPTIMIZATION_PROMPT,
    BULLET_ENHANCEMENT_PROMPT,
    IMPROVEMENT_SUGGESTION_PROMPT,
    METRIC_INJECTION_PROMPT,
    PROFESSIONAL_SUMMARY_PROMPT,
)
from src.modules.resume.domain.models import Resume, ResumeSection

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class EnhancedBullet(BaseModel):
    enhanced: str
    action_verb: str
    metrics_added: bool
    keywords_included: list[str] = Field(default_factory=list)
    confidence_score: float


class EnhancedSection(BaseModel):
    section_type: str
    original_content: dict[str, Any]
    enhanced_bullets: list[EnhancedBullet] = Field(default_factory=list)


class Suggestion(BaseModel):
    section: str
    issue: str
    suggestion: str
    priority: str  # LOW/MEDIUM/HIGH


class SuggestionList(BaseModel):
    suggestions: list[Suggestion]


class ResumeEnhancer:
    """Service to enhance resume content using Gemini AI."""

    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client
        self.cache_ttl = 86400  # 24 hours

    async def _get_cached_or_generate(
        self,
        cache_key: str,
        prompt: str,
        schema: type[T] | None = None,
        is_structured: bool = False,
    ) -> Any:
        """Helper to handle caching and AI generation."""
        try:
            cached = await redis_provider.get(cache_key)
            if cached:
                logger.info(f"Cache hit for key: {cache_key}")
                if is_structured and schema:
                    return schema.model_validate_json(cached)
                return cached
        except Exception as e:
            logger.error(f"Redis error: {str(e)}")

        try:
            if is_structured and schema:
                result = await self.client.generate_structured(prompt, schema)
                await redis_provider.set(
                    cache_key, result.model_dump_json(), expire=self.cache_ttl
                )
                return result
            result_text = await self.client.generate_text(prompt)
            await redis_provider.set(cache_key, result_text, expire=self.cache_ttl)
            return result_text
        except Exception as e:
            logger.error(f"AI Generation error: {str(e)}")
            raise

    async def enhance_bullet_point(
        self, bullet: str, context: str = ""
    ) -> EnhancedBullet:
        """Enhances a single bullet point using the STAR method."""
        cache_key = f"enhance:bullet:{hash(bullet + context)}"
        prompt = BULLET_ENHANCEMENT_PROMPT.format(original=bullet, context=context)

        try:
            return cast(
                EnhancedBullet,
                await self._get_cached_or_generate(
                    cache_key, prompt, schema=EnhancedBullet, is_structured=True
                ),
            )
        except Exception:
            # Fallback to a basic structure if AI fails
            return EnhancedBullet(
                enhanced=bullet,
                action_verb="",
                metrics_added=False,
                confidence_score=0.0,
            )

    async def enhance_full_section(self, section: ResumeSection) -> EnhancedSection:
        """Enhances all bullets in a section (e.g., Experience)."""
        # Note: This implementation assumes bullets are in section.content["items"]
        items = section.content.get("items", [])
        enhanced_bullets = []

        for item in items:
            description = item.get("description", "")
            if description:
                enhanced = await self.enhance_bullet_point(description)
                enhanced_bullets.append(enhanced)

        return EnhancedSection(
            section_type=str(section.section_type),
            original_content=section.content,
            enhanced_bullets=enhanced_bullets,
        )

    async def generate_professional_summary(self, persona: Persona) -> str:
        """Creates a compelling professional summary from persona data."""
        skills = ", ".join([s.name for s in persona.skills])
        achievements = []
        recent_role = "Candidate"

        if persona.experiences:
            recent_role = persona.experiences[0].job_title
            for exp in persona.experiences[:2]:
                achievements.extend(exp.achievements)

        prompt = PROFESSIONAL_SUMMARY_PROMPT.format(
            name=persona.full_name,
            years=5,  # TODO: Calculate from experience
            skills=skills,
            recent_role=recent_role,
            target_role=persona.career_preference.target_titles[0]
            if persona.career_preference and persona.career_preference.target_titles
            else "Professional",
            achievements="; ".join(achievements[:3]),
        )

        cache_key = f"summary:{persona.user_id}"
        return cast(str, await self._get_cached_or_generate(cache_key, prompt))

    async def inject_metrics(self, achievement: str) -> str:
        """Suggests quantifiable metrics for an achievement."""
        cache_key = f"metrics:{hash(achievement)}"
        prompt = METRIC_INJECTION_PROMPT.format(achievement=achievement)
        return cast(str, await self._get_cached_or_generate(cache_key, prompt))

    async def optimize_for_ats(self, content: str, target_keywords: list[str]) -> str:
        """Injects keywords naturally for ATS optimization."""
        keywords_str = ", ".join(target_keywords)
        cache_key = f"ats:opt:{hash(content + keywords_str)}"
        prompt = ATS_OPTIMIZATION_PROMPT.format(content=content, keywords=keywords_str)
        return cast(str, await self._get_cached_or_generate(cache_key, prompt))

    async def suggest_improvements(self, resume: Resume) -> list[Suggestion]:
        """Audits resume and provides improvement suggestions."""
        # Convert resume model to a readable text representation for the AI
        content_text = f"Resume: {resume.name}\n"
        for section in resume.sections:
            content_text += (
                f"\nSection: {section.section_type}\n{json.dumps(section.content)}\n"
            )

        cache_key = f"audit:{resume.id}:{resume.version}"
        prompt = IMPROVEMENT_SUGGESTION_PROMPT.format(content=content_text)

        try:
            result = cast(
                SuggestionList,
                await self._get_cached_or_generate(
                    cache_key, prompt, schema=SuggestionList, is_structured=True
                ),
            )
            return result.suggestions
        except Exception:
            return []
