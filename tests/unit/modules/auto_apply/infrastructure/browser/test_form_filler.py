# ruff: noqa: SLF001
from unittest.mock import AsyncMock

import pytest
from playwright.async_api import Locator, Page

from src.modules.auto_apply.infrastructure.browser.form_filler import (
    FieldType,
    FormFieldDetector,
    PersonaField,
)


@pytest.fixture
def detector():
    return FormFieldDetector()


@pytest.mark.asyncio
async def test_detect_fields_finds_inputs(detector):
    page = AsyncMock(spec=Page)

    # Mock finding inputs
    input1 = AsyncMock(spec=Locator)
    input1.is_visible.return_value = True
    input1.evaluate = AsyncMock(return_value="input")  # tag name
    input1.get_attribute = AsyncMock(
        side_effect=lambda attr: {
            "type": "text",
            "name": "first_name",
            "id": "fname",
            "required": "true",
        }.get(attr)
    )

    # Mock finding label for input1
    label_locator = AsyncMock(spec=Locator)
    label_locator.count.return_value = 1
    label_locator.first.inner_text = AsyncMock(return_value="First Name")
    # page.locator call for label search: locator("label[for='fname']")

    # We need to handle page.locator calls carefully
    # 1. page.locator("input, ...") -> returns locator that has .all()
    # 2. page.locator("label...") -> returns locator for label

    main_locator = AsyncMock()
    main_locator.all.return_value = [input1]

    def locator_side_effect(selector):
        if "label" in selector:
            return label_locator
        return main_locator

    page.locator.side_effect = locator_side_effect

    # Needs to handle element.page.locator access in _find_label
    input1.page = page

    fields = await detector.detect_fields(page)

    assert len(fields) == 1
    field = fields[0]
    assert field.selector == "#fname"
    assert field.field_type == FieldType.TEXT
    assert field.label == "First Name"
    assert field.mapping == PersonaField.FIRST_NAME
    assert field.required is True


@pytest.mark.asyncio
async def test_analyze_element_mapping(detector):
    # Helper to create a mock element
    def create_element(tag, type_attr, name, id_attr, label_text):
        el = AsyncMock(spec=Locator)
        el.evaluate = AsyncMock(return_value=tag)  # for tagName

        attrs = {"type": type_attr, "name": name, "id": id_attr}
        el.get_attribute = AsyncMock(side_effect=lambda k: attrs.get(k))

        # Mock label finding internals
        el.page = AsyncMock(spec=Page)
        lbl = AsyncMock(spec=Locator)
        lbl.count.return_value = 1 if label_text else 0
        lbl.first.inner_text = AsyncMock(return_value=label_text)
        el.page.locator.return_value = lbl

        return el

    # Case 1: Email
    el_email = create_element(
        "input", "email", "user_email", "email_id", "Email Address"
    )
    field_email = await detector._analyze_element(el_email)
    assert field_email.mapping == PersonaField.EMAIL
    assert field_email.field_type == FieldType.EMAIL

    # Case 2: Resume Upload
    el_resume = create_element("input", "file", "resume_upload", "cv", "Upload Resume")
    field_resume = await detector._analyze_element(el_resume)
    assert field_resume.mapping == PersonaField.RESUME
    assert field_resume.field_type == FieldType.FILE

    # Case 3: LinkedIn
    el_li = create_element("input", "text", "linkedin_url", "li", "LinkedIn Profile")
    field_li = await detector._analyze_element(el_li)
    assert field_li.mapping == PersonaField.LINKEDIN

    # Case 4: Phone
    el_phone = create_element("input", "tel", "phone_number", "mobile", "Phone")
    field_phone = await detector._analyze_element(el_phone)
    assert field_phone.mapping == PersonaField.PHONE
    assert field_phone.field_type == FieldType.PHONE


@pytest.mark.asyncio
async def test_determine_field_type(detector):
    assert detector._determine_field_type("textarea", "text") == FieldType.TEXTAREA
    assert detector._determine_field_type("select", "text") == FieldType.DROPDOWN
    assert detector._determine_field_type("input", "checkbox") == FieldType.CHECKBOX
    assert detector._determine_field_type("input", "file") == FieldType.FILE
    assert detector._determine_field_type("input", "text") == FieldType.TEXT


def test_map_to_persona_heuristics(detector):
    # Direct testing of mapping rules
    assert (
        detector._map_to_persona("First Name", "fname", "") == PersonaField.FIRST_NAME
    )
    assert detector._map_to_persona("Last Name", "lname", "") == PersonaField.LAST_NAME
    assert (
        detector._map_to_persona("Full Name", "fullname", "") == PersonaField.FULL_NAME
    )
    assert detector._map_to_persona("Email Address", "email", "") == PersonaField.EMAIL
    assert detector._map_to_persona("Phone Number", "phone", "") == PersonaField.PHONE
    assert (
        detector._map_to_persona("LinkedIn Profile", "linkedin", "")
        == PersonaField.LINKEDIN
    )
    assert (
        detector._map_to_persona("Portfolio Website", "website", "")
        == PersonaField.WEBSITE
    )
    assert (
        detector._map_to_persona("Salary Expectations", "salary", "")
        == PersonaField.SALARY_EXPECTATION
    )
    assert (
        detector._map_to_persona("Are you authorized?", "visa", "")
        == PersonaField.VISA_STATUS
    )
    assert (
        detector._map_to_persona("Random Label", "random", "") == PersonaField.UNKNOWN
    )
