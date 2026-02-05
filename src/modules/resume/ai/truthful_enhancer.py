import re
import logging
from uuid import UUID
from typing import Optional, List, Dict, Set, Any
from pydantic import BaseModel, Field

from src.core.ai.gemini_client import GeminiClient
from src.modules.persona.domain.services import PersonaService
from src.modules.resume.domain.enhancement_audit import EnhancementType

logger = logging.getLogger(__name__)


class TruthfulEnhancement(BaseModel):
    """A single enhancement with truthfulness guarantees"""

    original_text: str
    enhanced_text: str
    enhancement_type: EnhancementType

    # Truthfulness metadata
    requires_user_verification: bool = False
    verification_prompt: Optional[str] = None  # Question to ask user
    source_skills_used: List[str] = []  # Which user skills were referenced
    metrics_are_placeholder: bool = False  # If True, user MUST fill in
    confidence_score: float = Field(ge=0.0, le=1.0)

    # Audit trail
    grounding_explanation: str  # Why this enhancement is truthful


class TruthfulEnhancementResponse(BaseModel):
    """Internal model for structured Gemini output"""

    enhanced_text: str
    enhancement_type: str
    skills_referenced: List[str]
    has_placeholder_metrics: bool
    verification_needed: bool
    verification_question: Optional[str]
    truthfulness_explanation: str


class TruthfulResumeEnhancer:
    """
    Resume enhancer that guarantees truthfulness through:
    1. Grounding all enhancements in user's existing data
    2. Never fabricating information
    3. Clearly marking anything that needs verification
    4. Providing audit trails for every change
    """

    def __init__(self, gemini_client: GeminiClient, persona_service: PersonaService):
        self.gemini = gemini_client
        self.persona_service = persona_service

        # Skills and experiences the user HAS - our source of truth
        self.verified_skills: Set[str] = set()
        self.verified_experiences: List[Dict[str, Any]] = []
        self.verified_achievements: List[str] = []

    async def load_verified_data(self, user_id: UUID) -> None:
        """Load user's verified data as the ONLY source of truth"""
        persona = await self.persona_service.get_persona_by_user_id(user_id)
        if not persona:
            logger.warning(f"No persona found for user {user_id}")
            return

        # Build verified skill set
        self.verified_skills = {skill.name.lower() for skill in persona.skills}

        # Build verified experience list
        self.verified_experiences = [
            {
                "company": exp.company_name,
                "title": exp.job_title,
                "achievements": exp.achievements,
                "description": exp.description,
            }
            for exp in persona.experiences
        ]

        # Flatten all achievements
        self.verified_achievements = [
            ach for exp in persona.experiences for ach in exp.achievements
        ]

    async def enhance_bullet_point(
        self, bullet: str, context: Dict[str, Any], user_id: UUID
    ) -> TruthfulEnhancement:
        """
        Enhance a single bullet point with strict truthfulness.
        """

        await self.load_verified_data(user_id)

        # Create the truthfulness-enforcing prompt
        prompt = self._create_truthful_prompt(bullet, context)

        # Generate with structured output
        response = await self.gemini.generate_structured(
            prompt=prompt, schema=TruthfulEnhancementResponse
        )

        # Convert response dict-like object to dict if it's a Pydantic model
        response_dict = response.model_dump()

        # Validate the enhancement doesn't violate truth
        validated = self._validate_truthfulness(bullet, response_dict)

        return validated

    def _create_truthful_prompt(self, bullet: str, context: Dict[str, Any]) -> str:
        """Create a prompt that enforces truthfulness"""

        return f"""You are a resume editor who NEVER fabricates information.
Your job is to REPHRASE and IMPROVE existing content, not to invent new content.

CRITICAL RULES:
1. NEVER add skills that aren't in the VERIFIED SKILLS list below
2. NEVER invent metrics or numbers - if the original has no numbers, the enhanced version should have PLACEHOLDER like [X%] or [N+] that the user MUST fill in
3. NEVER change job titles, company names, or dates
4. NEVER claim achievements that aren't in the original
5. ONLY use stronger action verbs and clearer phrasing

VERIFIED SKILLS (the ONLY skills you can reference):
{", ".join(self.verified_skills)}

ORIGINAL BULLET POINT:
"{bullet}"

JOB CONTEXT:
Role: {context.get("target_role", "Not specified")}
Key Requirements: {context.get("requirements", [])}

YOUR TASK:
1. Improve the wording using strong action verbs
2. If you want to add metrics, use PLACEHOLDERS like [X%], [N users], [$X revenue]
3. Align with job requirements ONLY using skills from the VERIFIED list
4. Explain WHY your enhancement is truthful

RESPOND IN JSON:
{{
    "enhanced_text": "the improved bullet point",
    "enhancement_type": "rephrase|quantify|structure|keyword",
    "skills_referenced": ["only skills from VERIFIED list"],
    "has_placeholder_metrics": true/false,
    "verification_needed": true/false,
    "verification_question": "question to ask user if verification needed",
    "truthfulness_explanation": "why this is a truthful enhancement"
}}
"""

    def _validate_truthfulness(
        self, original: str, response: Dict[str, Any]
    ) -> TruthfulEnhancement:
        """Validate that the enhancement doesn't violate truthfulness"""

        enhanced_text = response["enhanced_text"]

        # Check 1: No new skills introduced
        # We check both what the LLM claims to have used, and scan the text for verified skills
        # Note: Detecting *unverified* skills in text without a global DB is hard,
        # so we rely on the LLM's structured output + the prompt constraints.

        reported_skills = set(response.get("skills_referenced", []))
        # Normalize reported skills
        reported_skills_lower = {s.lower() for s in reported_skills}

        unauthorized_skills = reported_skills_lower - self.verified_skills

        if unauthorized_skills:
            # Remove unauthorized skills from the enhancement
            for skill in unauthorized_skills:
                # Case-insensitive replacement
                pattern = re.compile(re.escape(skill), re.IGNORECASE)
                enhanced_text = pattern.sub("", enhanced_text)
            response["truthfulness_explanation"] += (
                f" [REMOVED unauthorized skills: {unauthorized_skills}]"
            )

        # Check 2: Metrics are properly marked as placeholders
        if self._has_unverified_metrics(enhanced_text, original):
            response["has_placeholder_metrics"] = True
            response["verification_needed"] = True
            response["verification_question"] = (
                "Please provide the actual numbers for the metrics in brackets"
            )

        # Check 3: Core meaning preserved (Simplified check for demo/code parity)
        if not self._meanings_aligned(original, enhanced_text):
            # Fall back to safer enhancement
            enhanced_text = self._safe_enhance(original)
            response["truthfulness_explanation"] = (
                "Fell back to safe enhancement to preserve meaning"
            )

        return TruthfulEnhancement(
            original_text=original,
            enhanced_text=enhanced_text,
            enhancement_type=EnhancementType(response["enhancement_type"]),
            requires_user_verification=response.get("verification_needed", False),
            verification_prompt=response.get("verification_question"),
            source_skills_used=response.get("skills_referenced", []),
            metrics_are_placeholder=response.get("has_placeholder_metrics", False),
            confidence_score=0.9 if not response.get("verification_needed") else 0.6,
            grounding_explanation=response["truthfulness_explanation"],
        )

    def _extract_skills(self, text: str) -> Set[str]:
        """Extract skills mentioned in text"""
        text_lower = text.lower()
        return {skill for skill in self.verified_skills if skill in text_lower}

    def _has_unverified_metrics(self, enhanced: str, original: str) -> bool:
        """Check if enhanced text has metrics that weren't in original"""

        # Find all numbers/percentages in both
        original_metrics = set(re.findall(r"\d+%|\$\d+|\d+\+?", original))
        enhanced_metrics = set(re.findall(r"\d+%|\$\d+|\d+\+?", enhanced))

        # New metrics that weren't in original are suspicious
        new_metrics = enhanced_metrics - original_metrics

        # Placeholders are okay
        placeholders = set(re.findall(r"\[.*?\]", enhanced))

        return len(new_metrics) > 0 and len(placeholders) == 0

    def _meanings_aligned(self, original: str, enhanced: str) -> bool:
        """
        Check if core words are preserved.
        Very basic implementation for internal safety.
        """
        original_words = set(original.lower().split())
        enhanced_words = set(enhanced.lower().split())

        # If less than 20% overlap, it might be a fabrication
        if not original_words:
            return True
        overlap = len(original_words & enhanced_words) / len(original_words)
        return overlap > 0.2

    def _safe_enhance(self, original: str) -> str:
        """Ultra-safe enhancement - only verb replacement"""
        weak_to_strong = {
            "helped": "contributed to",
            "worked on": "developed",
            "was responsible for": "managed",
            "did": "executed",
            "made": "created",
        }

        result = original
        for weak, strong in weak_to_strong.items():
            # Use regex for word-boundary replacement
            result = re.sub(rf"\b{weak}\b", strong, result, flags=re.IGNORECASE)

        return result
