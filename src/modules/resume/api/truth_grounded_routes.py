import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.api.middleware.auth import get_current_user
from src.core.database.connection import get_db
from src.core.config import settings
from src.core.ai.gemini_client import GeminiClient

from src.modules.persona.infrastructure.repository import SQLAlchemyPersonaRepository
from src.modules.resume.application.services.enhancement_service import (
    EnhancementService,
    EnhancementRequest,
    VerificationStatus,
)
from src.modules.resume.domain.truth_grounded_schemas import (
    EnhancementSuggestionSchema,
    EnhancementType as LegacyEnhancementType,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["resume-enhancement"])

# --- Schemas ---


class TruthfulEnhanceRequest(BaseModel):
    original_text: str
    section_type: str  # "summary" | "bullet_point" | "description"


class MetricConfirmationRequest(BaseModel):
    enhancement_id: str
    placeholder_values: dict[str, str]


# --- Dependencies ---


async def get_enhancement_service(
    db: AsyncSession = Depends(get_db),
) -> EnhancementService:
    """Dependency for obtaining the EnhancementService."""
    gemini_client = GeminiClient(
        api_key=settings.ai.GEMINI_API_KEY or "DUMMY_KEY",
        default_model=settings.ai.GEMINI_MODEL,
        requests_per_minute=settings.ai.RATE_LIMIT_RPM,
    )
    persona_repo = SQLAlchemyPersonaRepository(db)
    return EnhancementService(gemini_client, persona_repo)


# --- Routes ---


@router.post("/enhance-truthful", response_model=EnhancementSuggestionSchema)
async def enhance_truthfully(
    request: TruthfulEnhanceRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: EnhancementService = Depends(get_enhancement_service),
) -> EnhancementSuggestionSchema:
    """
    Enhance resume text with STRICT truth grounding.
    """
    user_id_str = current_user.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )
    user_id = UUID(user_id_str)

    try:
        service_request = EnhancementRequest(
            content=request.original_text, content_type=request.section_type
        )

        response = await service.enhance(user_id, service_request)

        if not response.success or not response.suggestions:
            # Fallback or return original
            return EnhancementSuggestionSchema(
                original_text=request.original_text,
                enhanced_text=request.original_text,
                enhancement_type=LegacyEnhancementType.REWORD,
                verification_status=VerificationStatus.REJECTED,
                confidence_score=0.0,
                verification_notes=response.error
                or "Unable to ground this enhancement.",
                interview_talking_points=["Use the original content."],
            )

        # Map to Legacy schema for frontend compatibility
        suggestion = response.suggestions[0]
        return EnhancementSuggestionSchema(
            original_text=suggestion.original_text,
            enhanced_text=suggestion.enhanced_text,
            enhancement_type=suggestion.enhancement_type.value,
            verification_status=suggestion.verification_status.value,
            confidence_score=suggestion.confidence_score,
            source_persona_fields=suggestion.source_persona_fields,
            verification_notes=suggestion.verification_notes,
            requires_confirmation=suggestion.requires_confirmation,
            confirmation_prompt=suggestion.confirmation_prompt,
            changes_made=suggestion.changes_made,
            defensibility_score=suggestion.defensibility_score,
            interview_talking_points=suggestion.interview_talking_points,
        )

    except Exception as e:
        logger.error(f"Error in truthful enhancement: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate truthful enhancement: {str(e)}",
        )


@router.post("/confirm-enhancement")
async def confirm_enhancement(
    _request: MetricConfirmationRequest,
    _current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Currently a placeholder - real confirmation logic should be added to service
    """
    return {"final_text": "Final text with confirmed metrics", "status": "verified"}
