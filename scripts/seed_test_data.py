"""
Seed script for creating test persona and sample jobs.
Run with: python -m scripts.seed_test_data
"""

import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.connection import async_engine, get_db
from src.modules.identity.domain.models import User
from src.modules.job_search.domain.models import Job
from src.modules.persona.domain.models import (
    CareerPreference,
    CompanySize,
    DegreeType,
    Education,
    Experience,
    Persona,
    RemotePreference,
    Skill,
    SkillCategory,
    WorkAuthorization,
)


async def create_test_persona(db: AsyncSession, user_id: UUID) -> Persona:
    """Create a test persona for the given user."""

    # Check if persona already exists
    from sqlalchemy import select

    result = await db.execute(select(Persona).where(Persona.user_id == user_id))
    existing = result.scalar_one_or_none()
    if existing:
        print(f"Persona already exists for user {user_id}")
        return existing

    # Create persona
    persona = Persona(
        user_id=user_id,
        full_name="Alex Johnson",
        email="alex.johnson@example.com",
        phone="+1-555-123-4567",
        location_city="San Francisco",
        location_state="CA",
        location_country="USA",
        work_authorization=WorkAuthorization.CITIZEN,
        remote_preference=RemotePreference.REMOTE,
        completeness_score=85.0,
    )
    db.add(persona)
    await db.flush()

    # Add experiences
    experiences = [
        Experience(
            persona_id=persona.id,
            company_name="TechCorp Inc",
            job_title="Senior Software Engineer",
            start_date=datetime(2021, 3, 1).date(),
            end_date=None,  # Current job
            description=(
                "Lead backend development for payment processing platform. "
                "Architected microservices handling 1M+ transactions daily. "
                "Mentored 4 junior engineers."
            ),
            achievements=[
                "Reduced payment processing latency by 40%",
                "Designed and implemented real-time fraud detection system",
                "Led migration from monolith to microservices",
            ],
            skills_used=["Python", "Go", "PostgreSQL", "Redis", "Kafka", "AWS"],
        ),
        Experience(
            persona_id=persona.id,
            company_name="DataFlow Labs",
            job_title="Data Engineer",
            start_date=datetime(2019, 1, 1).date(),
            end_date=datetime(2021, 2, 28).date(),
            description=(
                "Built data pipelines processing 10TB+ daily. "
                "Implemented ML feature store for recommendations."
            ),
            achievements=[
                "Built ETL pipeline reducing processing time by 60%",
                "Implemented data quality monitoring system",
            ],
            skills_used=["Python", "Spark", "Airflow", "SQL", "dbt"],
        ),
        Experience(
            persona_id=persona.id,
            company_name="StartupXYZ",
            job_title="Software Engineer",
            start_date=datetime(2017, 6, 1).date(),
            end_date=datetime(2018, 12, 31).date(),
            description="Full-stack development for B2B SaaS product.",
            achievements=["Launched MVP in 3 months", "Grew user base to 10K MAU"],
            skills_used=["Python", "JavaScript", "React", "Node.js", "PostgreSQL"],
        ),
    ]
    for exp in experiences:
        db.add(exp)

    # Add education
    education = Education(
        persona_id=persona.id,
        institution_name="Stanford University",
        degree_type=DegreeType.MASTER,
        field_of_study="Computer Science",
        graduation_date=datetime(2017, 5, 15).date(),
        gpa=3.8,
    )
    db.add(education)

    # Add skills
    skills = [
        Skill(
            persona_id=persona.id,
            name="Python",
            category=SkillCategory.TECHNICAL,
            proficiency_level=5,
        ),
        Skill(
            persona_id=persona.id,
            name="Go",
            category=SkillCategory.TECHNICAL,
            proficiency_level=4,
        ),
        Skill(
            persona_id=persona.id,
            name="PostgreSQL",
            category=SkillCategory.TECHNICAL,
            proficiency_level=5,
        ),
        Skill(
            persona_id=persona.id,
            name="Redis",
            category=SkillCategory.TECHNICAL,
            proficiency_level=4,
        ),
        Skill(
            persona_id=persona.id,
            name="Kafka",
            category=SkillCategory.TECHNICAL,
            proficiency_level=3,
        ),
        Skill(
            persona_id=persona.id,
            name="AWS",
            category=SkillCategory.TOOL,
            proficiency_level=4,
        ),
        Skill(
            persona_id=persona.id,
            name="Docker",
            category=SkillCategory.TOOL,
            proficiency_level=4,
        ),
        Skill(
            persona_id=persona.id,
            name="Kubernetes",
            category=SkillCategory.TOOL,
            proficiency_level=3,
        ),
        Skill(
            persona_id=persona.id,
            name="Spark",
            category=SkillCategory.TECHNICAL,
            proficiency_level=4,
        ),
        Skill(
            persona_id=persona.id,
            name="Airflow",
            category=SkillCategory.TOOL,
            proficiency_level=4,
        ),
        Skill(
            persona_id=persona.id,
            name="SQL",
            category=SkillCategory.TECHNICAL,
            proficiency_level=5,
        ),
        Skill(
            persona_id=persona.id,
            name="Distributed Systems",
            category=SkillCategory.TECHNICAL,
            proficiency_level=4,
        ),
        Skill(
            persona_id=persona.id,
            name="Leadership",
            category=SkillCategory.SOFT,
            proficiency_level=4,
        ),
        Skill(
            persona_id=persona.id,
            name="Communication",
            category=SkillCategory.SOFT,
            proficiency_level=4,
        ),
    ]
    for skill in skills:
        db.add(skill)

    # Add career preferences
    career_pref = CareerPreference(
        persona_id=persona.id,
        target_titles=[
            "Senior Software Engineer",
            "Staff Engineer",
            "Data Engineer",
            "Platform Engineer",
        ],
        target_industries=["Technology", "Fintech", "AI/ML"],
        salary_min=180000,
        salary_max=300000,
        company_sizes=[CompanySize.MEDIUM, CompanySize.LARGE, CompanySize.ENTERPRISE],
        dream_companies=["Stripe", "OpenAI", "Anthropic", "Google", "Netflix"],
        blacklisted_companies=[],
    )
    db.add(career_pref)

    await db.commit()
    print(f"Created persona for user {user_id}")
    return persona


async def create_sample_jobs(db: AsyncSession) -> list[Job]:
    """Create sample jobs for testing."""

    jobs_data = [
        {
            "external_id": "greenhouse:stripe:12345",
            "source": "greenhouse",
            "url": "https://stripe.com/jobs/12345",
            "title": "Senior Software Engineer",
            "company": "Stripe",
            "location": "San Francisco, CA",
            "description": (
                "Build payment infrastructure that powers millions of businesses worldwide. "
                "Work on distributed systems handling millions of transactions per second. "
                "Requirements: 5+ years experience, Python/Go, distributed systems."
            ),
            "salary_min": 180000,
            "salary_max": 250000,
            "salary_currency": "USD",
            "job_type": "full-time",
            "work_setting": "hybrid",
            "raw_data": {
                "skills": ["Python", "Go", "Distributed Systems", "PostgreSQL", "Redis"]
            },
            "posted_at": datetime.now(UTC) - timedelta(days=2),
        },
        {
            "external_id": "lever:airbnb:67890",
            "source": "lever",
            "url": "https://airbnb.com/careers/67890",
            "title": "Staff Data Engineer",
            "company": "Airbnb",
            "location": "Remote",
            "description": (
                "Design and build data pipelines using Spark, Airflow, and modern data stack. "
                "Lead projects that impact millions of hosts and guests. ML platform experience preferred."
            ),
            "salary_min": 200000,
            "salary_max": 280000,
            "salary_currency": "USD",
            "job_type": "full-time",
            "work_setting": "remote",
            "raw_data": {"skills": ["Spark", "Airflow", "Python", "SQL", "Kafka"]},
            "posted_at": datetime.now(UTC) - timedelta(days=1),
        },
        {
            "external_id": "greenhouse:openai:11111",
            "source": "greenhouse",
            "url": "https://openai.com/careers/11111",
            "title": "Backend Engineer",
            "company": "OpenAI",
            "location": "San Francisco, CA",
            "description": (
                "Build infrastructure for training and serving large language models. "
                "Python, distributed systems, and ML infrastructure experience preferred."
            ),
            "salary_min": 220000,
            "salary_max": 350000,
            "salary_currency": "USD",
            "job_type": "full-time",
            "work_setting": "onsite",
            "raw_data": {
                "skills": [
                    "Python",
                    "ML Infrastructure",
                    "Distributed Systems",
                    "CUDA",
                    "PyTorch",
                ]
            },
            "posted_at": datetime.now(UTC) - timedelta(days=3),
        },
        {
            "external_id": "greenhouse:figma:22222",
            "source": "greenhouse",
            "url": "https://figma.com/careers/22222",
            "title": "Platform Engineer",
            "company": "Figma",
            "location": "Remote (US)",
            "description": (
                "Build and scale the platform that powers Figma. "
                "Work on CI/CD, Kubernetes, and developer tooling."
            ),
            "salary_min": 170000,
            "salary_max": 230000,
            "salary_currency": "USD",
            "job_type": "full-time",
            "work_setting": "remote",
            "raw_data": {"skills": ["Kubernetes", "Docker", "AWS", "Terraform", "Go"]},
            "posted_at": datetime.now(UTC) - timedelta(days=5),
        },
        {
            "external_id": "lever:notion:33333",
            "source": "lever",
            "url": "https://notion.so/careers/33333",
            "title": "Senior ML Engineer",
            "company": "Notion",
            "location": "New York, NY",
            "description": (
                "Build ML features that help teams organize their knowledge. "
                "Experience with NLP and recommendation systems required."
            ),
            "salary_min": 190000,
            "salary_max": 270000,
            "salary_currency": "USD",
            "job_type": "full-time",
            "work_setting": "hybrid",
            "raw_data": {
                "skills": ["Python", "NLP", "PyTorch", "Recommendation Systems"]
            },
            "posted_at": datetime.now(UTC) - timedelta(days=7),
        },
    ]

    created_jobs = []
    from sqlalchemy import select

    for job_data in jobs_data:
        # Check if job already exists
        result = await db.execute(
            select(Job).where(Job.external_id == job_data["external_id"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Job already exists: {job_data['title']} at {job_data['company']}")
            created_jobs.append(existing)
            continue

        job = Job(**job_data)
        db.add(job)
        created_jobs.append(job)
        print(f"Created job: {job_data['title']} at {job_data['company']}")

    await db.commit()
    return created_jobs


async def get_or_create_test_user(db: AsyncSession) -> User:
    """Get existing test user or create one."""
    from sqlalchemy import select

    # Try to find existing user
    result = await db.execute(
        select(User).where(User.email == "debug_test_2@example.com")
    )
    user = result.scalar_one_or_none()

    if user:
        print(f"Found existing user: {user.email} (id: {user.id})")
        return user

    # Create new test user if not found
    user = User(
        email="test_persona@stellapply.ai",
        keycloak_id="test-keycloak-id-12345",
        full_name="Test User",
    )
    db.add(user)
    await db.commit()
    print(f"Created test user: {user.email} (id: {user.id})")
    return user


async def main():
    """Run the seed script."""
    print("=" * 50)
    print("StellarApply Test Data Seeding")
    print("=" * 50)

    async with AsyncSession(async_engine) as db:
        # Get or create test user
        user = await get_or_create_test_user(db)

        # Create persona for user
        persona = await create_test_persona(db, user.id)

        # Create sample jobs
        jobs = await create_sample_jobs(db)

        print("\n" + "=" * 50)
        print("Seeding Complete!")
        print(f"  - User ID: {user.id}")
        print(f"  - Persona ID: {persona.id}")
        print(f"  - Jobs created: {len(jobs)}")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
