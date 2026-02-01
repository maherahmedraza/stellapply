from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user
from src.core.database.connection import get_db
from src.modules.identity.api.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from src.modules.identity.domain.services import AuthService, RegistrationService
from src.modules.identity.infrastructure.repository import SQLAlchemyUserRepository

router = APIRouter()


async def get_auth_service() -> AuthService:
    return AuthService()


async def get_registration_service(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> RegistrationService:
    repository = SQLAlchemyUserRepository(db)
    return RegistrationService(repository)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> TokenResponse:
    try:
        return service.login(request.username, request.password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        ) from e


@router.get("/me", response_model=UserResponse)
async def get_me(
    _current_user: Any = Depends(get_current_user),  # noqa: B008
    _db: AsyncSession = Depends(get_db),  # noqa: B008
) -> UserResponse:
    # This would fetch user from DB based on Keycloak sub/id
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet"
    )


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    schema: UserCreate,
    service: RegistrationService = Depends(get_registration_service),  # noqa: B008
) -> UserResponse:
    try:
        user = await service.register_user(schema)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        import traceback
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Registration error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {str(e)}",
        ) from e
