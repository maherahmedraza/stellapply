import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import BYTEA, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.base_model import BaseModel

if TYPE_CHECKING:
    from src.modules.resume.domain.models import Resume


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email_encrypted: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    email_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    governance_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default={})

    resumes: Mapped[list["Resume"]] = relationship("Resume", back_populates="user")
