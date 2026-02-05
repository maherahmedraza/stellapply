import re
import json
import structlog
from typing import Any, Dict, List, Optional
from difflib import SequenceMatcher

from pydantic import BaseModel

from src.agent.brain import AgentBrain
from src.agent.form.detector import FormField
from src.modules.profile.schemas import UserProfileResponse, FullProfile

logger = structlog.get_logger(__name__)


class FieldMapping(BaseModel):
    selector: str
    profile_field: Optional[str] = None
    value: Any = None  # The actual value to fill (string, bool, or list of file paths)
    confidence: float
    requires_ai: bool = False


class FormMapper:
    """
    Maps form fields to user profile data using Expanded Heuristics + Intelligent AI Fallback.
    """

    # Expanded Heuristic Patterns (English + German + French + Spanish)
    PATTERNS = {
        # Personal Info
        "personal_info.first_name": [
            r"first.?name",
            r"vorname",
            r"given.?name",
            r"prénom",
            r"nombre",
        ],
        "personal_info.last_name": [
            r"last.?name",
            r"surname",
            r"nachname",
            r"family.?name",
            r"nom",
            r"apellido",
        ],
        "personal_info.email": [r"e.?mail", r"courriel", r"correo"],
        "personal_info.phone": [
            r"phone",
            r"mobile",
            r"telefon",
            r"handy",
            r"téléphone",
            r"cell",
        ],
        "personal_info.city": [r"\bcity\b", r"stadt", r"\bort\b", r"ville", r"ciudad"],
        "personal_info.zip_code": [
            r"zip",
            r"postal.?code",
            r"\bplz\b",
            r"postleitzahl",
        ],
        "personal_info.street_address": [
            r"street",
            r"address",
            r"straße",
            r"adresse",
            r"anschrift",
        ],
        "personal_info.state": [r"\bstate\b", r"province", r"bundesland", r"region"],
        "personal_info.country": [r"\bcountry\b", r"\bland\b", r"pays", r"país"],
        "personal_info.linkedin_url": [r"linkedin"],
        "personal_info.portfolio_url": [
            r"portfolio",
            r"website",
            r"webseite",
            r"homepage",
        ],
        "personal_info.github_url": [r"github"],
        "personal_info.nationality": [r"national", r"staatsang", r"citizenship"],
        "personal_info.date_of_birth": [
            r"birth.?date",
            r"date.?of.?birth",
            r"dob",
            r"geburtsdatum",
            r"geboren",
        ],
        "personal_info.gender": [r"\bgender\b", r"geschlecht", r"\bsex\b"],
        "personal_info.salutation": [
            r"salutation",
            r"anrede",
            r"title.*mr.*ms",
            r"herr.*frau",
        ],
        # Work authorization
        "personal_info.work_authorization": [
            r"work.?auth",
            r"visa",
            r"permit",
            r"arbeitserlaubnis",
            r"eligible.?to.?work",
        ],
        "personal_info.willing_to_relocate": [r"relocat", r"umzug", r"move"],
        "personal_info.drivers_license": [
            r"driver",
            r"führerschein",
            r"driving.?license",
        ],
        # Application-specific
        "application_answers.salary_expectation": [
            r"salary",
            r"compensation",
            r"gehalt",
            r"gehaltsvorstellung",
            r"pay.?expect",
            r"remuneration",
        ],
        "application_answers.earliest_start_date": [
            r"start.?date",
            r"availab",
            r"earliest",
            r"eintrittsdatum",
            r"verfügbar",
            r"begin",
        ],
        "application_answers.years_of_experience": [
            r"years?.?of?.?exp",
            r"berufserfahrung",
            r"experience.?years",
        ],
        "application_answers.notice_period": [r"notice.?period", r"kündigungsfrist"],
        "application_answers.require_sponsorship": [r"sponsor", r"visa.?sponsor"],
        "application_answers.willing_to_travel": [
            r"travel",
            r"reisebereit",
            r"business.?trip",
        ],
        "application_answers.why_interested": [
            r"why.*interest",
            r"motivation",
            r"warum.*bewerb",
            r"cover.?letter.*text",  # Text area for cover letter
        ],
        "application_answers.strengths": [r"strength", r"stärke", r"about.?you"],
        # Resume/CV upload
        "_resume_upload": [r"resume", r"cv\b", r"lebenslauf", r"curriculum"],
        "_cover_letter_upload": [
            r"cover.?letter",
            r"anschreiben",
            r"motivationsschreiben",
            r"letter.?of.?motivation",
        ],
    }

    def __init__(self, brain: AgentBrain):
        self.brain = brain

    def _get_profile_value(self, profile: UserProfileResponse, field_path: str) -> Any:
        """Helper to get value from dot-notation path."""
        try:
            if field_path == "_resume_upload":
                return (
                    profile.resume_file_path
                    if hasattr(profile, "resume_file_path")
                    else None
                )
                # Note: UserProfileResponse might not have resume_file_path if it's strict Pydantic.
                # Usually Orchestrator injects file paths. We accept FullProfile or similar.
                # Assuming profile object has these or we pass them in a context.
                # Checking schemas.py, UserProfileResponse doesn't have file paths usually.
                # We might need to handle this via extra context or assume it's added.
                # For now, return a placeholder or check attribute.

            if field_path == "_cover_letter_upload":
                return getattr(profile, "cover_letter_file_path", None)

            parts = field_path.split(".")
            value = profile.model_dump()
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    return None

                if value is None:
                    return None
            return value
        except Exception:
            return None

    def _match_select_option(self, field: FormField, profile_value: str) -> str | None:
        """
        Given a select field's options and a profile value, find the best matching option.
        Uses fuzzy matching.
        """
        if not field.options:
            return None

        profile_val_str = str(profile_value).lower()

        # Exact match first (Value or Text)
        for option in field.options:
            if (
                option["value"].lower() == profile_val_str
                or option["text"].lower() == profile_val_str
            ):
                return option["value"]

        # Fuzzy match using difflib
        best_match = None
        best_score = 0.0

        for option in field.options:
            text_score = SequenceMatcher(
                None, profile_val_str, option["text"].lower()
            ).ratio()
            val_score = SequenceMatcher(
                None, profile_val_str, option["value"].lower()
            ).ratio()

            score = max(text_score, val_score)

            if score > best_score and score > 0.6:  # Threshold 0.6
                best_score = score
                best_match = option["value"]

        return best_match

    def _heuristic_match(self, field: FormField) -> Optional[str]:
        """Tries to match a field using regex heuristics."""
        text_to_check = (
            f"{field.name} {field.id} {field.label} {field.placeholder}".lower()
        )

        for profile_key, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_to_check, re.IGNORECASE):
                    return profile_key
        return None

    async def map_fields(
        self, fields: List[FormField], profile: UserProfileResponse
    ) -> List[FieldMapping]:
        """
        Maps fields using 2-stage process: Heuristic -> AI.
        """
        mappings: List[FieldMapping] = []
        ambiguous_fields: List[FormField] = []

        # Stage 1: Heuristics
        for field in fields:
            # Skip hidden inputs generally unless we are sure (e.g. sometimes hidden fields carry tokens)
            if field.type == "hidden":
                continue

            matched_key = self._heuristic_match(field)

            if matched_key:
                val = self._get_profile_value(profile, matched_key)

                # Special handling for select fields
                if field.type == "select" or (
                    field.type == "combobox" and field.options
                ):
                    if val is not None:
                        val = self._match_select_option(field, str(val))

                if val is not None:
                    mappings.append(
                        FieldMapping(
                            selector=field.selector,
                            profile_field=matched_key,
                            value=val,
                            confidence=0.9,
                        )
                    )
                    continue

            # If not matched, add to ambiguous
            ambiguous_fields.append(field)

        # Stage 2: AI for Ambiguous Fields
        if ambiguous_fields:
            logger.info(
                "Resolving ambiguous fields with AI", count=len(ambiguous_fields)
            )
            # We convert UserProfileResponse to FullProfile-like dict if possible,
            # but UserProfileResponse from schemas is what we have.
            # Assuming profile has all data needed.
            ai_mappings = await self.map_ambiguous_fields(ambiguous_fields, profile)
            mappings.extend(ai_mappings)

        return mappings

    async def map_ambiguous_fields(
        self, fields: List[FormField], profile: UserProfileResponse
    ) -> List[FieldMapping]:
        """
        Use Gemini to map fields that heuristics couldn't resolve.
        """
        # Build compact field descriptions
        field_descriptions = []
        for i, field in enumerate(fields):
            desc = {
                "index": i,
                "tag": field.type,  # using type as tag approximation or add tag to FormField
                "label": field.label or "",
                "name": field.name or "",
                "id": field.id or "",
                "placeholder": field.placeholder or "",
                "required": field.required,
                "options_sample": [o["text"] for o in field.options[:10]]
                if field.options
                else [],
            }
            field_descriptions.append(desc)

        # Compact profile summary
        # Dump and exclude heavy/irrelevant fields if any.
        # UserProfileResponse is roughly 4KB-10KB, fits easily in context.
        profile_data = profile.model_dump(exclude_none=True)

        prompt = f"""
        You are an expert at filling job application forms.

        USER PROFILE:
        {json.dumps(profile_data, indent=2, default=str)}

        UNRESOLVED FORM FIELDS:
        {json.dumps(field_descriptions, indent=2)}

        For each field, determine what value from the user's profile should be entered.
        
        RULES:
        - Select fields: choose the best matching option VALUE based on text (not just index).
        - For questions not directly in the profile, use 'application_answers' logic or infer from experience/skills.
        - For free-text fields asking 'why interested', generate a brief 2-3 sentence response using profile data.
        - If a field cannot be answered from available data, set value to null.
        - For checkboxes, use boolean true/false.
        - For date fields, use YYYY-MM-DD format.

        Return JSON:
        {{
            "mappings": [
                {{
                    "index": 0,
                    "value": "the value to fill",
                    "reasoning": "brief explanation"
                }}
            ]
        }}
        """

        try:
            response = await self.brain.model.generate_content_async(prompt)
            # Cleaning fallback
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            result = json.loads(text)

            mappings = []
            for item in result.get("mappings", []):
                if item.get("value") is not None:
                    idx = item.get("index", -1)
                    if 0 <= idx < len(fields):
                        field = fields[idx]
                        mappings.append(
                            FieldMapping(
                                selector=field.selector,
                                value=item["value"],
                                confidence=0.7,
                                requires_ai=True,
                                profile_field=item.get("reasoning", "AI-mapped"),
                            )
                        )

            return mappings

        except Exception as e:
            logger.error("AI field mapping failed", error=str(e))
            return []
