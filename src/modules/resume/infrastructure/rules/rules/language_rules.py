import re
from typing import List, Dict, Any, Optional
from src.modules.resume.infrastructure.rules.base import (
    EnhancementRule,
    RuleViolation,
    RuleViolationType,
    RuleSeverity,
)


class LeadershipClaimsRule(EnhancementRule):
    """Verifies leadership claims have supporting evidence"""

    rule_id = "leadership_claims_verification"
    name = "Leadership Claims Verification"
    description = "Leadership claims need evidence from experience"
    violation_type = RuleViolationType.EXAGGERATION
    severity = RuleSeverity.WARN

    LEADERSHIP_VERBS = [
        "led",
        "managed",
        "directed",
        "headed",
        "supervised",
        "oversaw",
        "coordinated",
        "spearheaded",
        "orchestrated",
        "mentored",
        "coached",
        "guided",
        "championed",
    ]

    def check(
        self, original: str, enhanced: str, context: dict[str, Any]
    ) -> Optional[RuleViolation]:
        enhanced_lower = enhanced.lower()
        original_lower = original.lower()

        new_leadership_claims = []
        for verb in self.LEADERSHIP_VERBS:
            if verb in enhanced_lower and verb not in original_lower:
                new_leadership_claims.append(verb)

        if not new_leadership_claims:
            return None

        # Check if user has leadership evidence
        responsibilities = context.get("verified_responsibilities", [])
        job_titles = context.get("verified_job_titles", set())

        has_leadership_evidence = any(
            "lead" in title or "manager" in title or "director" in title
            for title in job_titles
        ) or any(
            any(
                verb in resp.get("description", "").lower()
                for verb in self.LEADERSHIP_VERBS
            )
            for resp in responsibilities
        )

        if not has_leadership_evidence:
            return RuleViolation(
                rule_id=self.rule_id,
                rule_name=self.name,
                description=self.description,
                violation_type=self.violation_type,
                severity=self.severity,
                details=f"Leadership verbs added without clear evidence: {', '.join(new_leadership_claims)}",
                suggested_fix="Ensure you can back up leadership claims with specific examples",
            )

        return None


class SuperlativeUsageRule(EnhancementRule):
    """Flags superlatives that may be hard to defend"""

    rule_id = "superlative_usage"
    name = "Superlative Usage Warning"
    description = "Superlatives may be hard to defend in interviews"
    violation_type = RuleViolationType.MISLEADING
    severity = RuleSeverity.INFO

    SUPERLATIVES = [
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
        "unparalleled",
        "unprecedented",
        "world-class",
        "industry-leading",
    ]

    def check(
        self, original: str, enhanced: str, context: dict[str, Any]
    ) -> Optional[RuleViolation]:
        enhanced_lower = enhanced.lower()
        original_lower = original.lower()

        new_superlatives = []
        for sup in self.SUPERLATIVES:
            if sup in enhanced_lower and sup not in original_lower:
                new_superlatives.append(sup)

        if new_superlatives:
            return RuleViolation(
                rule_id=self.rule_id,
                rule_name=self.name,
                description=self.description,
                violation_type=self.violation_type,
                severity=self.severity,
                details=f"Superlatives that may be questioned: {', '.join(new_superlatives)}",
                suggested_fix="Be prepared to back up these claims with specific examples",
            )

        return None
