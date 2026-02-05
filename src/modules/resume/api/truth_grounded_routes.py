from typing import Any, List, Optional
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.api.middleware.auth import get_current_user
from src.core.database.connection import get_db
from src.core.config import settings
from src.core.ai.gemini_client import GeminiClient

from src.modules.persona.infrastructure.repository import SQLAlchemyPersonaRepository
from src.modules.persona.domain.services import PersonaService
from src.modules.resume.ai.truthful_enhancer import (
    TruthfulResumeEnhancer,
    TruthfulEnhancement,
)
from src.modules.resume.domain.enhancement_audit import EnhancementType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/enhance", tags=["resume-enhancement"])

# --- Schemas ---


class EnhancementRequest(BaseModel):
    original_content: str
    target_role: Optional[str] = None
    requirements: List[str] = []


class EnhancementResponse(BaseModel):
    enhancement: TruthfulEnhancement


# --- Dependencies ---


async def get_truthful_enhancer(
    db: AsyncSession = Depends(get_db),
) -> TruthfulResumeEnhancer:
    """Dependency for obtaining the TruthfulResumeEnhancer."""
    gemini_client = GeminiClient(
        api_key=settings.ai.GEMINI_API_KEY or "DUMMY_KEY",
        default_model=settings.ai.GEMINI_MODEL,
        requests_per_minute=settings.ai.RATE_LIMIT_RPM,
    )
    persona_repo = SQLAlchemyPersonaRepository(db)
    persona_service = PersonaService(persona_repo)
    return TruthfulResumeEnhancer(gemini_client, persona_service)


# --- Routes ---


@router.post("/truthful", response_model=EnhancementResponse)
async def enhance_content_truthfully(
    request: EnhancementRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    enhancer: TruthfulResumeEnhancer = Depends(get_truthful_enhancer),
) -> EnhancementResponse:
    """
    Generate a truthful enhancement for a resume bullet point.
    Strictly grounded in the user's verified Persona data.
    """
    user_id_str = current_user.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )
    user_id = UUID(user_id_str)

    try:
        context = {
            "target_role": request.target_role,
            "requirements": request.requirements,
        }

        enhancement = await enhancer.enhance_bullet_point(
            bullet=request.original_content, context=context, user_id=user_id
        )

        return EnhancementResponse(enhancement=enhancement)
    except Exception as e:
        logger.error(f"Error in truthful enhancement: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate enhancement: {str(e)}",
        )
