from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user
from src.core.database.connection import get_db
from src.modules.persona.api.schemas import PersonaResponse, PersonaUpdate
from src.modules.persona.domain.services import PersonaService
from src.modules.persona.infrastructure.repository import SQLAlchemyPersonaRepository

router = APIRouter()


async def get_persona_service(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> PersonaService:
    repository = SQLAlchemyPersonaRepository(db)
    return PersonaService(repository)


@router.get("/me", response_model=PersonaResponse)
async def get_my_persona(
    current_user: dict[str, Any] = Depends(get_current_user),  # noqa: B008
    service: PersonaService = Depends(get_persona_service),  # noqa: B008
) -> PersonaResponse:
    # Keycloak token payload usually has "sub" as the user ID
    user_id_str = current_user.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )

    from uuid import UUID

    user_id = UUID(user_id_str)

    persona = await service.get_persona_by_user_id(user_id)
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found"
        )
    return PersonaResponse.model_validate(persona)


@router.patch("/me", response_model=PersonaResponse)
async def update_my_persona(
    schema: PersonaUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),  # noqa: B008
    service: PersonaService = Depends(get_persona_service),  # noqa: B008
) -> PersonaResponse:
    user_id_str = current_user.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )

    from uuid import UUID

    user_id = UUID(user_id_str)

    persona = await service.update_persona(user_id, schema)
    return PersonaResponse.model_validate(persona)
