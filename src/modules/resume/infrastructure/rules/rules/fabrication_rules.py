import re
from typing import List, Dict, Any, Optional
from src.modules.resume.infrastructure.rules.base import (
    EnhancementRule,
    RuleViolation,
    RuleViolationType,
    RuleSeverity,
)


class NoFabricatedSkillsRule(EnhancementRule):
    """Prevents adding skills not in the user's verified profile"""

    rule_id = "no_fabricated_skills"
    name = "No Fabricated Skills"
    description = "Cannot add skills not in the user's profile"
    violation_type = RuleViolationType.FABRICATION
    severity = RuleSeverity.BLOCK

    def check(
        self, original: str, enhanced: str, context: dict[str, Any]
    ) -> Optional[RuleViolation]:
        verified_skills = context.get("verified_skills", set())
        verified_tools = context.get("verified_tools", set())
        all_verified = {s.lower() for s in (verified_skills | verified_tools)}

        # Only check skills that appear in enhanced but not in original
        enhanced_lower = enhanced.lower()
        original_lower = original.lower()

        # Use the skill taxonomy from context (if available) or a default set
        skills_to_check = context.get("skill_taxonomy", self._get_common_tech_skills())

        fabricated = []
        for skill in skills_to_check:
            skill_lower = skill.lower()
            # Skill is in enhanced, not in original, and not verified
            if (
                skill_lower in enhanced_lower
                and skill_lower not in original_lower
                and skill_lower not in all_verified
            ):
                # Verify it's a word boundary match (not substring)
                if re.search(rf"\b{re.escape(skill_lower)}\b", enhanced_lower):
                    fabricated.append(skill)

        if fabricated:
            return RuleViolation(
                rule_id=self.rule_id,
                rule_name=self.name,
                description=self.description,
                violation_type=self.violation_type,
                severity=self.severity,
                details=f"Unverified skills detected: {', '.join(fabricated)}",
                suggested_fix="Remove skills not in your profile or add them to your persona first",
            )

        return None

    @staticmethod
    def _get_common_tech_skills() -> list[str]:
        """
        Returns common tech skills to check for.
        In production, this should come from a maintained database/config.
        """
        return [
            # Languages
            "python",
            "java",
            "javascript",
            "typescript",
            "golang",
            "rust",
            "c++",
            "c#",
            "ruby",
            "php",
            "swift",
            "kotlin",
            "scala",
            # Frontend
            "react",
            "angular",
            "vue",
            "svelte",
            "next.js",
            "nuxt",
            # Backend
            "node",
            "django",
            "flask",
            "fastapi",
            "spring",
            "rails",
            "express",
            # Cloud
            "aws",
            "azure",
            "gcp",
            "heroku",
            "vercel",
            "cloudflare",
            # DevOps
            "kubernetes",
            "docker",
            "terraform",
            "ansible",
            "jenkins",
            "github actions",
            # Databases
            "postgresql",
            "mysql",
            "mongodb",
            "redis",
            "elasticsearch",
            "cassandra",
            # ML/AI
            "machine learning",
            "deep learning",
            "tensorflow",
            "pytorch",
            "scikit-learn",
            # Other
            "graphql",
            "rest",
            "grpc",
            "kafka",
            "rabbitmq",
            "spark",
        ]


class NoExperienceInflationRule(EnhancementRule):
    """Prevents inflating years of experience"""

    rule_id = "no_experience_inflation"
    name = "No Experience Inflation"
    description = "Cannot inflate years of experience"
    violation_type = RuleViolationType.EXAGGERATION
    severity = RuleSeverity.BLOCK

    YEAR_PATTERNS = [
        r"(\d+)\+?\s*years?\s*(?:of\s*)?experience",
        r"over\s*(\d+)\s*years",
        r"(\d+)\+\s*years",
        r"(\d+)\s*yrs?\s*experience",
    ]

    def check(
        self, original: str, enhanced: str, context: dict[str, Any]
    ) -> Optional[RuleViolation]:
        years_experience = context.get("years_of_experience", {})
        if not years_experience:
            return None

        # Calculate actual total years
        total_years = sum(years_experience.values())

        # Find year claims in enhanced text
        for pattern in self.YEAR_PATTERNS:
            matches = re.findall(pattern, enhanced, re.IGNORECASE)
            for match in matches:
                claimed_years = int(match)

                # Allow 10% buffer for rounding
                max_allowed = total_years * 1.1

                if claimed_years > max_allowed:
                    # Check if this claim was in the original
                    if not re.search(rf"\b{claimed_years}\b", original):
                        return RuleViolation(
                            rule_id=self.rule_id,
                            rule_name=self.name,
                            description=self.description,
                            violation_type=self.violation_type,
                            severity=self.severity,
                            details=f"Claimed {claimed_years} years, but verified experience is ~{total_years:.1f} years",
                            suggested_fix=f"Use accurate experience: {int(total_years)} years",
                        )

        return None


class NoFabricatedCertificationsRule(EnhancementRule):
    """Prevents claiming certifications the user doesn't have"""

    rule_id = "no_fabricated_certifications"
    name = "No Fabricated Certifications"
    description = "Cannot add certifications user doesn't have"
    violation_type = RuleViolationType.FABRICATION
    severity = RuleSeverity.BLOCK

    CERT_PATTERNS = [
        r"certified\s+(\w+(?:\s+\w+){0,3})",
        r"(\w+(?:\s+\w+){0,2})\s+certified",
        r"(\w+(?:\s+\w+){0,2})\s+certification",
        r"(AWS|GCP|Azure|PMP|CISSP|CPA|CFA|CISA|CCNA|CCNP)\s*(?:certified)?",
    ]

    def check(
        self, original: str, enhanced: str, context: dict[str, Any]
    ) -> Optional[RuleViolation]:
        verified_certs = {c.lower() for c in context.get("certifications", [])}

        enhanced_lower = enhanced.lower()
        original_lower = original.lower()

        fabricated = []
        for pattern in self.CERT_PATTERNS:
            matches = re.findall(pattern, enhanced, re.IGNORECASE)
            for match in matches:
                cert_text = (
                    match.lower() if isinstance(match, str) else match[0].lower()
                )

                # Skip if it was in the original
                if cert_text in original_lower:
                    continue

                # Check if user has this certification
                if not any(
                    cert_text in cert or cert in cert_text for cert in verified_certs
                ):
                    fabricated.append(match if isinstance(match, str) else match[0])

        if fabricated:
            return RuleViolation(
                rule_id=self.rule_id,
                rule_name=self.name,
                description=self.description,
                violation_type=self.violation_type,
                severity=self.severity,
                details=f"Unverified certifications: {', '.join(fabricated)}",
                suggested_fix="Remove certifications not in your profile or add them to your persona",
            )

        return None
