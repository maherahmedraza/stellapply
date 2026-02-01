import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.base_model import BaseModel

if TYPE_CHECKING:
    from src.modules.identity.domain.models import User


class ResumeSource(str, PyEnum):
    SCRATCH = "SCRATCH"
    UPLOAD = "UPLOAD"
    PERSONA = "PERSONA"
    LINKEDIN = "LINKEDIN"


class TemplateCategory(str, PyEnum):
    CLASSIC = "CLASSIC"
    MODERN = "MODERN"
    TECHNICAL = "TECHNICAL"
    EXECUTIVE = "EXECUTIVE"
    CREATIVE = "CREATIVE"


class SectionType(str, PyEnum):
    SUMMARY = "SUMMARY"
    EXPERIENCE = "EXPERIENCE"
    EDUCATION = "EDUCATION"
    SKILLS = "SKILLS"
    PROJECTS = "PROJECTS"
    CERTIFICATIONS = "CERTIFICATIONS"
    LANGUAGES = "LANGUAGES"
    CUSTOM = "CUSTOM"


class ResumeTemplate(BaseModel):
    """Resume template definition and Jinja2 content."""

    __tablename__ = "resume_templates"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    thumbnail_url: Mapped[str | None] = mapped_column(String(512))
    template_file: Mapped[str] = mapped_column(Text, nullable=False)  # Jinja2 content
    category: Mapped[TemplateCategory] = mapped_column(
        Enum(TemplateCategory), nullable=False, default=TemplateCategory.CLASSIC
    )
    is_ats_optimized: Mapped[bool] = mapped_column(Boolean, default=True)
    settings: Mapped[dict[str, Any]] = mapped_column(JSONB, default={})

    resumes: Mapped[list["Resume"]] = relationship(
        "Resume", back_populates="template", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ResumeTemplate(name={self.name}, category={self.category})>"


class Resume(BaseModel):
    """Main resume container model."""

    __tablename__ = "resumes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resume_templates.id")
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[dict[str, Any]] = mapped_column(JSONB, default={})
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)

    ats_score: Mapped[float | None] = mapped_column(Float)
    word_count: Mapped[int | None] = mapped_column(Integer)
    file_path: Mapped[str | None] = mapped_column(String(512))  # MinIO path

    created_from: Mapped[ResumeSource] = mapped_column(
        Enum(ResumeSource), nullable=False, default=ResumeSource.SCRATCH
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="resumes")
    template: Mapped[ResumeTemplate | None] = relationship(
        "ResumeTemplate", back_populates="resumes"
    )
    sections: Mapped[list["ResumeSection"]] = relationship(
        "ResumeSection", back_populates="resume", cascade="all, delete-orphan"
    )
    ats_analyses: Mapped[list["ATSAnalysis"]] = relationship(
        "ATSAnalysis", back_populates="resume", cascade="all, delete-orphan"
    )
    versions: Mapped[list["ResumeVersion"]] = relationship(
        "ResumeVersion", back_populates="resume", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_resumes_user_id_is_primary", "user_id", "is_primary"),
        Index(
            "ix_resumes_user_id_created_at_desc",
            "user_id",
            "created_at",
            postgresql_using="btree",
            postgresql_ops={"created_at": "desc"},
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Resume(name={self.name}, user_id={self.user_id}, "
            f"primary={self.is_primary})>"
        )


class ResumeSection(BaseModel):
    """Granular resume content sections."""

    __tablename__ = "resume_sections"

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True
    )
    section_type: Mapped[SectionType] = mapped_column(Enum(SectionType), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[dict[str, Any]] = mapped_column(JSONB, default={})
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)

    resume: Mapped[Resume] = relationship("Resume", back_populates="sections")

    def __repr__(self) -> str:
        return f"<ResumeSection(type={self.section_type}, order={self.order})>"


class ATSAnalysis(BaseModel):
    """Historical ATS scoring and recommendations."""

    __tablename__ = "ats_analyses"

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True
    )
    job_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id")
    )

    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    format_score: Mapped[float | None] = mapped_column(Float)
    content_score: Mapped[float | None] = mapped_column(Float)
    keyword_score: Mapped[float | None] = mapped_column(Float)

    recommendations: Mapped[list[str]] = mapped_column(JSONB, default=[])
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    resume: Mapped[Resume] = relationship("Resume", back_populates="ats_analyses")

    def __repr__(self) -> str:
        return f"<ATSAnalysis(resume_id={self.resume_id}, score={self.overall_score})>"


class ResumeVersion(BaseModel):
    """Version history and snapshots for resumes."""

    __tablename__ = "resume_versions"

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    change_summary: Mapped[str | None] = mapped_column(Text)

    resume: Mapped[Resume] = relationship("Resume", back_populates="versions")

    def __repr__(self) -> str:
        return (
            f"<ResumeVersion(resume_id={self.resume_id}, "
            f"version={self.version_number})>"
        )
