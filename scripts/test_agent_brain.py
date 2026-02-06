import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, Any
from unittest.mock import AsyncMock

from src.agent.brain import AgentBrain
from src.agent.models.schemas import PageContext
from src.modules.profile.schemas import (
    UserProfileResponse,
    PersonalInfoSchema,
    SearchPreferencesSchema,
    AgentRulesSchema,
    ApplicationAnswersSchema,
    ResumeStrategySchema,
    AddressSchema,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def verify_brain_engine():
    try:
        logger.info("1. Initializing Agent Brain...")

        # Mock Profile using Pydantic Schema
        profile = UserProfileResponse(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            personal_info=PersonalInfoSchema(
                first_name="Neo",
                last_name="Anderson",
                email="neo@matrix.com",
                phone="+1234567890",
                address=AddressSchema(city="Zion", country="Real World"),
            ),
            search_preferences=SearchPreferencesSchema(),
            agent_rules=AgentRulesSchema(),
            application_answers=ApplicationAnswersSchema(),
            resume_strategy=ResumeStrategySchema(),
            experience=[],
            education=[],
            projects=[],
            skills=["Python", "AI"],
            certifications=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        brain = AgentBrain(profile)

        # Mock Gemini Model
        class MockResponse:
            text = '```json\n{"thinking": "I see an apply button.", "action_type": "click", "selector": "#apply-btn", "confidence": 1.0, "expected_result": "Application form opens"}\n```'

        brain.model.generate_content_async = AsyncMock(return_value=MockResponse())

        # Test 1: Brain Decision
        logger.info("2. Testing Brain Decision Making...")

        goal = "Apply to the Software Engineer job at MetaCortex."

        page_context = PageContext(
            url="https://metacortex.com/careers",
            title="MetaCortex Careers",
            dom_snippet="<body><button id='apply-btn'>Apply Now</button></body>",
            forms=[],
        )

        action = await brain.decide_next_action(goal=goal, page_context=page_context)
        logger.info(f"Brain Action: {action.action_type} -> {action.selector}")
        logger.info(f"Thinking: {action.thinking}")

        if action.action_type != "click":
            logger.error(
                f"EXPECTED 'click', GOT '{action.action_type}'. Thinking: {action.thinking}"
            )

        # Validate logic (should click apply)
        assert action.action_type == "click"
        assert "apply-btn" in action.selector or "Apply" in action.selector
        logger.info("Brain Logic Verification PASSED ✅")

        # Test 2: Data Extraction
        logger.info("3. Testing Data Extraction...")

        content = "Job Title: Senior Developer. Salary: $120,000. Location: Remote."
        schema = {"title": "str", "salary": "str", "location": "str"}

        class MockExtractionResponse:
            text = '```json\n{"title": "Senior Developer", "salary": "$120,000", "location": "Remote"}\n```'

        brain.model.generate_content_async.return_value = MockExtractionResponse()

        data = await brain.extract_data(content, schema)
        logger.info(f"Extracted Data: {data}")

        assert "Senior Developer" in data.get("title", "")
        logger.info("Data Extraction Verification PASSED ✅")

    except Exception as e:
        logger.error(f"Verification FAILED: {e}")
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(verify_brain_engine())
