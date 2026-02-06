import asyncio
import uuid
import logging

from src.agent.agents.scout_helpers import SearchURLBuilder
from src.modules.profile.schemas import SearchPreferencesSchema
from src.agent.agents.scout import ScoutAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_url_builder():
    logger.info("Testing SearchURLBuilder...")

    prefs = SearchPreferencesSchema(
        target_roles=["Python Developer", "Data Scientist"],
        locations=["Berlin", "Remote"],
        min_salary=60000,
    )

    urls = SearchURLBuilder.build_urls(prefs)

    for u in urls:
        logger.info(f"Generated: {u}")

    # Assertions
    assert len(urls) >= 4  # 2 roles * 2 locations
    assert any("linkedin" in u["platform"] for u in urls)
    assert any("indeed" in u["platform"] for u in urls)
    # Check encoding
    assert (
        "Python%20Developer" in urls[0]["search_url"]
        or "Python+Developer" in urls[0]["search_url"]
    )

    logger.info("SearchURLBuilder Test PASSED ✅")


async def test_scout_agent_instantiation():
    logger.info("Testing ScoutAgent Instantiation...")
    user_id = uuid.uuid4()
    task_id = uuid.uuid4()

    agent = ScoutAgent(user_id, task_id)
    assert agent.user_id == user_id
    assert agent.task_id == task_id
    assert agent.discovered_jobs == []

    logger.info("ScoutAgent Instantiation PASSED ✅")


if __name__ == "__main__":
    test_url_builder()
    asyncio.run(test_scout_agent_instantiation())
