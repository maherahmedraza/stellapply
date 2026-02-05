import logging
from typing import List, Dict, Any, Optional, Type
from src.modules.resume.infrastructure.rules.base import (
    EnhancementRule,
    ValidationResult,
    RuleSeverity,
    RuleViolationType,
)
from src.modules.resume.infrastructure.rules.rules.fabrication_rules import (
    NoFabricatedSkillsRule,
    NoExperienceInflationRule,
    NoFabricatedCertificationsRule,
)
from src.modules.resume.infrastructure.rules.rules.metric_rules import (
    MetricsNeedConfirmationRule,
)
from src.modules.resume.infrastructure.rules.rules.language_rules import (
    LeadershipClaimsRule,
    SuperlativeUsageRule,
)

logger = logging.getLogger(__name__)


class EnhancementRulesEngine:
    """
    Plugin-based rules engine for validating enhancements.
    Rules can be added, removed, or customized per user/tier.
    """

    # Default rules in priority order
    DEFAULT_RULES: list[Type[EnhancementRule]] = [
        # Blocking rules first
        NoFabricatedSkillsRule,
        NoExperienceInflationRule,
        NoFabricatedCertificationsRule,
        # Warning rules
        MetricsNeedConfirmationRule,
        LeadershipClaimsRule,
        # Info rules
        SuperlativeUsageRule,
    ]

    def __init__(
        self,
        rules: Optional[list[EnhancementRule]] = None,
        disabled_rules: Optional[list[str]] = None,
    ):
        """
        Initialize the rules engine.

        Args:
            rules: Custom list of rule instances. If None, uses defaults.
            disabled_rules: List of rule_ids to disable
        """
        if rules is not None:
            self.rules = rules
        else:
            self.rules = [rule_class() for rule_class in self.DEFAULT_RULES]

        if disabled_rules:
            self.rules = [r for r in self.rules if r.rule_id not in disabled_rules]

    def add_rule(self, rule: EnhancementRule):
        """Add a custom rule to the engine"""
        self.rules.append(rule)

    def remove_rule(self, rule_id: str):
        """Remove a rule by ID"""
        self.rules = [r for r in self.rules if r.rule_id != rule_id]

    def validate_enhancement(
        self, original: str, enhanced: str, context: dict[str, Any]
    ) -> ValidationResult:
        """
        Validate an enhancement against all registered rules.

        Args:
            original: Original text before enhancement
            enhanced: Enhanced text to validate
            context: Verification context from persona

        Returns:
            ValidationResult with all violations categorized
        """
        result = ValidationResult(
            is_valid=True, can_proceed=True, requires_confirmation=False
        )

        for rule in self.rules:
            try:
                violation = rule.check(original, enhanced, context)
                if violation:
                    result.add_violation(violation)
            except Exception as e:
                logger.error(f"Rule {rule.rule_id} failed: {e}")
                # Don't block on rule errors, but log them

        return result

    def get_rule_descriptions(self) -> list[dict[str, str]]:
        """Get descriptions of all active rules for documentation"""
        return [
            {
                "id": rule.rule_id,
                "name": rule.name,
                "description": rule.description,
                "severity": rule.severity.value,
                "type": rule.violation_type.value,
            }
            for rule in self.rules
        ]
