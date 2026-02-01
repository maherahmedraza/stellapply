import uuid
from datetime import date
from enum import StrEnum
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    ARRAY,
    Date,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
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

    # Preferences
    work_authorization: Mapped[WorkAuthorization] = mapped_column(
        Enum(WorkAuthorization), nullable=False, default=WorkAuthorization.NOT_REQUIRED
    )
    remote_preference: Mapped[RemotePreference] = mapped_column(
        Enum(RemotePreference), nullable=False, default=RemotePreference.ANY
    )

    # AI Search data
    summary_embedding: Mapped[Any | None] = mapped_column(Vector(768))
    completeness_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationships
    experiences: Mapped[list["Experience"]] = relationship(
        "Experience",
        back_populates="persona",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    educations: Mapped[list["Education"]] = relationship(
        "Education",
        back_populates="persona",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    skills: Mapped[list["Skill"]] = relationship(
        "Skill", back_populates="persona", cascade="all, delete-orphan", lazy="selectin"
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
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    description: Mapped[str | None] = mapped_column(Text)
    achievements: Mapped[list[str]] = mapped_column(ARRAY(Text), default=[])
    skills_used: Mapped[list[str]] = mapped_column(ARRAY(String(100)), default=[])

    experience_embedding: Mapped[Any | None] = mapped_column(Vector(768))

    persona: Mapped["Persona"] = relationship("Persona", back_populates="experiences")

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
    answer_embedding: Mapped[Any | None] = mapped_column(Vector(768))

    persona: Mapped["Persona"] = relationship(
        "Persona", back_populates="behavioral_answers"
    )

    def __repr__(self) -> str:
        return f"<BehavioralAnswer(type={self.question_type})>"
