import sys
import os
from uuid import uuid4

# Add src to path
sys.path.append(os.getcwd())

try:
    from src.agent.orchestrator import AgentOrchestrator
    from src.agent.brain import AgentBrain
    from src.agent.models.pipeline import PipelineConfig, FilterConfig, SearchSource
    from src.agent.models.entities import AgentSession
    from src.agent.tasks.pipeline import run_agent_pipeline
    from src.agent.browser.pool import BrowserPool
    from src.modules.profile.schemas import (
        UserProfileResponse,
        PersonalInfoSchema,
        SearchPreferencesSchema,
        AgentRulesSchema,
        ApplicationAnswersSchema,
        ResumeStrategySchema,
    )

    print("✅ All imports successful.")

    # Test Instantiation
    user_id = uuid4()
    session_id = uuid4()
    pool = BrowserPool()

    orch = AgentOrchestrator(user_id=user_id, session_id=session_id, browser_pool=pool)
    print("✅ AgentOrchestrator instantiated.")

    config = PipelineConfig(
        search_sources=[
            SearchSource(platform="linkedin", url="https://linkedin.com/jobs")
        ],
        filters=FilterConfig(),
    )
    print("✅ PipelineConfig instantiated.")

    # Mock Profile
    profile = UserProfileResponse(
        id=uuid4(),
        user_id=user_id,
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        personal_info=PersonalInfoSchema(
            first_name="Test", last_name="User", email="test@example.com"
        ),
        search_preferences=SearchPreferencesSchema(),
        agent_rules=AgentRulesSchema(),
        application_answers=ApplicationAnswersSchema(),
        resume_strategy=ResumeStrategySchema(),
        experience=[],
        education=[],
        projects=[],
        skills=[],
        certifications=[],
    )

    # Manually instantiate brain for verification
    orch.brain = AgentBrain(profile)

    # Test Brain methods existence
    if hasattr(orch.brain, "score_job") and hasattr(orch.brain, "extract_data"):
        print("✅ AgentBrain has required methods.")
    else:
        print("❌ AgentBrain missing methods!")

except Exception as e:
    print(f"❌ Verification failed: {e}")
    import traceback

    traceback.print_exc()
