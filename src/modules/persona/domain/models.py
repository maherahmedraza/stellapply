import uuid
from datetime import UTC, date, datetime
from enum import Enum as PyEnum
from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.modules.resume.domain.models import Resume

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    ARRAY,
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.base_model import BaseModel
from src.core.security.encryption import EncryptedString


class WorkAuthorization(StrEnum):
    CITIZEN = "CITIZEN"
    PERMANENT_RESIDENT = "PERMANENT_RESIDENT"
    H1B = "H1B"
    L1 = "L1"
    F1_OPT = "F1_OPT"
    J1 = "J1"
    TN = "TN"
    OTHER = "OTHER"
    NOT_REQUIRED = "NOT_REQUIRED"


class RemotePreference(StrEnum):
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ONSITE = "ONSITE"
    ANY = "ANY"


class DegreeType(StrEnum):
    HIGH_SCHOOL = "HIGH_SCHOOL"
    ASSOCIATE = "ASSOCIATE"
    BACHELOR = "BACHELOR"
    MASTER = "MASTER"
    DOCTORATE = "DOCTORATE"
    PROFESSIONAL = "PROFESSIONAL"
    CERTIFICATION = "CERTIFICATION"
    CERTIFICATE = "CERTIFICATION"  # Alias for frontend compatibility
    OTHER = "OTHER"


class SkillCategory(StrEnum):
    TECHNICAL = "TECHNICAL"
    SOFT = "SOFT"
    TOOL = "TOOL"
    LANGUAGE = "LANGUAGE"


class QuestionType(StrEnum):
    CHALLENGE = "CHALLENGE"
    ACHIEVEMENT = "ACHIEVEMENT"
    FAILURE = "FAILURE"
    LEADERSHIP = "LEADERSHIP"
    TEAMWORK = "TEAMWORK"
    CONFLICT = "CONFLICT"
    GENERAL = "GENERAL"


class CompanySize(StrEnum):
    STARTUP = "STARTUP"
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"
    ENTERPRISE = "ENTERPRISE"


class SkillSource(PyEnum):
    USER_DECLARED = "user_declared"  # User explicitly added
    RESUME_PARSED = "resume_parsed"  # Extracted from uploaded resume
    EXPERIENCE_INFERRED = "experience_inferred"  # Inferred from job descriptions
    CERTIFICATION = "certification"  # From verified certification
    VERIFIED = "verified"  # User confirmed inferred skill


class Persona(BaseModel):
    """Main model for candidate persona, including PII and preferences."""

    __tablename__ = "personas"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        unique=True,
        index=True,
        nullable=False,
    )

    # Encrypted PII
    full_name: Mapped[str] = mapped_column(EncryptedString(255), nullable=False)
    email: Mapped[str] = mapped_column(EncryptedString(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(EncryptedString(50), nullable=True)

    # Location
    location_city: Mapped[str | None] = mapped_column(String(100))
    location_state: Mapped[str | None] = mapped_column(String(100))
    location_country: Mapped[str | None] = mapped_column(String(100))

    # Professional Links
    linkedin_url: Mapped[str | None] = mapped_column(String(255))
    github_url: Mapped[str | None] = mapped_column(String(255))
    portfolio_url: Mapped[str | None] = mapped_column(String(255))
    website_url: Mapped[str | None] = mapped_column(String(255))

    # Application Email Configuration
    # Separate email for receiving responses from job applications
    application_email: Mapped[str | None] = mapped_column(
        EncryptedString(255), nullable=True
    )
    # If True, agent uses the persona's primary email for applications
    use_login_email_for_applications: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # Professional Summary (can be AI-enhanced)
    summary_original: Mapped[str | None] = mapped_column(Text)
    summary_enhanced: Mapped[str | None] = mapped_column(Text)
    summary_active: Mapped[str | None] = mapped_column(Text)

    # Preferences
    work_authorization: Mapped[WorkAuthorization] = mapped_column(
        Enum(WorkAuthorization), nullable=False, default=WorkAuthorization.NOT_REQUIRED
    )
    requires_sponsorship: Mapped[bool] = mapped_column(Boolean, default=False)
    remote_preference: Mapped[RemotePreference] = mapped_column(
        Enum(RemotePreference), nullable=False, default=RemotePreference.ANY
    )

    # AI Search data
    summary_embedding: Mapped[Vector | None] = mapped_column(Vector(768))
    embedding: Mapped[Vector | None] = mapped_column(Vector(768))
    embedding_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    completeness_score: Mapped[float] = mapped_column(Float, default=0.0)
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # Relationships
    experiences: Mapped[list["Experience"]] = relationship(
        "Experience",
        back_populates="persona",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(Experience.start_date)",
    )
    educations: Mapped[list["Education"]] = relationship(
        "Education",
        back_populates="persona",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(Education.graduation_date)",
    )
    skills: Mapped[list["Skill"]] = relationship(
        "Skill", back_populates="persona", cascade="all, delete-orphan", lazy="selectin"
    )
    certifications: Mapped[list["Certification"]] = relationship(
        "Certification",
        back_populates="persona",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="persona",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    career_preference: Mapped["CareerPreference"] = relationship(
        "CareerPreference",
        back_populates="persona",
        cascade="all, delete-orphan",
        uselist=False,
    )
    behavioral_answers: Mapped[list["BehavioralAnswer"]] = relationship(
        "BehavioralAnswer",
        back_populates="persona",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    resumes: Mapped[list["Resume"]] = relationship(
        "Resume",
        back_populates="persona",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def get_verified_skills(self) -> list["Skill"]:
        """Return only skills that are verified/declared (not just inferred)"""
        verified_sources = [
            SkillSource.USER_DECLARED,
            SkillSource.CERTIFICATION,
            SkillSource.VERIFIED,
        ]
        return [s for s in self.skills if s.source in verified_sources]

    def get_all_facts(self) -> dict[str, Any]:
        """Return all facts for truth-grounding in AI enhancement"""
        return {
            "skills": [
                {
                    "name": s.name,
                    "level": s.proficiency_level,
                    "verified": s.source != SkillSource.EXPERIENCE_INFERRED,
                }
                for s in self.skills
            ],
            "experiences": [
                {
                    "company": e.company_name,
                    "title": e.job_title,
                    "description": e.description_active,
                    "achievements": e.achievements,
                }
                for e in self.experiences
            ],
            "education": [
                {
                    "institution": e.institution_name,
                    "degree": str(e.degree_type),
                    "field": e.field_of_study,
                }
                for e in self.educations
            ],
            "certifications": [
                {"name": c.name, "issuer": c.issuer} for c in self.certifications
            ],
        }

    def __repr__(self) -> str:
        return (
            f"<Persona(id={self.id}, user_id={self.user_id}, "
            f"completeness={self.completeness_score})>"
        )


class Experience(BaseModel):
    """Professional experience record."""

    __tablename__ = "persona_experiences"

    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("personas.id"), index=True, nullable=False
    )

    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_url: Mapped[str | None] = mapped_column(String(255))
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255))
    employment_type: Mapped[str | None] = mapped_column(String(50))  # full_time, etc.

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)

    # Original content (user-provided)
    description_original: Mapped[str | None] = mapped_column(Text)
    bullets_original: Mapped[list[str]] = mapped_column(ARRAY(Text), default=[])

    # Enhanced content (AI-improved)
    description_enhanced: Mapped[str | None] = mapped_column(Text)
    bullets_enhanced: Mapped[list[str]] = mapped_column(ARRAY(Text), default=[])

    # Active content (what's used in CVs)
    description_active: Mapped[str | None] = mapped_column(Text)
    bullets_active: Mapped[list[str]] = mapped_column(ARRAY(Text), default=[])

    # Achievements (distinct from bullets)
    achievements: Mapped[list[str]] = mapped_column(ARRAY(Text), default=[])

    # Skills used in this role
    skills_used: Mapped[list[str]] = mapped_column(ARRAY(String(100)), default=[])

    experience_embedding: Mapped[Vector | None] = mapped_column(Vector(768))

    # Metadata
    order: Mapped[int] = mapped_column(Integer, default=0)

    @property
    def description(self) -> str | None:
        return self.description_active or self.description_original

    # Relationships
    persona: Mapped["Persona"] = relationship("Persona", back_populates="experiences")
    enhancement_history: Mapped[list["ExperienceEnhancement"]] = relationship(
        "ExperienceEnhancement",
        back_populates="experience",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Experience(company={self.company_name}, title={self.job_title})>"


class Education(BaseModel):
    """Educational background record."""

    __tablename__ = "persona_educations"

    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("personas.id"), index=True, nullable=False
    )

    institution_name: Mapped[str] = mapped_column(String(255), nullable=False)
    degree_type: Mapped[DegreeType] = mapped_column(Enum(DegreeType), nullable=False)
    field_of_study: Mapped[str] = mapped_column(String(255), nullable=False)
    graduation_date: Mapped[date] = mapped_column(Date, nullable=False)
    gpa: Mapped[float | None] = mapped_column(Float, nullable=True)

    persona: Mapped["Persona"] = relationship("Persona", back_populates="educations")

    def __repr__(self) -> str:
        return (
            f"<Education(institution={self.institution_name}, "
            f"degree={self.degree_type})>"
        )


class Skill(BaseModel):
    """Skills associated with a persona."""

    __tablename__ = "persona_skills"

    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("personas.id"), index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    category: Mapped[SkillCategory] = mapped_column(
        Enum(SkillCategory), nullable=False, default=SkillCategory.TECHNICAL
    )
    proficiency_level: Mapped[int] = mapped_column(Integer, default=1)  # 1-5
    years_of_experience: Mapped[int | None] = mapped_column(Integer)

    # Source and verification
    source: Mapped[SkillSource] = mapped_column(
        Enum(SkillSource), nullable=False, default=SkillSource.USER_DECLARED
    )
    source_detail: Mapped[str | None] = mapped_column(String(255))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Evidence (for inferred skills)
    evidence: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=[])

    persona: Mapped["Persona"] = relationship("Persona", back_populates="skills")

    def __repr__(self) -> str:
        return f"<Skill(name={self.name}, level={self.proficiency_level})>"


class CareerPreference(BaseModel):
    """Aggregated career preferences and targets."""

    __tablename__ = "persona_career_preferences"

    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personas.id"),
        unique=True,
        index=True,
        nullable=False,
    )

    target_titles: Mapped[list[str]] = mapped_column(ARRAY(String(255)), default=[])
    target_industries: Mapped[list[str]] = mapped_column(ARRAY(String(255)), default=[])

    salary_min: Mapped[int | None] = mapped_column(Integer)
    salary_max: Mapped[int | None] = mapped_column(Integer)

    company_sizes: Mapped[list[CompanySize]] = mapped_column(
        ARRAY(Enum(CompanySize)), default=[]
    )
    blacklisted_companies: Mapped[list[str]] = mapped_column(
        ARRAY(String(255)), default=[]
    )
    dream_companies: Mapped[list[str]] = mapped_column(ARRAY(String(255)), default=[])

    persona: Mapped["Persona"] = relationship(
        "Persona", back_populates="career_preference"
    )

    def __repr__(self) -> str:
        return f"<CareerPreference(persona_id={self.persona_id})>"


class BehavioralAnswer(BaseModel):
    """Behavioral interview question answers for AI context."""

    __tablename__ = "persona_behavioral_answers"

    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("personas.id"), index=True, nullable=False
    )

    question_type: Mapped[QuestionType] = mapped_column(
        Enum(QuestionType), nullable=False
    )
    # Encrypted answer text
    answer: Mapped[str] = mapped_column(EncryptedString, nullable=False)
    answer_embedding: Mapped[Vector | None] = mapped_column(Vector(768))

    persona: Mapped["Persona"] = relationship(
        "Persona", back_populates="behavioral_answers"
    )

    def __repr__(self) -> str:
        return f"<BehavioralAnswer(type={self.question_type})>"


class Certification(BaseModel):
    """Professional certifications."""

    __tablename__ = "persona_certifications"

    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("personas.id"), index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuer: Mapped[str] = mapped_column(String(255), nullable=False)
    issue_date: Mapped[date | None] = mapped_column(Date)
    expiry_date: Mapped[date | None] = mapped_column(Date)
    credential_id: Mapped[str | None] = mapped_column(String(255))
    credential_url: Mapped[str | None] = mapped_column(String(500))

    persona: Mapped["Persona"] = relationship(
        "Persona", back_populates="certifications"
    )


class Project(BaseModel):
    """Professional or personal projects."""

    __tablename__ = "persona_projects"

    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("personas.id"), index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(String(500))
    github_url: Mapped[str | None] = mapped_column(String(500))
    technologies: Mapped[list[str]] = mapped_column(ARRAY(String(100)), default=[])

    persona: Mapped["Persona"] = relationship("Persona", back_populates="projects")


class ExperienceEnhancement(BaseModel):
    """Tracks AI enhancements made to an experience."""

    __tablename__ = "experience_enhancements"

    experience_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persona_experiences.id"),
        index=True,
        nullable=False,
    )

    field_enhanced: Mapped[str] = mapped_column(String(50), nullable=False)
    original_content: Mapped[str] = mapped_column(Text, nullable=False)
    enhanced_content: Mapped[str] = mapped_column(Text, nullable=False)

    enhancement_type: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(20), nullable=False)

    # User verification
    user_approved: Mapped[bool | None] = mapped_column(Boolean)
    user_modified: Mapped[bool] = mapped_column(Boolean, default=False)
    user_final_content: Mapped[str | None] = mapped_column(Text)

    # Source tracking
    sources_used: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=[])

    experience: Mapped["Experience"] = relationship(
        "Experience", back_populates="enhancement_history"
    )
