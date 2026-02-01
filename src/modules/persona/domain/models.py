import uuid
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.base_model import BaseModel


class Persona(BaseModel):
    __tablename__ = "personas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    preferred_name: Mapped[str | None] = mapped_column(String(100))
    pronouns: Mapped[str | None] = mapped_column(String(50))
    location: Mapped[dict[str, Any]] = mapped_column(JSONB, default={})
    experience: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=[])
    education: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=[])
    skills: Mapped[dict[str, Any]] = mapped_column(JSONB, default={})
    summary_embedding: Mapped[Any | None] = mapped_column(
        Vector(768)
    )  # BERT-sized vector
    completeness_score: Mapped[int] = mapped_column(Integer, default=0)
