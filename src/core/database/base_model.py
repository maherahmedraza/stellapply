import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, Integer, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, Query, mapped_column
from sqlalchemy.sql import func


class TimestampMixin:
    """Mixin for automatic creation and update timestamps."""

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


class SoftDeleteMixin:
    """Mixin for soft delete support (GDPR compliance)."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deleted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    @property
    def is_active(self) -> bool:
        """Helper to check if record is not deleted."""
        return self.deleted_at is None

    def soft_delete(self, user_id: uuid.UUID | None = None) -> None:
        """Mark record as deleted without removing from DB."""
        self.deleted_at = datetime.now(UTC)
        self.deleted_by = user_id


class AuditMixin:
    """Mixin for auditing user actions and optimistic locking."""

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class TenantMixin:
    """Mixin for multi-tenant isolation (Row Level Security foundation)."""

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), index=True, nullable=False
    )


class SoftDeleteQuery(Query[Any]):
    """Query extension for automatic soft delete filtering."""

    def __iter__(self) -> Any:
        return super().filter_by(deleted_at=None).__iter__()


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class BaseModel(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Base model with full data governance features."""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


# Event Listeners for automatic governance
@event.listens_for(BaseModel, "before_update", propagate=True)
def receive_before_update(_mapper: Any, _connection: Any, target: Any) -> None:
    """Automatically increment version number on every update."""
    if hasattr(target, "version") and target.version is not None:
        target.version += 1


@event.listens_for(BaseModel, "before_insert", propagate=True)
def receive_before_insert(_mapper: Any, _connection: Any, target: Any) -> None:
    """Ensure version is initialized and timestamps are set if needed."""
    if hasattr(target, "version") and target.version is None:
        target.version = 1
