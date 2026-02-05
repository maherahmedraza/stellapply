import asyncio
import uuid
from datetime import date, datetime, UTC

# Import all models to satisfy SQLAlchemy registries
from src.modules.identity.domain.models import User
from src.modules.persona.domain.models import (
    Persona,
    Experience,
    Skill,
    SkillSource,
    DegreeType,
    Education,
    Certification,
    Project,
    ExperienceEnhancement,
)
from src.modules.resume.domain.models import (
    Resume,
    ResumeSource,
    ResumeTemplate,
    ResumeSection,
    ATSAnalysis,
    ResumeVersion,
)
from src.modules.resume.domain.schemas import ResumeCreate, RenderedResume
from src.modules.resume.domain.services import ResumeService


# Mock Repositories for Demonstration
class MockResumeRepository:
    def __init__(self):
        self.resumes = {}

    async def save(self, resume):
        if not hasattr(resume, "id") or not resume.id:
            resume.id = uuid.uuid4()
        self.resumes[resume.id] = resume
        return resume

    async def get_by_id(self, resume_id):
        return self.resumes.get(resume_id)


class MockPersonaRepository:
    def __init__(self, persona):
        self.persona = persona

    async def get_by_user_id(self, user_id):
        return self.persona if self.persona.user_id == user_id else None

    async def get_by_id(self, persona_id):
        return self.persona if self.persona.id == persona_id else None


async def run_demo():
    print("--- Persona-CV Architecture Demo ---")

    user_id = uuid.uuid4()
    persona_id = uuid.uuid4()

    # 1. Create a Persona (The Single Source of Truth)
    persona = Persona(
        id=persona_id,
        user_id=user_id,
        full_name="Jane Doe",
        email="jane@example.com",
        phone="+1234567890",
        location_city="San Francisco",
        location_state="CA",
        summary_original="Experienced software engineer with a focus on AI.",
        summary_active="Senior Software Engineer specializing in Generative AI and scalable backend systems.",
        completeness_score=0.85,
    )

    # Add Experiences
    exp1 = Experience(
        id=uuid.uuid4(),
        persona_id=persona_id,
        company_name="TechCorp",
        job_title="Senior AI Engineer",
        start_date=date(2020, 1, 1),
        is_current=True,
        description_original="Built AI models.",
        description_active="Architected and deployed enterprise-grade LLM solutions using Gemini and LangChain.",
        bullets_active=["Improved model latency by 40%", "Led a team of 5 engineers"],
    )

    exp2 = Experience(
        id=uuid.uuid4(),
        persona_id=persona_id,
        company_name="OldSoft",
        job_title="Full Stack Developer",
        start_date=date(2018, 1, 1),
        end_date=date(2019, 12, 31),
        description_original="Worked on some web apps.",
        description_active="Developed responsive web applications using React and Node.js.",
        bullets_active=["Implemented CI/CD pipelines", "Reduced page load time by 30%"],
    )

    persona.experiences = [exp1, exp2]

    # Add Skill
    skill1 = Skill(
        id=uuid.uuid4(),
        persona_id=persona_id,
        name="Python",
        proficiency_level=5,
        source=SkillSource.USER_DECLARED,
    )
    persona.skills = [skill1]

    # Add Education
    edu1 = Education(
        id=uuid.uuid4(),
        persona_id=persona_id,
        institution_name="State University",
        degree_type=DegreeType.BACHELOR,
        field_of_study="Computer Science",
        graduation_date=date(2017, 5, 1),
    )
    persona.educations = [edu1]

    persona.certifications = []
    persona.projects = []

    print(f"Persona created for {persona.full_name} ({persona_id})")

    # 2. Setup Service
    resume_repo = MockResumeRepository()
    persona_repo = MockPersonaRepository(persona)
    resume_service = ResumeService(resume_repo, persona_repo)

    # 3. Create a Resume (Tailored View)
    resume_create = ResumeCreate(
        user_id=user_id,
        persona_id=persona_id,
        name="AI Engineer Resume",
        target_role="Staff AI Engineer",
        content_selection={
            "summary": "active",
            "experiences": [str(exp1.id)],  # Only select the latest experience
            "experience_versions": {str(exp1.id): "active"},
            "education": [str(edu1.id)],
            "skills": {"selected": [str(skill1.id)]},
        },
    )

    resume = await resume_service.create_resume(resume_create)
    print(f"Resume created: {resume.name} (linked to persona {resume.persona_id})")

    # 4. Render the Resume
    rendered = await resume_service.render_resume(resume.id)

    print("\n--- Rendered Resume Output ---")
    print(f"Name: {rendered.header.name}")
    print(f"Summary: {rendered.summary}")
    print("\nExperiences:")
    for exp in rendered.experiences:
        print(
            f"- {exp.job_title} at {exp.company_name} ({exp.start_date} to {exp.end_date})"
        )
        print(f"  Description: {exp.description}")
        for bullet in exp.bullets:
            print(f"  * {bullet}")

    print("\nEducation:")
    for edu in rendered.education:
        print(
            f"- {edu.degree_type} in {edu.field_of_study} from {edu.institution_name}"
        )

    print("\nSkills:")
    for skill in rendered.skills:
        print(f"- {skill.name} (Level {skill.level})")

    # 5. Verify Content Switching
    print("\n--- Testing Content Selection Update ---")
    # Update resume to use original summary
    from src.modules.resume.domain.schemas import ResumeUpdate

    await resume_service.update_resume(
        resume.id,
        ResumeUpdate(
            name="Original Summary Resume",
            content_selection={
                "summary": "original",
                "experiences": [str(exp1.id), str(exp2.id)],
                "experience_versions": {
                    str(exp1.id): "original",
                    str(exp2.id): "active",
                },
                "education": [str(edu1.id)],
                "skills": {"selected": [str(skill1.id)]},
            },
        ),
    )

    rendered_updated = await resume_service.render_resume(resume.id)
    print(f"Updated Summary (Original): {rendered_updated.summary}")
    print(
        f"Experience 1 Description (Original): {rendered_updated.experiences[0].description}"
    )
    print(
        f"Experience 2 Description (Active): {rendered_updated.experiences[1].description}"
    )


if __name__ == "__main__":
    asyncio.run(run_demo())
