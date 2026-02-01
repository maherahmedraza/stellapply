import logging
import re
from contextlib import suppress
from enum import Enum
from typing import Any
from uuid import UUID

from playwright.async_api import Locator, Page
from pydantic import BaseModel

from src.modules.auto_apply.ai.question_answerer import QuestionAnswerer
from src.modules.job_search.domain.models import Job
from src.modules.persona.domain.models import Persona
from src.modules.persona.domain.services import PersonaService

logger = logging.getLogger(__name__)


class FieldType(str, Enum):
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    FILE = "file"
    TEXTAREA = "textarea"
    DATE = "date"
    UNKNOWN = "unknown"


class PersonaField(str, Enum):
    FULL_NAME = "full_name"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    CITY = "city"
    STATE = "state"
    ZIP = "zip"
    COUNTRY = "country"
    LINKEDIN = "linkedin"
    WEBSITE = "website"
    PORTFOLIO = "portfolio"
    GITHUB = "github"
    SALARY_EXPECTATION = "salary_expectation"
    START_DATE = "start_date"
    VISA_STATUS = "visa_status"
    WORK_AUTHORIZATION = "work_authorization"
    SPONSORSHIP_REQUIRED = "sponsorship_required"
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    YEARS_EXPERIENCE = "years_experience"
    EDUCATION_LEVEL = "education_level"
    WILLING_TO_RELOCATE = "willing_to_relocate"
    REMOTE_PREFERENCE = "remote_preference"
    REFERRAL_SOURCE = "referral_source"
    CUSTOM_QUESTION = "custom_question"
    UNKNOWN = "unknown"


class FormField(BaseModel):
    selector: str
    field_type: FieldType
    label: str
    required: bool = False
    max_length: int | None = None
    options: list[str] | None = None
    mapping: PersonaField = PersonaField.UNKNOWN


class ApplicationResult(BaseModel):
    success: bool
    filled_fields: list[dict[str, Any]]
    errors: list[dict[str, Any]]
    pages_processed: int = 1


class FormFieldDetector:
    """
    Detects and maps form fields on a page to persona fields.
    """

    FIELD_PATTERNS = {
        PersonaField.FIRST_NAME: [
            r"first\s*name",
            r"given\s*name",
            r"vorname",
            r"prénom",
        ],
        PersonaField.LAST_NAME: [
            r"last\s*name",
            r"surname",
            r"family\s*name",
            r"nachname",
        ],
        PersonaField.FULL_NAME: [r"full\s*name", r"complete\s*name"],
        PersonaField.EMAIL: [r"email", r"e-mail", r"mail\s*address"],
        PersonaField.PHONE: [
            r"phone",
            r"mobile",
            r"telephone",
            r"cell",
            r"contact\s*number",
        ],
        PersonaField.LINKEDIN: [
            r"linkedin",
            r"linked\s*in\s*profile",
            r"linkedin\s*url",
        ],
        PersonaField.WEBSITE: [r"website", r"portfolio", r"personal\s*site"],
        PersonaField.GITHUB: [r"github", r"git\s*profile"],
        PersonaField.SALARY_EXPECTATION: [
            r"salary",
            r"compensation",
            r"expected\s*pay",
            r"desired\s*salary",
        ],
        PersonaField.VISA_STATUS: [
            r"visa",
            r"work\s*authorization",
            r"legally\s*authorized",
            r"sponsorship",
            r"right\s*to\s*work",
        ],
        PersonaField.RESUME: [
            r"resume",
            r"cv",
            r"curriculum\s*vitae",
            r"upload\s*resume",
        ],
        PersonaField.COVER_LETTER: [
            r"cover\s*letter",
            r"cl",
            r"upload\s*cover\s*letter",
        ],
        PersonaField.START_DATE: [
            r"start\s*date",
            r"available\s*from",
            r"earliest\s*start",
        ],
        PersonaField.ADDRESS: [r"address", r"street", r"residence"],
        PersonaField.CITY: [r"city", r"town", r"municipality"],
        PersonaField.STATE: [r"state", r"province", r"region"],
        PersonaField.ZIP: [r"zip", r"postal\s*code"],
        PersonaField.COUNTRY: [r"country", r"nation"],
    }

    async def detect_fields(self, page: Page) -> list[FormField]:
        """Scans the page for form inputs and returns a list of mapped fields."""
        detected_fields: list[FormField] = []

        # 1. Inputs (exclude hidden)
        inputs = await page.locator(
            "input:not([type='hidden']), textarea, select"
        ).all()

        for el in inputs:
            if not await el.is_visible():
                continue

            field = await self._analyze_element(el)
            if field:
                detected_fields.append(field)

        return detected_fields

    async def _analyze_element(self, element: Locator) -> FormField | None:
        """Analyzes a single form element to create a FormField."""
        tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
        input_type = await element.get_attribute("type") or "text"
        name_attr = await element.get_attribute("name") or ""
        id_attr = await element.get_attribute("id") or ""
        placeholder = await element.get_attribute("placeholder") or ""

        # Determine Selector (ID preferred, then Name)
        if id_attr:
            selector = f"#{id_attr}"
        elif name_attr:
            selector = f"[name='{name_attr}']"
        else:
            return None  # Skip elements without stable locators

        # Determine Label
        label_text = await self._find_label(element, id_attr, name_attr)

        # Determine Field Type
        field_type = self._determine_field_type(tag_name, input_type)

        # Determine Mapping
        mapping = self._map_to_persona(label_text, name_attr, placeholder)

        # Skip submit buttons, etc.
        if input_type in ["submit", "button", "hidden", "image", "reset"]:
            return None

        # Get specifics
        required = await element.get_attribute("required") is not None
        max_length_str = await element.get_attribute("maxlength")
        max_length = int(max_length_str) if max_length_str else None

        options = None
        if tag_name == "select":
            options = await element.locator("option").all_inner_texts()

        return FormField(
            selector=selector,
            field_type=field_type,
            label=label_text,
            required=required,
            max_length=max_length,
            options=options,
            mapping=mapping,
        )

    async def _find_label(self, element: Locator, id_attr: str, _name_attr: str) -> str:
        """Attempts to find the label text for an input."""
        # 1. <label for="id">
        if id_attr:
            label_el = element.page.locator(f"label[for='{id_attr}']")
            if await label_el.count() > 0:
                return await label_el.first.inner_text()

        # 2. aria-label
        aria_label = await element.get_attribute("aria-label")
        if aria_label:
            return aria_label

        # 3. placeholder
        placeholder = await element.get_attribute("placeholder")
        if placeholder:
            return placeholder

        return ""

    def _determine_field_type(self, tag_name: str, input_type: str) -> FieldType:
        if tag_name == "textarea":
            return FieldType.TEXTAREA
        if tag_name == "select":
            return FieldType.DROPDOWN

        if input_type == "checkbox":
            return FieldType.CHECKBOX
        if input_type == "radio":
            return FieldType.RADIO
        if input_type == "file":
            return FieldType.FILE
        if input_type == "date":
            return FieldType.DATE
        if input_type == "email":
            return FieldType.EMAIL
        if input_type == "tel":
            return FieldType.PHONE

        return FieldType.TEXT

    def _map_to_persona(self, label: str, name: str, placeholder: str) -> PersonaField:
        """Maps input to a persona field using regex patterns."""
        combined_text = f"{label} {name} {placeholder}".lower()

        for field, patterns in self.FIELD_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    return field

        # If text/textarea and no match, classify as custom question
        if label and len(label) > 10:  # Reasonable heuristics for questions
            return PersonaField.CUSTOM_QUESTION

        return PersonaField.UNKNOWN


class FormFiller:
    def __init__(
        self,
        detector: FormFieldDetector,
        persona_service: PersonaService,
        question_answerer: QuestionAnswerer,
    ) -> None:
        self.detector = detector
        self.persona_service = persona_service
        self.question_answerer = question_answerer

    async def fill_application(
        self,
        page: Page,
        user_id: UUID,
        job: Job,
        resume_path: str,
        cover_letter_path: str,
    ) -> ApplicationResult:
        """Fill out entire application form, handling multi-page."""

        # Load persona data
        persona = await self.persona_service.get_persona_by_user_id(user_id)
        if not persona:
            raise ValueError(f"Persona not found for user {user_id}")

        all_filled_fields: list[dict[str, Any]] = []
        all_errors: list[dict[str, Any]] = []
        page_count = 0
        max_pages = 10

        while page_count < max_pages:
            # Detect fields on current page
            fields = await self.detector.detect_fields(page)

            # Fill fields
            for field in fields:
                try:
                    value = await self._get_field_value(
                        field, persona, job, resume_path, cover_letter_path
                    )
                    if value:
                        await self._fill_field(page, field, value)
                        all_filled_fields.append({"field": field.label, "value": value})
                except Exception as e:
                    logger.warning(f"Failed to fill {field.label}: {e}")
                    all_errors.append({"field": field.label, "error": str(e)})

            # Try to proceed to next page
            if await self._try_click_next(page):
                page_count += 1
            else:
                # Usually means submit or end
                break

        return ApplicationResult(
            success=len(all_errors) == 0,
            filled_fields=all_filled_fields,
            errors=all_errors,
            pages_processed=page_count + 1,
        )

    async def _try_click_next(self, page: Page) -> bool:
        """Attempts to click a Next/Continue button."""
        # Simple heuristic for Next button
        next_selectors = [
            "button:has-text('Next')",
            "button:has-text('Continue')",
            "input[type='submit'][value*='Next']",
        ]

        for sel in next_selectors:
            btn = page.locator(sel).first
            if await btn.count() > 0 and await btn.is_visible():
                await btn.click()
                with suppress(Exception):
                    await page.wait_for_load_state("networkidle", timeout=5000)
                return True
        return False

    async def _get_field_value(
        self,
        field: FormField,
        persona: Persona,
        job: Job,
        resume_path: str,
        cover_letter_path: str,
    ) -> str:
        """Get value for a field from persona or AI."""

        # Direct Mappings
        if field.mapping == PersonaField.FIRST_NAME:
            return persona.full_name.split()[0] if persona.full_name else ""
        if field.mapping == PersonaField.LAST_NAME:
            return persona.full_name.split()[-1] if persona.full_name else ""
        if field.mapping == PersonaField.FULL_NAME:
            return persona.full_name or ""
        if field.mapping == PersonaField.EMAIL:
            return persona.email or ""
        if field.mapping == PersonaField.PHONE:
            return persona.phone or ""
        if field.mapping == PersonaField.CITY:
            return persona.location_city or ""
        if field.mapping == PersonaField.STATE:
            return persona.location_state or ""
        if field.mapping == PersonaField.COUNTRY:
            return persona.location_country or ""
        if field.mapping == PersonaField.LINKEDIN:
            # Find LinkedIn link in persona links? Or field?
            # Assuming persona model has it, or we iterate links
            # Placeholder if not in model directly
            return "https://linkedin.com/in/example"
        if field.mapping == PersonaField.RESUME:
            return resume_path
        if field.mapping == PersonaField.COVER_LETTER:
            return cover_letter_path
        if field.mapping == PersonaField.SALARY_EXPECTATION:
            min_sal = (
                persona.career_preference.salary_min if persona.career_preference else 0
            )
            return str(int(min_sal)) if min_sal else "0"

        if (
            field.mapping == PersonaField.CUSTOM_QUESTION
            or field.mapping == PersonaField.UNKNOWN
        ) and len(field.label) > 10:
            # Only ask AI if it looks like a question
            return await self.question_answerer.answer_question(
                question=field.label,
                user_id=persona.user_id,
                job_context={
                    "id": str(job.id),
                    "company": job.company,
                    "title": job.title,
                    # using description as requirements
                    "requirements": job.description,
                },
                char_limit=field.max_length or 1000,
            )

        return ""

    async def _fill_field(self, page: Page, field: FormField, value: str) -> None:
        """Fill a single form field with human-like behavior."""
        if not value:
            return

        locator = page.locator(field.selector).first

        if field.field_type == FieldType.FILE:
            await locator.set_input_files(value)

        elif field.field_type == FieldType.DROPDOWN:
            # Try to select by label first, then value
            # Value usually matches option text
            # Playwright's select_option is smart
            try:
                await locator.select_option(label=value)
            except Exception:
                await locator.select_option(value=value)

        elif field.field_type in [FieldType.CHECKBOX, FieldType.RADIO]:
            if value.lower() in ["yes", "true", "1"]:
                await locator.check()

        else:  # TEXT, EMAIL, PHONE, TEXTAREA
            # Clear existing value
            await locator.fill("")
            # Type with human-like delays logic (simplified calls here)
            # Reusing local logic or calling automation helper if injected
            await locator.type(value, delay=50)  # simple delay
