from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class RuleViolationType(Enum):
    FABRICATION = "fabrication"
    EXAGGERATION = "exaggeration"
    UNVERIFIABLE = "unverifiable"
    MISLEADING = "misleading"


class RuleSeverity(Enum):
    BLOCK = "block"  # Cannot proceed
    WARN = "warn"  # Requires confirmation
    INFO = "info"  # Flag but allow


@dataclass
class RuleViolation:
    """Represents a single rule violation"""

    rule_id: str
    rule_name: str
    description: str
    violation_type: RuleViolationType
    severity: RuleSeverity
    details: Optional[str] = None
    suggested_fix: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validating an enhancement against all rules"""

    is_valid: bool
    can_proceed: bool
    requires_confirmation: bool
    blocking_violations: list[RuleViolation] = field(default_factory=list)
    warnings: list[RuleViolation] = field(default_factory=list)
    info: list[RuleViolation] = field(default_factory=list)

    def add_violation(self, violation: RuleViolation):
        """Add a violation to the appropriate list"""
        if violation.severity == RuleSeverity.BLOCK:
            self.blocking_violations.append(violation)
            self.is_valid = False
            self.can_proceed = False
        elif violation.severity == RuleSeverity.WARN:
            self.warnings.append(violation)
            self.requires_confirmation = True
        else:
            self.info.append(violation)


class EnhancementRule(ABC):
    """
    Base class for all enhancement rules.
    Each rule is a separate class for testability and extensibility.
    """

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique identifier for the rule"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """What this rule checks"""
        pass

    @property
    @abstractmethod
    def violation_type(self) -> RuleViolationType:
        """Type of violation if triggered"""
        pass

    @property
    @abstractmethod
    def severity(self) -> RuleSeverity:
        """How severe is a violation"""
        pass

    @abstractmethod
    def check(
        self, original: str, enhanced: str, context: dict[str, Any]
    ) -> Optional[RuleViolation]:
        """
        Check if the rule is violated.

        Args:
            original: Original text before enhancement
            enhanced: Enhanced text to validate
            context: Verification context from persona

        Returns:
            RuleViolation if violated, None otherwise
        """
        pass
