"""
Metric Confirmation Service
===========================
Ensures all quantified claims are user-verified.
"""

import re
from uuid import UUID, uuid4
from typing import List, Dict, Any, Optional
from src.modules.resume.domain.truth_grounded_schemas import EnhancementSuggestionSchema


class MetricConfirmationService:
    """
    Service for handling user confirmation of suggested metrics.
    Ensures all quantified claims are user-verified.
    """

    METRIC_PATTERNS = [
        r"\d+%",  # Percentages
        r"\$[\d,]+",  # Dollar amounts
        r"\d+x",  # Multipliers
        r"\d+\s*(?:users|customers|clients|employees|team members)",
    ]

    def __init__(self, redis_client=None):
        self.redis = redis_client
        # In a real app, pending suggestions would be stored in Redis with a TTL
        self._pending_store = {}

    async def request_metric_confirmation(
        self, user_id: UUID, suggestion: EnhancementSuggestionSchema
    ) -> Dict[str, Any]:
        """
        Create a confirmation request for the user to verify metrics.
        """

        metrics = self._extract_metrics_needing_confirmation(suggestion)
        confirmation_id = str(uuid4())

        # Store for later processing
        self._pending_store[confirmation_id] = suggestion

        return {
            "confirmation_id": confirmation_id,
            "original_text": suggestion.original_text,
            "suggested_text": suggestion.enhanced_text,
            "metrics_to_confirm": metrics,
            "questions": [
                {
                    "metric": metric,
                    "question": self._generate_confirmation_question(metric),
                    "input_type": "number" if self._is_numeric(metric) else "text",
                }
                for metric in metrics
            ],
            "can_proceed_without": False,
            "alternative_action": "Use original text without metrics",
        }

    async def process_confirmation(
        self, confirmation_id: str, user_responses: Dict[str, str]
    ) -> EnhancementSuggestionSchema:
        """
        Process user's confirmation and update the enhancement.
        """
        suggestion = self._pending_store.get(confirmation_id)
        if not suggestion:
            raise ValueError("Confirmation request not found or expired")

        updated_text = suggestion.enhanced_text
        for metric, confirmed_value in user_responses.items():
            if confirmed_value:
                # Replace the suggested metric with the user's confirmed value
                # Simple replacement for now, might need better regex matching
                updated_text = updated_text.replace(metric, confirmed_value)

        # Update suggestion
        suggestion.enhanced_text = updated_text
        suggestion.verification_status = "verified"
        suggestion.requires_confirmation = False
        suggestion.verification_notes = "Metrics confirmed by user"

        # Cleanup
        del self._pending_store[confirmation_id]

        return suggestion

    def _extract_metrics_needing_confirmation(
        self, suggestion: EnhancementSuggestionSchema
    ) -> List[str]:
        """Extract metrics suggested by AI that weren't in original."""
        original_metrics = self._extract_metrics(suggestion.original_text)
        enhanced_metrics = self._extract_metrics(suggestion.enhanced_text)
        return list(set(enhanced_metrics) - set(original_metrics))

    def _extract_metrics(self, text: str) -> List[str]:
        metrics = []
        for pattern in self.METRIC_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            metrics.extend(matches)
        return metrics

    def _is_numeric(self, metric: str) -> bool:
        return bool(re.search(r"\d+", metric))

    def _generate_confirmation_question(self, metric: str) -> str:
        """Generate a clear confirmation question for a metric."""
        if "%" in metric:
            return f"What was the actual percentage improvement/change? (You suggested: {metric})"
        elif "$" in metric:
            return f"What was the actual dollar amount? (You suggested: {metric})"
        elif "team" in metric.lower() or "people" in metric.lower():
            return (
                f"How many people were actually on the team? (You suggested: {metric})"
            )
        elif "users" in metric.lower() or "customers" in metric.lower():
            return f"What was the actual number of users/customers? (You suggested: {metric})"
        else:
            return f"Please confirm this metric is accurate: {metric}"
