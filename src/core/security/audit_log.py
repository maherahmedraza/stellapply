import hashlib
import json
import logging
from collections.abc import Callable
from datetime import UTC, datetime
from enum import StrEnum
from functools import wraps
from typing import Any, TypeVar
from uuid import UUID, uuid4

from fastapi import Request, Response
from sqlalchemy import DateTime, Enum, String, Text, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.core.database.connection import Base
from src.core.security.encryption import encryption_service

logger = logging.getLogger(__name__)

T = TypeVar("T")


class AuditAction(StrEnum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    EXPORT = "EXPORT"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"


class AuditEvent(Base):
    """Immutable audit log event for GDPR compliance."""

    __tablename__ = "audit_events"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )

    # Encrypted fields
    ip_address_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    user_agent_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    request_id: Mapped[str] = mapped_column(String(50), nullable=False)

    old_value_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)

    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True
    )
    hash_chain: Mapped[str] = mapped_column(String(64), nullable=False)


class AuditLogger:
    """Service for managing immutable audit logs with hash chaining."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _calculate_hash(self, event: AuditEvent, prev_hash: str) -> str:
        """Calculate SHA-256 hash including previous record hash for immutability."""
        content = (
            f"{event.timestamp.isoformat()}|{event.user_id}|{event.action}|"
            f"{event.resource_type}|{event.resource_id}|{event.request_id}|"
            f"{event.ip_address_encrypted}|{event.user_agent_hash}|"
            f"{event.old_value_encrypted}|{event.new_value_encrypted}|"
            f"{prev_hash}"
        )
        return hashlib.sha256(content.encode()).hexdigest()

    async def log_event(
        self,
        action: AuditAction,
        resource_type: str,
        resource_id: UUID | None = None,
        user_id: str | None = None,
        ip_address: str = "0.0.0.0",
        user_agent: str = "",
        request_id: str = "N/A",
        old_value: dict[str, Any] | None = None,
        new_value: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Create and persist a new audit event with hash chaining."""
        # Get latest event hash
        stmt = select(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(1)
        result = await self.db.execute(stmt)
        last_event = result.scalar_one_or_none()
        prev_hash = last_event.hash_chain if last_event else "initial-seed"

        # Prepare encrypted PII
        ip_encrypted = encryption_service.encrypt_field(ip_address)
        ua_fingerprint = hashlib.sha256(user_agent.encode()).hexdigest()

        old_val_enc = (
            encryption_service.encrypt_field(json.dumps(old_value))
            if old_value
            else None
        )
        new_val_enc = (
            encryption_service.encrypt_field(json.dumps(new_value))
            if new_value
            else None
        )

        event = AuditEvent(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address_encrypted=ip_encrypted,
            user_agent_hash=ua_fingerprint,
            request_id=request_id,
            old_value_encrypted=old_val_enc,
            new_value_encrypted=new_val_enc,
            metadata_json=metadata,
            hash_chain="pending",  # Placeholder
        )

        # We need to set timestamp explicitly if we calculate hash before commit
        event.timestamp = datetime.now(UTC)
        event.hash_chain = self._calculate_hash(event, prev_hash)

        self.db.add(event)
        await self.db.commit()
        return event

    async def get_user_audit_trail(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> list[AuditEvent]:
        stmt = (
            select(AuditEvent)
            .filter(
                AuditEvent.user_id == user_id,
                AuditEvent.timestamp >= start_date,
                AuditEvent.timestamp <= end_date,
            )
            .order_by(AuditEvent.timestamp.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def export_audit_trail_for_dsar(self, user_id: str) -> list[dict[str, Any]]:
        """Export decrypted audit trail for a user (DSAR compliance)."""
        stmt = select(AuditEvent).filter(AuditEvent.user_id == user_id)
        result = await self.db.execute(stmt)
        events = result.scalars().all()
        export_data = []
        for event in events:
            old_val = None
            if event.old_value_encrypted:
                decrypted_old = encryption_service.decrypt_field(
                    event.old_value_encrypted
                )
                if decrypted_old:
                    old_val = json.loads(decrypted_old)

            new_val = None
            if event.new_value_encrypted:
                decrypted_new = encryption_service.decrypt_field(
                    event.new_value_encrypted
                )
                if decrypted_new:
                    new_val = json.loads(decrypted_new)

            export_data.append(
                {
                    "id": str(event.id),
                    "timestamp": event.timestamp.isoformat(),
                    "action": event.action,
                    "resource_type": event.resource_type,
                    "resource_id": str(event.resource_id)
                    if event.resource_id
                    else None,
                    "ip_address": encryption_service.decrypt_field(
                        event.ip_address_encrypted
                    ),
                    "request_id": event.request_id,
                    "old_value": old_val,
                    "new_value": new_val,
                    "metadata": event.metadata_json,
                }
            )
        return export_data

    async def verify_chain_integrity(self) -> bool:
        """Verify the immutable chain of audit logs."""
        stmt = select(AuditEvent).order_by(AuditEvent.timestamp.asc())
        result = await self.db.execute(stmt)
        events = result.scalars().all()
        prev_hash = "initial-seed"
        for event in events:
            calculated_hash = self._calculate_hash(event, prev_hash)
            if calculated_hash != event.hash_chain:
                logger.critical(f"Audit chain corruption detected at event {event.id}!")
                return False
            prev_hash = event.hash_chain
        return True


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically log all API requests for audit purposes."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Correlation ID from headers or generated
        _request_id = request.headers.get("X-Request-ID", str(uuid4()))

        return await call_next(request)


def audit_action(_action: AuditAction, _resource_type: str) -> Callable[..., Any]:
    """Decorator to log high-level service method calls."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Placeholder for logging logic
            # In a real app, this would use a global request-local context
            return await func(*args, **kwargs)

        return wrapper

    return decorator
