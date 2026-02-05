"""
Enhancement Rules Engine
========================
Defines what can and cannot be done during CV enhancement.
"""

from dataclasses import dataclass
from typing import List, Set, Callable, Dict, Any
from enum import Enum
import re


class RuleViolationType(Enum):
    FABRICATION = "fabrication"
    EXAGGERATION = "exaggeration"
    UNVERIFIABLE = "unverifiable"
    MISLEADING = "misleading"


@dataclass
class EnhancementRule:
    name: str
    description: str
    violation_type: RuleViolationType
    check_function: Callable[[str, str, Dict[str, Any]], bool]
    severity: str  # "block", "warn", "info"


class EnhancementRulesEngine:
    """
    Rules engine that validates all enhancements before they're shown to users.
    """

    def __init__(self):
        self.rules = self._build_rules()

    def _build_rules(self) -> List[EnhancementRule]:
        return [
            # === BLOCKING RULES (Cannot proceed) ===
            EnhancementRule(
                name="no_fabricated_skills",
                description="Cannot add skills not in the user's profile",
                violation_type=RuleViolationType.FABRICATION,
                check_function=self._check_fabricated_skills,
                severity="block",
            ),
            EnhancementRule(
                name="no_fabricated_companies",
                description="Cannot mention companies user didn't work at",
                violation_type=RuleViolationType.FABRICATION,
                check_function=self._check_fabricated_companies,
                severity="block",
            ),
            EnhancementRule(
                name="no_fabricated_certifications",
                description="Cannot add certifications user doesn't have",
                violation_type=RuleViolationType.FABRICATION,
                check_function=self._check_fabricated_certifications,
                severity="block",
            ),
            EnhancementRule(
                name="no_fabricated_education",
                description="Cannot add degrees or institutions user didn't attend",
                violation_type=RuleViolationType.FABRICATION,
                check_function=self._check_fabricated_education,
                severity="block",
            ),
            EnhancementRule(
                name="no_experience_inflation",
                description="Cannot inflate years of experience",
                violation_type=RuleViolationType.EXAGGERATION,
                check_function=self._check_experience_inflation,
                severity="block",
            ),
            # === WARNING RULES (Require confirmation) ===
            EnhancementRule(
                name="metrics_need_confirmation",
                description="Any new metrics must be confirmed by user",
                violation_type=RuleViolationType.UNVERIFIABLE,
                check_function=self._check_new_metrics,
                severity="warn",
            ),
            EnhancementRule(
                name="industry_alignment",
                description="Industries mentioned should align with your profile",
                violation_type=RuleViolationType.MISLEADING,
                check_function=self._check_industry_alignment,
                severity="warn",
            ),
            EnhancementRule(
                name="leadership_claims_verification",
                description="Leadership claims need evidence from experience",
                violation_type=RuleViolationType.EXAGGERATION,
                check_function=self._check_leadership_claims,
                severity="warn",
            ),
            EnhancementRule(
                name="impact_claims_verification",
                description="Impact claims (saved, increased, etc.) need backing",
                violation_type=RuleViolationType.EXAGGERATION,
                check_function=self._check_impact_claims,
                severity="warn",
            ),
            # === INFO RULES (Flag but allow) ===
            EnhancementRule(
                name="superlative_usage",
                description="Superlatives may be hard to defend in interviews",
                violation_type=RuleViolationType.MISLEADING,
                check_function=self._check_superlatives,
                severity="info",
            ),
        ]

    def validate_enhancement(
        self, original: str, enhanced: str, persona_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate an enhancement against all rules.
        """

        blocking = []
        warnings = []
        info = []

        for rule in self.rules:
            violated = rule.check_function(original, enhanced, persona_context)

            if violated:
                violation = {
                    "rule": rule.name,
                    "description": rule.description,
                    "type": rule.violation_type.value,
                }

                if rule.severity == "block":
                    blocking.append(violation)
                elif rule.severity == "warn":
                    warnings.append(violation)
                else:
                    info.append(violation)

        return {
            "is_valid": len(blocking) == 0,
            "blocking_violations": blocking,
            "warnings": warnings,
            "info": info,
            "can_proceed": len(blocking) == 0,
            "requires_confirmation": len(warnings) > 0,
        }

    # === Rule Check Functions ===

    def _check_fabricated_skills(
        self, original: str, enhanced: str, context: Dict[str, Any]
    ) -> bool:
        """Check if enhanced text contains skills not in persona."""
        verified_skills = context.get("verified_skills", set())
        verified_tools = context.get("verified_tools", set())
        all_verified = set(s.lower() for s in (verified_skills | verified_tools))

        enhanced_lower = enhanced.lower()
        original_lower = original.lower()

        # This list should ideally be dynamic or more comprehensive
        tech_skills = [
            "python",
            "java",
            "javascript",
            "typescript",
            "react",
            "angular",
            "vue",
            "node",
            "django",
            "flask",
            "spring",
            "kubernetes",
            "docker",
            "aws",
            "azure",
            "gcp",
            "terraform",
            "jenkins",
            "machine learning",
            "deep learning",
            "sql",
            "mongodb",
            "postgresql",
            "graphql",
            "rest",
        ]

        for skill in tech_skills:
            # If skill is in enhanced but not in original AND not verified
            if (
                skill in enhanced_lower
                and skill not in original_lower
                and skill not in all_verified
            ):
                return True

        return False

    def _check_fabricated_companies(
        self, original: str, enhanced: str, context: Dict[str, Any]
    ) -> bool:
        """Check if enhanced text mentions companies user didn't work at."""
        verified_companies = set(
            c.lower() for c in context.get("verified_companies", set())
        )

        company_patterns = [
            r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Inc|Corp|LLC|Ltd|Company)\b",
            r"\bat\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",
        ]

        for pattern in company_patterns:
            matches = re.findall(pattern, enhanced)
            for match in matches:
                match_lower = match.lower()
                if match_lower not in verified_companies:
                    if match.lower() not in original.lower():
                        return True

        return False

    def _check_fabricated_certifications(
        self, original: str, enhanced: str, context: Dict[str, Any]
    ) -> bool:
        """Check if enhanced text claims certifications user doesn't have."""
        verified_certs = set(c.lower() for c in context.get("certifications", []))

        cert_patterns = [
            r"certified\s+(\w+(?:\s+\w+)*)",
            r"(\w+)\s+certification",
            r"(AWS|GCP|Azure|PMP|CISSP|CPA|CFA)\s+certified",
        ]

        enhanced_lower = enhanced.lower()
        original_lower = original.lower()

        for pattern in cert_patterns:
            matches = re.findall(pattern, enhanced, re.IGNORECASE)
            for match in matches:
                match_lower = (
                    match.lower() if isinstance(match, str) else match[0].lower()
                )
                if match_lower not in original_lower and not any(
                    match_lower in cert for cert in verified_certs
                ):
                    return True

        return False

    def _check_fabricated_education(
        self, original: str, enhanced: str, context: Dict[str, Any]
    ) -> bool:
        """Check if enhanced text claims education user doesn't have."""
        verified_education = context.get("education", [])
        verified_degrees = set(
            edu.get("degree", "").lower() for edu in verified_education
        )
        verified_institutions = set(
            edu.get("institution", "").lower() for edu in verified_education
        )

        degree_patterns = [
            r"(bachelor|master|phd|doctorate|mba|bs|ba|ms|ma)\s+(?:of|in|degree)",
            r"(university|college|institute)\s+of\s+(\w+)",
        ]

        enhanced_lower = enhanced.lower()
        original_lower = original.lower()

        for pattern in degree_patterns:
            matches = re.findall(pattern, enhanced_lower)
            for match in matches:
                match_text = match if isinstance(match, str) else " ".join(match)
                if (
                    match_text not in original_lower
                    and match_text not in verified_degrees
                    and not any(match_text in inst for inst in verified_institutions)
                ):
                    return True

        return False

    def _check_experience_inflation(
        self, original: str, enhanced: str, context: Dict[str, Any]
    ) -> bool:
        """Check if years of experience are inflated."""
        year_patterns = [
            r"(\d+)\+?\s+years?\s+(?:of\s+)?experience",
            r"over\s+(\d+)\s+years",
            r"(\d+)\+\s+years",
        ]

        years_experience = context.get("years_of_experience", {})
        if not years_experience:
            return False

        total_years = sum(years_experience.values()) / len(years_experience)

        for pattern in year_patterns:
            matches = re.findall(pattern, enhanced, re.IGNORECASE)
            for match in matches:
                claimed_years = int(match)
                if claimed_years > total_years * 1.1:
                    if match not in original:
                        return True

        return False

    def _check_new_metrics(
        self, original: str, enhanced: str, context: Dict[str, Any]
    ) -> bool:
        """Check if new metrics were added that need confirmation."""
        metric_patterns = [
            r"\d+%",
            r"\$[\d,]+",
            r"\d+x",
            r"\d+\s*(?:users|customers|clients|employees|team members)",
        ]

        original_metrics = set()
        enhanced_metrics = set()

        for pattern in metric_patterns:
            original_metrics.update(re.findall(pattern, original, re.IGNORECASE))
            enhanced_metrics.update(re.findall(pattern, enhanced, re.IGNORECASE))

        new_metrics = enhanced_metrics - original_metrics
        return len(new_metrics) > 0

    def _check_leadership_claims(
        self, original: str, enhanced: str, context: Dict[str, Any]
    ) -> bool:
        """Check if leadership claims can be backed by experience."""
        leadership_verbs = [
            "led",
            "managed",
            "directed",
            "headed",
            "supervised",
            "oversaw",
            "coordinated",
            "spearheaded",
            "orchestrated",
        ]

        enhanced_lower = enhanced.lower()
        original_lower = original.lower()

        for verb in leadership_verbs:
            if verb in enhanced_lower and verb not in original_lower:
                responsibilities = context.get("verified_responsibilities", [])
                has_leadership_evidence = any(
                    verb in resp.get("description", "").lower()
                    or "lead" in resp.get("role", "").lower()
                    or "manager" in resp.get("role", "").lower()
                    for resp in responsibilities
                )
                if not has_leadership_evidence:
                    return True

        return False

    def _check_impact_claims(
        self, original: str, enhanced: str, context: Dict[str, Any]
    ) -> bool:
        """Check if impact claims have supporting evidence."""
        impact_verbs = [
            "saved",
            "increased",
            "decreased",
            "improved",
            "reduced",
            "generated",
            "delivered",
            "achieved",
            "exceeded",
            "boosted",
        ]

        enhanced_lower = enhanced.lower()
        original_lower = original.lower()

        for verb in impact_verbs:
            if verb in enhanced_lower and verb not in original_lower:
                achievements = context.get("verified_achievements", [])
                has_achievement_evidence = any(
                    verb in ach.get("text", "").lower() for ach in achievements
                )
                if not has_achievement_evidence:
                    return True

        return False

    def _check_superlatives(
        self, original: str, enhanced: str, context: Dict[str, Any]
    ) -> bool:
        """Flag superlatives that might be hard to defend."""
        superlatives = [
            "best",
            "top",
            "leading",
            "premier",
            "only",
            "first",
            "most",
            "highest",
            "greatest",
            "exceptional",
            "outstanding",
        ]

        enhanced_lower = enhanced.lower()
        original_lower = original.lower()

        for sup in superlatives:
            if sup in enhanced_lower and sup not in original_lower:
                return True

        return False

    def _check_industry_alignment(
        self, original: str, enhanced: str, context: Dict[str, Any]
    ) -> bool:
        """Check if industries mentioned align with persona."""
        verified_industries = set(
            i.lower() for i in context.get("verified_industries", set())
        )
        if not verified_industries:
            return False

        # Some common industries to check for
        industries = [
            "fintech",
            "healthcare",
            "edtech",
            "ecommerce",
            "retail",
            "manufacturing",
            "logistics",
            "gaming",
            "saas",
            "web3",
            "crypto",
            "adtech",
        ]

        enhanced_lower = enhanced.lower()
        original_lower = original.lower()

        for industry in industries:
            if industry in enhanced_lower and industry not in original_lower:
                if industry not in verified_industries:
                    return True

        return False
