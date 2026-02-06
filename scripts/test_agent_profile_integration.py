import asyncio
import uuid
import logging
from unittest.mock import MagicMock, patch

# Ensure all models are loaded to avoid relationship errors
import src.core.database.all_models  # noqa
from src.core.database.connection import get_db_context
from src.modules.identity.domain.models import User
from src.modules.profile.models import UserProfile
from src.agent.tasks.application import execute

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_integration():
    # 1. Setup Data
    user_id = uuid.uuid4()
    task_id = str(uuid.uuid4())
    payload = {"job_url": "http://example.com/job"}

    async with get_db_context() as session:
        # Create dummy user and profile
        # We need to create User first due to FK
        user = User(
            id=user_id,
            email=f"test_agent_{user_id}@example.com",
            hashed_password="pw",
            is_active=True,
        )
        session.add(user)

        profile = UserProfile(
            user_id=user_id,
            personal_info='{"first_name": "Agent", "last_name": "Smith"}',
            search_preferences={"roles": ["Agent"]},
            agent_rules={"auto_apply": True},
            application_answers='{"strength": "Speed"}',
            resume_strategy={},
        )
        session.add(profile)
        await session.commit()
        logger.info(f"Created test user {user_id} and profile")

    # 2. Mock Agent to avoid browser launch
    with patch("src.agent.tasks.application.ApplicantAgent") as MockAgentClass:
        mock_agent_instance = MagicMock()
        MockAgentClass.return_value = mock_agent_instance

        # Define async run method
        async def mock_run(payload):
            logger.info("Mock Agent run called with payload keys: %s", payload.keys())
            if "profile_data" not in payload:
                raise AssertionError("profile_data missing from payload")

            p_data = payload["profile_data"]
            logger.info("Profile Data received: %s", p_data)

            if p_data["personal_info"]["first_name"] != "Agent":
                raise AssertionError("Profile data mismatch")

            return {"status": "success"}

        mock_agent_instance.run.side_effect = mock_run

        # 3. Execute Task (Sync wrapper calling async logic)
        # execute is the Celery task function
        logger.info("Calling task execute...")
        result = execute(task_id, str(user_id), payload)

        logger.info("Task result: %s", result)
        assert result["status"] == "success"
        logger.info("Integration Test PASSED")

    # Cleanup (Optional, assuming test DB or rollback)


if __name__ == "__main__":
    # execute is a Celery task, so it might be wrapped.
    # But locally importing it gives the wrapper.
    # calling .run() on task object or just calling it if bind=True?
    # execute is decorated with @celery_app.task(bind=True)
    # acts as function but needs 'self'.

    # We can mock 'self'

    # Actually, simpler to test the inner async logic or just invoke the wrapper if we can mock the celery bind.
    # calling execute(task_id, user_id, payload) might fail because first arg is 'self'.

    # Let's import the underlying function if possible, or mock the task wrapper.
    # Celery tasks are callable.

    # Since we are mocking ApplicantAgent, we just need to run the code in execute.
    # execute(task_id, user_id, payload) -> Celery passes self automatically if called via apply_async,
    # but direct call?

    # Direct call typically ignores bind=True argument in some versions, or expects it.
    # Let's try calling with a dummy self.

    pass
    # We usually can't run async code easily in simple script if execute does async_to_sync
    # But execute uses async_to_sync internally.

    # We need to run this test.
    try:
        mock_self = MagicMock()
        # The execute function defined in application.py:
        # def execute(self, task_id, user_id, payload):
        # We call it directly.
        execute(mock_self, str(uuid.uuid4()), str(uuid.uuid4()), payload)
        # Wait, inside test_integration we have real IDs and DB.
    except Exception as e:
        logger.error(f"Execution setup failed: {e}")

    # Let's run the main test logic which repeats the setup
    # We'll just copy the mock setup to main logic
    pass


# Redefining for direct execution
async def run_check():
    user_id = uuid.uuid4()
    task_id = str(uuid.uuid4())
    payload = {"job_url": "http://example.com/job"}

    async with get_db_context() as session:
        # Create dummy user and profile
        user = User(
            id=user_id,
            email=f"test_{user_id}@example.com",
            hashed_password="pw",
            is_active=True,
        )
        session.add(user)
        profile = UserProfile(
            user_id=user_id,
            personal_info='{"first_name": "Neo"}',  # EncryptedString handles string
            search_preferences={},
            agent_rules={},
            application_answers="{}",
            resume_strategy={},
        )
        session.add(profile)
        await session.commit()

    with patch("src.agent.tasks.application.ApplicantAgent") as MockAgent:
        instance = MockAgent.return_value

        async def side_effect(p):
            print(f"DEBUG: Payload keys: {p.keys()}")
            print(f"DEBUG: Profile Data: {p.get('profile_data')}")
            if p["profile_data"]["personal_info"]["first_name"] == "Neo":
                return "SUCCESS"
            return "FAILURE"

        instance.run.side_effect = side_effect

        # Call execute
        # execute uses async_to_sync which requires an event loop.
        # Since we are in an async function, async_to_sync might conflict if it tries to get existing loop.
        # But 'execute' is synchronous.
        # So we should call 'execute' from outside async loop or use run_in_executor.
        pass


# Simpler approach:
# Just run the sync function `execute` in main, mocking the DB patch if needed or relying on real DB.
# Real DB is fine.

if __name__ == "__main__":
    # We need to setup DB data first using async

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    user_id = uuid.uuid4()
    task_id = str(uuid.uuid4())

    async def setup():
        async with get_db_context() as session:
            user = User(
                id=user_id,
                email=f"test_{user_id}@example.com",
                hashed_password="pw",
                is_active=True,
            )
            session.add(user)
            profile = UserProfile(
                user_id=user_id,
                personal_info='{"first_name": "Morpheus"}',
                search_preferences={},
                agent_rules={},
                application_answers="{}",
                resume_strategy={},
            )
            session.add(profile)
            await session.commit()
            print("Setup done")

    loop.run_until_complete(setup())

    # Now run sync execute
    with patch("src.agent.tasks.application.ApplicantAgent") as MockAgent:
        instance = MockAgent.return_value

        async def side_effect(p):
            print(
                f"VERIFICATION: Profile First Name = {p['profile_data']['personal_info'].get('first_name')}"
            )
            return "OK"

        instance.run.side_effect = side_effect

        print("Running execute...")
        mock_self = MagicMock()
        # execute(self, task_id, user_id, payload)
        res = execute(mock_self, str(task_id), str(user_id), {"url": "http://test"})
        print(f"Result: {res}")
