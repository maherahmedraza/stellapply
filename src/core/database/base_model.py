from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.core.database.connection import Base


class AuditMixin:
    """Mixin for audit fields."""

    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )

    @declared_attr
    def created_by(cls) -> Mapped[str | None]:
        return mapped_column(String(255), nullable=True)  # External ID or User ID


class SoftDeleteMixin:
    """Mixin for soft delete (GDPR Compliance)."""

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def soft_delete(self: Any) -> None:
        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)


class BaseModel(Base, AuditMixin, SoftDeleteMixin):
    __abstract__ = True
    pass
