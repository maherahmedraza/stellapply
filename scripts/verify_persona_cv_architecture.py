import asyncio
import uuid
from datetime import date
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from src.modules.identity.domain.models import User
from src.modules.persona.domain.models import (
    Certification,
    Education,
    Experience,
    Persona,
    Project,
    Skill,
    SkillSource,
)
from src.modules.resume.domain.models import Resume, ResumeTemplate, ResumeSection
from src.modules.resume.domain.services import ResumeService


async def verify_architecture():
    print("🚀 Starting Persona-CV Relationship Architecture Verification\n")

    # 1. Setup Mock Repositories
    resume_repo = MagicMock()
    resume_repo.save = AsyncMock(side_effect=lambda x: x)

    persona_repo = MagicMock()

    # 2. Setup Persona (The Master Record)
    user_id = uuid.uuid4()
    persona_id = uuid.uuid4()

    persona = Persona(
        id=persona_id,
        user_id=user_id,
        full_name="Alex Stellar",
        email="alex@stellarapply.com",
        summary_active="Experienced AI Engineer focused on agentic systems.",
    )

    # Add Experiences
    exp1_id = uuid.uuid4()
    exp1 = Experience(
        id=exp1_id,
        company_name="TechCorp",
        job_title="Senior Engineer",
        description_active="Led development of AI agents.",
        bullets_active=["Improved latency by 20%", "Architected RAG pipeline"],
        start_date=date(2022, 1, 1),
    )

    exp2_id = uuid.uuid4()
    exp2 = Experience(
        id=exp2_id,
        company_name="CloudNine",
        job_title="Software Developer",
        description_active="Fullstack development.",
        bullets_active=["Implemented UI components"],
        start_date=date(2020, 1, 1),
        end_date=date(2021, 12, 31),
    )

    persona.experiences = [exp1, exp2]

    # Add Skills
    skill1 = Skill(
        id=uuid.uuid4(),
        name="Python",
        proficiency_level=5,
        source=SkillSource.USER_DECLARED,
    )
    skill2 = Skill(
        id=uuid.uuid4(),
        name="FastAPI",
        proficiency_level=4,
        source=SkillSource.USER_DECLARED,
    )
    skill3 = Skill(
        id=uuid.uuid4(),
        name="Java",
        proficiency_level=3,
        source=SkillSource.EXPERIENCE_INFERRED,
    )

    persona.skills = [skill1, skill2, skill3]

    persona_repo.get_by_user_id = AsyncMock(return_value=persona)
    persona_repo.get_by_id = AsyncMock(return_value=persona)

    # 3. Initialize Service
    service = ResumeService(resume_repo, persona_repo)

    # 4. Create Resume (The Tailored View)
    print("--- Creating Resume for a Leadership Role ---")
    resume = await service.create_resume(
        user_id=str(user_id),
        name="Leadership CV",
        target_role="Engineering Manager",
        target_job_id=str(uuid.uuid4()),  # Trigger optimization
    )

    # Set a mock return for get_by_id for rendering
    resume_repo.get_by_id = AsyncMock(return_value=resume)

    print(f"✅ Resume Created: {resume.name}")
    print(f"Selection - Experiences: {resume.content_selection['experiences']}")
    print(
        f"Selection - Verified Skills Only: {resume.content_selection['skills']['selected']}"
    )
    print("")

    # 5. Render Resume
    print("--- Rendering Resume Content ---")
    rendered = await service.render_resume(resume.id)

    print(f"✅ Rendered Header: {rendered.header.name} ({rendered.header.email})")
    print(f"✅ Rendered Summary: {rendered.summary}")
    print(f"✅ Rendered Experiences: {len(rendered.experiences)}")
    for exp in rendered.experiences:
        print(f"   - {exp.job_title} @ {exp.company_name}")

    print(
        f"✅ Rendered Skills (Verified Only): {', '.join([s.name for s in rendered.skills])}"
    )
    print("")

    # 6. Verify Single Source of Truth
    print("--- Verifying Single Source of Truth (SSOT) ---")
    persona.full_name = "Alex Updated Stellar"

    print("Updating Persona header...")
    rendered_updated = await service.render_resume(resume.id)
    print(f"✅ Re-rendered Header Name: {rendered_updated.header.name}")

    assert rendered_updated.header.name == "Alex Updated Stellar"
    print(
        "\n🌟 Verification Successful: Resume successfully behaves as a view of the Persona master record."
    )


if __name__ == "__main__":
    asyncio.run(verify_architecture())
