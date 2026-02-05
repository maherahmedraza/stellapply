from dataclasses import dataclass
from typing import List, Dict, Optional, Set, Any
from enum import Enum
import re
from src.modules.persona.domain.models import Skill


class MatchType(str, Enum):
    EXACT = "exact"
    SYNONYM = "synonym"
    SEMANTIC = "semantic"
    PARTIAL = "partial"


@dataclass(frozen=True)
class SkillMatch:
    """Immutable skill match result"""

    required_skill: str
    matched_skill: str
    match_type: MatchType
    proficiency: Optional[int] = None
    confidence: float = 1.0


class SkillMatcher:
    """
    Handles skill matching with multiple strategies.
    Extracted for testability and single responsibility.
    """

    # Common skill synonyms
    SKILL_SYNONYMS: dict[str, set[str]] = {
        "javascript": {"js", "ecmascript", "es6", "es2015"},
        "typescript": {"ts"},
        "react": {"react.js", "reactjs"},
        "node": {"node.js", "nodejs"},
        "python": {"python3", "py"},
        "postgresql": {"postgres", "psql"},
        "kubernetes": {"k8s"},
        "amazon web services": {"aws"},
        "google cloud platform": {"gcp"},
        "microsoft azure": {"azure"},
        "machine learning": {"ml"},
        "artificial intelligence": {"ai"},
        "continuous integration": {"ci"},
        "continuous deployment": {"cd"},
        "ci/cd": {"cicd", "ci cd"},
    }

    # Skills that should NOT match each other
    EXCLUSIONS: dict[str, set[str]] = {
        "java": {"javascript", "js"},
        "c": {"c++", "c#", "objective-c"},
    }

    def __init__(self, embedding_service=None):
        self.embedding_service = embedding_service
        self._build_reverse_synonym_map()

    def _build_reverse_synonym_map(self):
        """Build reverse lookup for faster synonym matching"""
        self._reverse_synonyms: dict[str, str] = {}
        for canonical, synonyms in self.SKILL_SYNONYMS.items():
            for syn in synonyms:
                self._reverse_synonyms[syn] = canonical
            self._reverse_synonyms[canonical] = canonical

    def match(
        self, required_skill: str, user_skills: dict[str, Skill]
    ) -> Optional[SkillMatch]:
        """
        Match a required skill against user's skills using multiple strategies.
        Returns the best match or None if no match found.
        """
        req_lower = required_skill.lower().strip()
        req_canonical = self._canonicalize(req_lower)

        # Strategy 1: Exact match
        if req_lower in user_skills:
            skill = user_skills[req_lower]
            return SkillMatch(
                required_skill=required_skill,
                matched_skill=skill.name,
                match_type=MatchType.EXACT,
                proficiency=self._get_proficiency_value(skill),
                confidence=1.0,
            )

        # Strategy 2: Canonical/Synonym match
        for user_skill_lower, skill in user_skills.items():
            user_canonical = self._canonicalize(user_skill_lower)

            if req_canonical == user_canonical:
                return SkillMatch(
                    required_skill=required_skill,
                    matched_skill=skill.name,
                    match_type=MatchType.SYNONYM,
                    proficiency=self._get_proficiency_value(skill),
                    confidence=0.95,
                )

        # Strategy 3: Partial match (with exclusion check)
        for user_skill_lower, skill in user_skills.items():
            if self._is_excluded_match(req_lower, user_skill_lower):
                continue

            if self._is_valid_partial_match(req_lower, user_skill_lower):
                return SkillMatch(
                    required_skill=required_skill,
                    matched_skill=skill.name,
                    match_type=MatchType.PARTIAL,
                    proficiency=self._get_proficiency_value(skill),
                    confidence=0.7,
                )

        # Strategy 4: Semantic match (if embedding service available)
        if self.embedding_service:
            # Semantic match would be async usually, but review shows it as potentially async or placeholder
            pass

        return None

    def _canonicalize(self, skill: str) -> str:
        """Convert skill to canonical form using synonyms"""
        return self._reverse_synonyms.get(skill, skill)

    def _is_excluded_match(self, skill1: str, skill2: str) -> bool:
        """Check if two skills should NOT match"""
        for base, exclusions in self.EXCLUSIONS.items():
            if skill1 == base and skill2 in exclusions:
                return True
            if skill2 == base and skill1 in exclusions:
                return True
        return False

    def _is_valid_partial_match(self, req: str, user: str) -> bool:
        """
        Check for valid partial match.
        Requires one to be a meaningful substring of the other.
        """
        # Minimum 4 characters to avoid false positives
        if len(req) < 4 or len(user) < 4:
            return False

        # One must contain the other
        if req in user or user in req:
            # Additional validation: check word boundaries
            longer = user if len(user) > len(req) else req
            shorter = req if len(req) < len(user) else user

            # The shorter should be a "word" in the longer
            # e.g., "react" in "react.js" ✓, but "act" in "react" ✗
            pattern = rf"\b{re.escape(shorter)}\b"
            if re.search(pattern, longer, re.IGNORECASE):
                return True

            # Or separated by common delimiters
            if any(
                f"{shorter}{sep}" in longer or f"{sep}{shorter}" in longer
                for sep in [".", "-", " ", "_"]
            ):
                return True

        return False

    def _get_proficiency_value(self, skill: Skill) -> int:
        """Safely extract proficiency value"""
        if hasattr(skill.proficiency_level, "value"):
            return skill.proficiency_level.value
        return (
            skill.proficiency_level if isinstance(skill.proficiency_level, int) else 3
        )
