import pytest
from src.modules.resume.ai.enhancement_rules import (
    EnhancementRulesEngine,
    RuleViolationType,
)


@pytest.fixture
def rules_engine():
    return EnhancementRulesEngine()


@pytest.fixture
def persona_context():
    return {
        "verified_skills": {"python", "react", "fastapi"},
        "verified_tools": {"docker", "git"},
        "verified_industries": {"fintech", "saas"},
        "verified_job_titles": {"software engineer", "backend developer"},
        "verified_companies": {"tech corp", "innovate soft"},
        "verified_achievements": [],
        "verified_metrics": ["20%", "50ms"],
        "verified_responsibilities": [],
        "years_of_experience": {"python": 3, "react": 2},
        "education": [],
        "certifications": [],
        "projects": [],
    }


def test_rules_engine_valid_enhancement(rules_engine, persona_context):
    original = "I wrote python code"
    enhanced = "Developed high-performance Python applications using FastAPI"

    result = rules_engine.validate_enhancement(original, enhanced, persona_context)

    assert result["is_valid"] is True
    assert len(result["blocking_violations"]) == 0
    assert result["can_proceed"] is True


def test_rules_engine_detects_fabricated_skill(rules_engine, persona_context):
    original = "I wrote python code"
    # Kubernetes is not in verified_tools or verified_skills
    enhanced = "Developed python applications and managed Kubernetes clusters"

    result = rules_engine.validate_enhancement(original, enhanced, persona_context)

    assert result["is_valid"] is False
    assert any(
        v["rule"] == "no_fabricated_skills" for v in result["blocking_violations"]
    )
    assert result["can_proceed"] is False


def test_rules_engine_triggers_metric_confirmation(rules_engine, persona_context):
    original = "I fixed bugs"
    # 50% is a new metric not in verified_metrics
    enhanced = "Fixed critical bugs reducing downtime by 50%"

    result = rules_engine.validate_enhancement(original, enhanced, persona_context)

    # It should not be a blocking violation if it's just a warning
    assert result["is_valid"] is True
    assert any(v["rule"] == "metrics_need_confirmation" for v in result["warnings"])
    assert result["requires_confirmation"] is True


def test_rules_engine_allows_existing_metric(rules_engine, persona_context):
    original = "I improved speed by 20%"
    # 20% is already in verified_metrics
    enhanced = "Optimized system performance achieving a 20% speed improvement"

    result = rules_engine.validate_enhancement(original, enhanced, persona_context)

    # 20% is in context, so it should not trigger a warning
    assert not any(v["rule"] == "metrics_need_confirmation" for v in result["warnings"])


def test_rules_engine_detects_industry_mismatch(rules_engine, persona_context):
    original = "Worked as a developer"
    # "healthcare" is not in verified_industries
    enhanced = "Strategic developer in the healthcare space"

    result = rules_engine.validate_enhancement(original, enhanced, persona_context)

    assert any(v["rule"] == "industry_alignment" for v in result["warnings"])
    assert result["requires_confirmation"] is True
