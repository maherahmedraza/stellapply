import logging
import re
from enum import Enum

from playwright.async_api import Locator, Page
from pydantic import BaseModel

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
    SALARY_EXPECTATION = "salary_expectation"
    START_DATE = "start_date"
    VISA_STATUS = "visa_status"
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    UNKNOWN = "unknown"


class FormField(BaseModel):
    selector: str
    field_type: FieldType
    label: str
    required: bool = False
    max_length: int | None = None
    options: list[str] | None = None
    mapping: PersonaField = PersonaField.UNKNOWN


class FormFieldDetector:
    """
    Detects and maps form fields on a page to persona fields.
    """

    def __init__(self) -> None:
        # Heuristic rules: (Regex Pattern, PersonaField)
        self.mapping_rules = [
            (r"(?i)first\s*name", PersonaField.FIRST_NAME),
            (r"(?i)last\s*name", PersonaField.LAST_NAME),
            (r"(?i)full\s*name", PersonaField.FULL_NAME),
            (r"(?i)email", PersonaField.EMAIL),
            (r"(?i)phone|mobile", PersonaField.PHONE),
            (r"(?i)linkedin", PersonaField.LINKEDIN),
            (r"(?i)website|portfolio|github", PersonaField.WEBSITE),
            (r"(?i)resume|cv", PersonaField.RESUME),
            (r"(?i)cover\s*letter", PersonaField.COVER_LETTER),
            (r"(?i)salary|compensation|expected", PersonaField.SALARY_EXPECTATION),
            (r"(?i)start\s*date|available", PersonaField.START_DATE),
            (r"(?i)visa|sponsorship|work\s*auth", PersonaField.VISA_STATUS),
            (r"(?i)address", PersonaField.ADDRESS),
            (r"(?i)city", PersonaField.CITY),
            (r"(?i)state|province", PersonaField.STATE),
            (r"(?i)zip|postal", PersonaField.ZIP),
            (r"(?i)country", PersonaField.COUNTRY),
        ]

    async def detect_fields(self, page: Page) -> list[FormField]:
        """Scans the page for form inputs and returns a list of mapped fields."""
        detected_fields: list[FormField] = []

        # 1. Inputs
        inputs = await page.locator("input, textarea, select").all()

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

        # Determine Selector (ID preferred, then Name, then Generic)
        if id_attr:
            selector = f"#{id_attr}"
        elif name_attr:
            selector = f"[name='{name_attr}']"
        else:
            # Fallback - might perform poorly if structure changes, but OK for now
            # In a real scenario, we'd generate a robust path
            return None

        # Determine Label
        label_text = await self._find_label(element, id_attr, name_attr)

        # Determine Field Type
        field_type = self._determine_field_type(tag_name, input_type)

        # Determine Mapping
        mapping = self._map_to_persona(label_text, name_attr, id_attr)

        # Skip obvious non-fields (submit buttons, hidden inputs)
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

        # 4. Infer from nearby text (complex, skipped for MVP)
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

    def _map_to_persona(self, label: str, name: str, id_attr: str) -> PersonaField:
        """Maps input to a persona field using heuristic rules."""
        # Combine cues text for searching
        search_text = f"{label} {name} {id_attr}".lower()

        for pattern, field in self.mapping_rules:
            if re.search(pattern, search_text):
                return field

        return PersonaField.UNKNOWN
