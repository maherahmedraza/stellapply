"""
GDPR API Routes for Data Subject Rights.

German DSGVO Compliance Endpoints:
- GET /consent - Get consent status
- PUT /consent - Update consent
- POST /export - Export user data (Art. 20)
- POST /erasure - Request data deletion (Art. 17)
"""

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user
from src.core.database.connection import get_db
from src.modules.gdpr.domain.models import (
    ConsentGrantRequest,
    ConsentStatusResponse,
    DataExportRequest,
    ErasureRequest,
)
from src.modules.gdpr.domain.services import GDPRService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gdpr", tags=["GDPR/DSGVO"])


async def get_gdpr_service(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> GDPRService:
    return GDPRService(db)


@router.get("/consent", response_model=list[ConsentStatusResponse])
async def get_consent_status(
    current_user: dict[str, Any] = Depends(get_current_user),  # noqa: B008
    service: GDPRService = Depends(get_gdpr_service),  # noqa: B008
) -> list[ConsentStatusResponse]:
    """
    Get current consent status for all purposes.

    Returns the consent status for each processing purpose,
    including when consent was granted and if it can be withdrawn.
    """
    user_id = UUID(current_user["sub"])
    return await service.get_user_consents(user_id)


@router.put("/consent", response_model=ConsentStatusResponse)
async def update_consent(
    request: Request,
    consent_request: ConsentGrantRequest,
    current_user: dict[str, Any] = Depends(get_current_user),  # noqa: B008
    service: GDPRService = Depends(get_gdpr_service),  # noqa: B008
) -> ConsentStatusResponse:
    """
    Grant or withdraw consent for a specific purpose.

    GDPR Article 7: Consent must be freely given, specific,
    informed, and unambiguous.
    """
    user_id = UUID(current_user["sub"])
    ip_address = request.client.host if request.client else "0.0.0.0"
    user_agent = request.headers.get("user-agent", "")

    record = await service.update_consent(
        user_id, consent_request, ip_address, user_agent
    )

    return ConsentStatusResponse(
        purpose=record.purpose,
        is_granted=record.is_granted,
        granted_at=record.granted_at,
        consent_version=record.consent_version,
        can_withdraw=record.purpose != "essential",
    )


@router.post("/export")
async def export_user_data(
    export_request: DataExportRequest,
    current_user: dict[str, Any] = Depends(get_current_user),  # noqa: B008
    service: GDPRService = Depends(get_gdpr_service),  # noqa: B008
) -> dict[str, Any]:
    """
    Export all user data in machine-readable format.

    GDPR Article 20: Right to data portability.
    Response within 30 days required by law.
    """
    user_id = UUID(current_user["sub"])
    logger.info(f"Data export requested by user {user_id}")

    data = await service.export_user_data(
        user_id, include_audit=export_request.include_audit_trail
    )

    return {
        "status": "success",
        "message": "Data export generated successfully",
        "format": export_request.format,
        "data": data,
    }


@router.post("/erasure")
async def request_erasure(
    erasure_request: ErasureRequest,
    current_user: dict[str, Any] = Depends(get_current_user),  # noqa: B008
    service: GDPRService = Depends(get_gdpr_service),  # noqa: B008
) -> dict[str, Any]:
    """
    Request complete data erasure.

    GDPR Article 17: Right to erasure ('right to be forgotten').
    Must be processed within 30 days.
    """
    if not erasure_request.confirm_deletion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deletion confirmation required",
        )

    user_id = UUID(current_user["sub"])
    logger.warning(f"Erasure request initiated by user {user_id}")

    request = await service.request_erasure(
        user_id, keep_anonymized=erasure_request.keep_anonymized_analytics
    )

    return {
        "status": "pending",
        "request_id": str(request.id),
        "message": "Your data deletion request has been received. "
        "It will be processed within 30 days as required by law.",
        "deadline": request.deadline_at.isoformat(),
    }


@router.get("/processing-info")
async def get_processing_info() -> dict[str, Any]:
    """
    Get information about data processing activities.

    GDPR Article 13/14: Information to be provided.
    """
    return {
        "data_controller": {
            "name": "StellarApply GmbH",
            "address": "Germany",
            "contact": "datenschutz@stellarapply.ai",
        },
        "processing_purposes": [
            {
                "purpose": "essential",
                "description": "Core service functionality",
                "legal_basis": "Contract (Art. 6(1)(b))",
                "retention": "Duration of account",
            },
            {
                "purpose": "ai_profiling",
                "description": "AI-powered job matching and recommendations",
                "legal_basis": "Consent (Art. 6(1)(a))",
                "retention": "Until consent withdrawn",
            },
            {
                "purpose": "analytics",
                "description": "Service improvement analytics",
                "legal_basis": "Legitimate interest (Art. 6(1)(f))",
                "retention": "26 months (anonymized)",
            },
        ],
        "data_recipients": [
            "Google Gemini API (AI processing, EU servers)",
            "Job board APIs (application submission)",
        ],
        "your_rights": [
            "Right to access (Art. 15)",
            "Right to rectification (Art. 16)",
            "Right to erasure (Art. 17)",
            "Right to restrict processing (Art. 18)",
            "Right to data portability (Art. 20)",
            "Right to object (Art. 21)",
        ],
        "supervisory_authority": "Der Bundesbeauftragte für den Datenschutz "
        "und die Informationsfreiheit (BfDI)",
    }
