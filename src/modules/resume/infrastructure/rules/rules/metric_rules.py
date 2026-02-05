import re
from typing import Dict, Any, Optional
from src.modules.resume.infrastructure.rules.base import (
    EnhancementRule,
    RuleViolation,
    RuleViolationType,
    RuleSeverity,
)


class MetricsNeedConfirmationRule(EnhancementRule):
    """Flags new metrics that need user confirmation"""

    rule_id = "metrics_need_confirmation"
    name = "Metrics Need Confirmation"
    description = "Any new metrics must be confirmed by user"
    violation_type = RuleViolationType.UNVERIFIABLE
    severity = RuleSeverity.WARN

    METRIC_PATTERNS = [
        r"\d+%",  # Percentages
        r"\$[\d,]+(?:\.\d{2})?[KMB]?",  # Dollar amounts
        r"\d+x",  # Multipliers
        r"\d+(?:,\d{3})*\s*(?:users|customers|clients|employees|team\s*members|people)",
    ]

    def check(
        self, original: str, enhanced: str, context: dict[str, Any]
    ) -> Optional[RuleViolation]:
        original_metrics = set()
        enhanced_metrics = set()

        for pattern in self.METRIC_PATTERNS:
            original_metrics.update(re.findall(pattern, original, re.IGNORECASE))
            enhanced_metrics.update(re.findall(pattern, enhanced, re.IGNORECASE))

        new_metrics = enhanced_metrics - original_metrics

        # Exclude placeholders (e.g., [X%], [N users])
        new_metrics = {m for m in new_metrics if not re.match(r"\[.*\]", m)}

        if new_metrics:
            return RuleViolation(
                rule_id=self.rule_id,
                rule_name=self.name,
                description=self.description,
                violation_type=self.violation_type,
                severity=self.severity,
                details=f"New metrics need verification: {', '.join(new_metrics)}",
                suggested_fix="Confirm these numbers are accurate before using",
            )

        return None
