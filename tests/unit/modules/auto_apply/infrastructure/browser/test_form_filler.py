# ruff: noqa: SLF001
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from playwright.async_api import Locator, Page

from src.modules.auto_apply.infrastructure.browser.form_filler import (
    FieldType,
    FormField,
    FormFieldDetector,
    FormFiller,
    PersonaField,
)
from src.modules.job_search.domain.models import Job
from src.modules.persona.domain.models import Persona


@pytest.fixture
def detector():
    return FormFieldDetector()


@pytest.fixture
def mock_persona_service():
    service = AsyncMock()
    persona = Persona(
        user_id=uuid4(),
        full_name="John Doe",
        email="john@example.com",
        phone="1234567890",
        location_city="New York",
        location_state="NY",
        location_country="USA",
    )
    service.get_persona_by_user_id.return_value = persona
    return service


@pytest.fixture
def mock_question_answerer():
    qa = AsyncMock()
    qa.answer_question.return_value = "AI Answer"
    return qa


@pytest.fixture
def form_filler(detector, mock_persona_service, mock_question_answerer):
    return FormFiller(detector, mock_persona_service, mock_question_answerer)


@pytest.mark.asyncio
async def test_detect_fields_finds_inputs(detector):
    page = AsyncMock(spec=Page)

    input1 = AsyncMock(spec=Locator)
    input1.is_visible.return_value = True
    input1.evaluate = AsyncMock(return_value="input")
    input1.get_attribute = AsyncMock(
        side_effect=lambda attr: {
            "type": "text",
            "name": "first_name",
            "id": "fname",
            "required": "true",
        }.get(attr)
    )

    label_locator = AsyncMock(spec=Locator)
    label_locator.count.return_value = 1
    label_locator.first.inner_text = AsyncMock(return_value="First Name")

    main_locator = AsyncMock()
    main_locator.all.return_value = [input1]

    def locator_side_effect(selector):
        if "label" in selector:
            return label_locator
        return main_locator

    page.locator.side_effect = locator_side_effect
    input1.page = page

    fields = await detector.detect_fields(page)

    assert len(fields) == 1
    assert fields[0].mapping == PersonaField.FIRST_NAME


@pytest.mark.asyncio
async def test_form_filler_fill_application(form_filler):
    page = AsyncMock(spec=Page)
    user_id = uuid4()
    job = Job(title="Engineer", company="Tech Corp", description="Python code")

    # Mock detected fields
    field1 = FormField(
        selector="#fname",
        field_type=FieldType.TEXT,
        label="First Name",
        mapping=PersonaField.FIRST_NAME,
    )
    field2 = FormField(
        selector="#q1",
        field_type=FieldType.TEXTAREA,
        label="Why do you want this job?",
        mapping=PersonaField.CUSTOM_QUESTION,
    )

    form_filler.detector = AsyncMock()
    form_filler.detector.detect_fields.side_effect = [
        [field1, field2],
        [],
    ]  # 2nd call empty (next page check fails)

    # Mock Next button failure to exit loop
    # locator("button...").first.count = 0
    next_btn = AsyncMock()
    next_btn.count.return_value = 0
    page.locator.return_value.first = next_btn

    result = await form_filler.fill_application(
        page, user_id, job, "/path/resume.pdf", "/path/cover.pdf"
    )

    assert result.success is True
    assert len(result.filled_fields) == 2

    # Check field 1 filled with Persona data
    # page.locator(#fname).first.fill("John")
    # But wait, we mocked page.locator general return above.

    # To verify specific calls, we'd need more complex mocks.
    # Trusting the result dict is easier:
    # Verification via result dict is easier:
    assert result.filled_fields[0]["field"] == "First Name"
    assert result.filled_fields[0]["value"] == "John"

    assert result.filled_fields[1]["field"] == "Why do you want this job?"
    assert result.filled_fields[1]["value"] == "AI Answer"


@pytest.mark.asyncio
async def test_get_field_value_logic(form_filler, mock_persona_service):
    persona = mock_persona_service.get_persona_by_user_id.return_value
    job = Job(title="Role", company="Comp", description="Desc")

    # 1. Direct Mapping
    f_email = FormField(
        selector="#e",
        field_type=FieldType.EMAIL,
        label="Email",
        mapping=PersonaField.EMAIL,
    )
    val = await form_filler._get_field_value(f_email, persona, job, "", "")
    assert val == "john@example.com"

    # 2. AI Question
    f_custom = FormField(
        selector="#c",
        field_type=FieldType.TEXTAREA,
        label="Describe yourself in 500 words",
        mapping=PersonaField.CUSTOM_QUESTION,
    )
    val = await form_filler._get_field_value(f_custom, persona, job, "", "")
    assert val == "AI Answer"


def test_map_to_persona_heuristics(detector):
    assert (
        detector._map_to_persona("First Name", "fname", "") == PersonaField.FIRST_NAME
    )
    assert detector._map_to_persona("Last Name", "lname", "") == PersonaField.LAST_NAME
    assert detector._map_to_persona("Misc", "unk", "") == PersonaField.UNKNOWN
