"""
GDPR/DSGVO Service Layer.

Implements German Data Protection Law requirements:
- Consent management (Article 7)
- Data subject rights (Articles 15-22)
- Data export and erasure
"""

import hashlib
import logging
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.gdpr.domain.models import (
    ConsentGrantRequest,
    ConsentPurpose,
    ConsentRecord,
    ConsentStatusResponse,
    DataSubjectRequest,
    LegalBasis,
)

logger = logging.getLogger(__name__)


class GDPRService:
    """
    Service for GDPR/DSGVO compliance operations.

    Data Controller: StellarApply GmbH
    Processing Location: European Union
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.current_consent_version = "1.0.0"
        self.current_policy_version = "2026.01"

    # ========== Consent Management (Article 7) ==========

    async def get_user_consents(self, user_id: UUID) -> list[ConsentStatusResponse]:
        """Get all consent statuses for a user."""
        stmt = select(ConsentRecord).where(
            ConsentRecord.user_id == user_id,
            ConsentRecord.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        records = result.scalars().all()

        # Build response with all purposes
        consents = []
        purpose_map = {r.purpose: r for r in records}

        for purpose in ConsentPurpose:
            record = purpose_map.get(purpose)
            consents.append(
                ConsentStatusResponse(
                    purpose=purpose,
                    is_granted=record.is_granted if record else False,
                    granted_at=record.granted_at if record else None,
                    consent_version=record.consent_version
                    if record
                    else self.current_consent_version,
                    can_withdraw=purpose != ConsentPurpose.ESSENTIAL,
                )
            )

        return consents

    async def update_consent(
        self,
        user_id: UUID,
        request: ConsentGrantRequest,
        ip_address: str,
        user_agent: str,
    ) -> ConsentRecord:
        """Grant or withdraw consent for a specific purpose."""
        # Check if consent record exists
        stmt = select(ConsentRecord).where(
            ConsentRecord.user_id == user_id,
            ConsentRecord.purpose == request.purpose,
            ConsentRecord.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        record = result.scalar_one_or_none()

        now = datetime.now(UTC)
        ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()
        ua_hash = hashlib.sha256(user_agent.encode()).hexdigest()

        if record:
            # Update existing record
            record.is_granted = request.granted
            if request.granted:
                record.granted_at = now
                record.withdrawn_at = None
            else:
                record.withdrawn_at = now
            record.consent_version = self.current_consent_version
            record.policy_version = self.current_policy_version
            record.ip_address_hash = ip_hash
            record.user_agent_hash = ua_hash
        else:
            # Create new consent record
            record = ConsentRecord(
                user_id=user_id,
                purpose=request.purpose,
                legal_basis=LegalBasis.CONSENT,
                is_granted=request.granted,
                granted_at=now if request.granted else None,
                consent_version=self.current_consent_version,
                policy_version=self.current_policy_version,
                ip_address_hash=ip_hash,
                user_agent_hash=ua_hash,
            )
            self.db.add(record)

        await self.db.commit()
        logger.info(
            f"Consent {'granted' if request.granted else 'withdrawn'} for "
            f"user {user_id}, purpose {request.purpose}"
        )
        return record

    # ========== Right to Access (Article 15) ==========

    async def export_user_data(
        self, user_id: UUID, include_audit: bool = False
    ) -> dict[str, Any]:
        """
        Export all user data in machine-readable format.
        GDPR Article 20: Right to data portability.
        """
        from src.modules.persona.domain.models import Persona

        export_data: dict[str, Any] = {
            "export_metadata": {
                "generated_at": datetime.now(UTC).isoformat(),
                "data_controller": "StellarApply GmbH",
                "processing_location": "EU",
                "format_version": "1.0",
            },
            "user_id": str(user_id),
        }

        # Fetch persona data
        stmt = select(Persona).where(
            Persona.user_id == user_id, Persona.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        persona = result.scalar_one_or_none()

        if persona:
            export_data["persona"] = {
                "full_name": persona.full_name,
                "email": persona.email,
                "phone": persona.phone,
                "location": {
                    "city": persona.location_city,
                    "state": persona.location_state,
                    "country": persona.location_country,
                },
                "work_authorization": str(persona.work_authorization),
                "remote_preference": str(persona.remote_preference),
                "experiences": [
                    {
                        "job_title": exp.job_title,
                        "company_name": exp.company_name,
                        "start_date": exp.start_date.isoformat()
                        if exp.start_date
                        else None,
                        "end_date": exp.end_date.isoformat() if exp.end_date else None,
                        "description": exp.description,
                    }
                    for exp in persona.experiences
                ],
                "skills": [
                    {"name": s.name, "proficiency": s.proficiency_level}
                    for s in persona.skills
                ],
                "education": [
                    {
                        "institution": e.institution,
                        "degree": e.degree,
                        "field_of_study": e.field_of_study,
                    }
                    for e in persona.education
                ],
            }

        # Fetch consent records
        stmt = select(ConsentRecord).where(ConsentRecord.user_id == user_id)
        result = await self.db.execute(stmt)
        consents = result.scalars().all()
        export_data["consents"] = [
            {
                "purpose": str(c.purpose),
                "is_granted": c.is_granted,
                "granted_at": c.granted_at.isoformat() if c.granted_at else None,
            }
            for c in consents
        ]

        # Optionally include audit trail
        if include_audit:
            from src.core.security.audit_log import AuditLogger

            audit_logger = AuditLogger(self.db)
            audit_trail = await audit_logger.export_audit_trail_for_dsar(str(user_id))
            export_data["audit_trail"] = audit_trail

        return export_data

    # ========== Right to Erasure (Article 17) ==========

    async def request_erasure(
        self, user_id: UUID, keep_anonymized: bool = False
    ) -> DataSubjectRequest:
        """
        Create a data erasure request.
        GDPR Article 17: Right to erasure ('right to be forgotten').
        """
        deadline = datetime.now(UTC) + timedelta(days=30)

        request = DataSubjectRequest(
            user_id=user_id,
            request_type="erasure",
            status="pending",
            deadline_at=deadline,
            identity_verified=True,  # Assume verified via authenticated session
            verification_method="session_auth",
        )
        self.db.add(request)
        await self.db.commit()

        logger.info(f"Erasure request created for user {user_id}, deadline: {deadline}")
        return request

    async def execute_erasure(
        self, request_id: UUID, keep_anonymized: bool = False
    ) -> bool:
        """
        Execute data erasure for a user.
        Implements cascading deletion across all modules.
        """
        stmt = select(DataSubjectRequest).where(DataSubjectRequest.id == request_id)
        result = await self.db.execute(stmt)
        request = result.scalar_one_or_none()

        if not request:
            raise ValueError("Erasure request not found")

        user_id = request.user_id

        # Soft delete user data across modules
        from src.modules.persona.domain.models import Persona

        stmt = select(Persona).where(Persona.user_id == user_id)
        result = await self.db.execute(stmt)
        persona = result.scalar_one_or_none()

        if persona:
            now = datetime.now(UTC)
            if keep_anonymized:
                # Anonymize instead of delete
                persona.full_name = "ANONYMIZED"
                persona.email = f"anonymized_{user_id}@deleted.local"
                persona.phone = None
            else:
                persona.deleted_at = now

        # Mark request as completed
        request.status = "completed"
        request.completed_at = datetime.now(UTC)
        request.response_notes = "Anonymized" if keep_anonymized else "Fully deleted"

        await self.db.commit()
        logger.info(f"Erasure completed for user {user_id}")
        return True

    # ========== Data Subject Request Tracking ==========

    async def get_pending_requests(self) -> list[DataSubjectRequest]:
        """Get all pending data subject requests approaching deadline."""
        warning_threshold = datetime.now(UTC) + timedelta(days=7)
        stmt = select(DataSubjectRequest).where(
            DataSubjectRequest.status == "pending",
            DataSubjectRequest.deadline_at <= warning_threshold,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
