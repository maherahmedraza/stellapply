import asyncio
import uuid
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


# Mock classes to simulate dependencies
class MockPersonaService:
    async def get_persona_by_user_id(self, user_id: uuid.UUID):
        return MockPersona()


class MockPersona:
    def __init__(self):
        self.skills = [
            MockSkill("Python"),
            MockSkill("FastAPI"),
            MockSkill("SQLAlchemy"),
            MockSkill("React"),
        ]
        self.experiences = [
            MockExperience(
                company_name="TechCorp",
                job_title="Software Engineer",
                achievements=["Built API"],
                description="Backend development",
            )
        ]


class MockSkill:
    def __init__(self, name: str):
        self.name = name


class MockExperience:
    def __init__(self, company_name, job_title, achievements, description):
        self.company_name = company_name
        self.job_title = job_title
        self.achievements = achievements
        self.description = description
        self.description_original = description
        self.description_active = description
        self.description_enhanced = None
        self.bullets_original = []
        self.bullets_active = []
        self.bullets_enhanced = []
        self.skills_used = []  # added missing attr


class MockGeminiClient:
    async def generate_structured(self, prompt: str, schema: Any, **kwargs):
        # Determine based on prompt whether to fail or succeed truthfulness

        # Test Case 1: Safe enhancement (Adding action verbs)
        if "Developed REST APIs" in prompt:
            return MockResponse(
                enhanced_text="Architected and deployed high-performance REST APIs",
                enhancement_type="rephrase",
                skills_referenced=["Python", "FastAPI"],
                has_placeholder_metrics=False,
                verification_needed=False,
                verification_question=None,
                truthfulness_explanation="Improved action verbs using verified skills.",
            )

        # Test Case 2: Fabrication attempt (Adding unverified skill)
        if "trigger_rust_hallucination" in prompt:
            # The AI *tries* to add Rust, but our validator should catch it
            return MockResponse(
                enhanced_text="Built low-latency systems using Rust and Python",
                enhancement_type="rephrase",
                skills_referenced=["Rust", "Python"],
                has_placeholder_metrics=False,
                verification_needed=False,  # AI claims it's fine
                verification_question=None,
                truthfulness_explanation="Added relevant tech stack.",
            )

        # Test Case 3: Metric fabrication (Adding number)
        if "increased revenue" in prompt:
            return MockResponse(
                enhanced_text=" increased revenue by 20%",  # AI invents a number
                enhancement_type="quantify",
                skills_referenced=[],
                has_placeholder_metrics=False,  # AI claims it's real
                verification_needed=False,
                verification_question=None,
                truthfulness_explanation="Quantified impact.",
            )

        print(f"DEBUG: No mock matched for prompt: {prompt[:100]}...")
        return MockResponse(
            enhanced_text="DEBUG_FALLBACK",
            enhancement_type="rephrase",
            skills_referenced=[],
            has_placeholder_metrics=False,
            verification_needed=False,
            verification_question=None,
            truthfulness_explanation="Fallback",
        )


class MockResponse:  # To simulate pydantic model
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def model_dump(self):
        return self.__dict__

    # Add attribute access to match pydantic behavior if needed directly
    def __getattr__(self, item):
        return self.__dict__.get(item)


# Import the class to test (we need to make sure imports work)
# We might need to adjust python path for this to run
import sys
import os

sys.path.append(os.getcwd())

from src.modules.resume.ai.truthful_enhancer import (
    TruthfulResumeEnhancer,
    EnhancementType,
)


async def run_verification():
    print("🚀 Starting Truthful AI Enhancer Verification...\n")

    enhancer = TruthfulResumeEnhancer(
        gemini_client=MockGeminiClient(), persona_service=MockPersonaService()
    )
    user_id = uuid.uuid4()
    context = {"target_role": "Senior Engineer", "requirements": []}

    # --- Test 1: Safe Enhancement ---
    print("Test 1: Safe Enhancement (Verb Improvement)")
    original = "Developed REST APIs using Python"
    result = await enhancer.enhance_bullet_point(original, context, user_id)

    print(f"Original: {result.original_text}")
    print(f"Enhanced: {result.enhanced_text}")
    print(
        f"Status: {'✅ VERIFIED' if not result.requires_user_verification else '⚠️ NEEDS VERIFICATION'}"
    )
    assert "Architected" in result.enhanced_text
    assert not result.requires_user_verification
    print("PASS\n")

    # --- Test 2: Preventing Fabrication (Unverified Skill) ---
    print("Test 2: Preventing Fabrication (Adding 'Rust' - Unverified Skill)")
    # We use a trigger phrase that the Mock AI recognizes to hallucinate 'Rust'
    # But the original text matches the rest of the content so fallback doesn't happen due to low overlap
    original_with_trap = (
        "Built high-performance backend systems [trigger_rust_hallucination]"
    )
    result = await enhancer.enhance_bullet_point(original_with_trap, context, user_id)

    print(f"Original Request: {original_with_trap}")
    print(f"Raw AI Output (Simulated): Built low-latency systems using Rust and Python")
    print(f"Sanitized Output: {result.enhanced_text}")

    # "Rust" should be removed by the validator
    assert "Rust" not in result.enhanced_text
    print(f"Explanation: {result.grounding_explanation}")
    assert "REMOVED unauthorized skills" in result.grounding_explanation
    print("PASS\n")

    # --- Test 3: Metric Verification ---
    print("Test 3: Metric Verification (Unverified Claims)")
    original_metric = "Significantly increased revenue"
    result = await enhancer.enhance_bullet_point(original_metric, context, user_id)

    print(f"Original: {original_metric}")
    print(f"Enhanced: {result.enhanced_text}")
    print(f"Requires Verification: {result.requires_user_verification}")

    # The validator detects "20%" (from mock response) was NOT in original "Significantly..."
    # So it should flag it.
    assert result.requires_user_verification == True
    assert result.metrics_are_placeholder == True
    print(f"Verification Question: {result.verification_prompt}")
    print("PASS\n")

    print("🎉 All Truthfulness Guarantees Verified!")


if __name__ == "__main__":
    asyncio.run(run_verification())
