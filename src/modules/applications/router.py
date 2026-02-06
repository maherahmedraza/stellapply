import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user
from src.core.database.connection import get_db
from src.modules.applications.models import ApplicationStatus
from src.modules.applications.schemas import (
    ApplicationCreate,
    ApplicationEventResponse,
    ApplicationListResponse,
    ApplicationResponse,
    ApplicationStats,
    ApplicationUpdate,
    BulkUpdateStatus,
)
from src.modules.applications.service import ApplicationService

router = APIRouter()


async def get_application_service(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> ApplicationService:
    return ApplicationService(db)


@router.post(
    "/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED
)
async def create_application(
    data: ApplicationCreate,
    current_user: dict = Depends(get_current_user),  # noqa: B008
    service: ApplicationService = Depends(get_application_service),  # noqa: B008
) -> ApplicationResponse:
    """
    Track a new job application.
    """
    user_id = uuid.UUID(current_user["sub"])
    return await service.create_application(user_id, data)


@router.get("/", response_model=ApplicationListResponse)
async def list_applications(
    status: ApplicationStatus | None = None,
    company: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: dict = Depends(get_current_user),  # noqa: B008
    service: ApplicationService = Depends(get_application_service),  # noqa: B008
) -> ApplicationListResponse:
    """
    List user's applications with filtering and pagination.
    """
    user_id = uuid.UUID(current_user["sub"])
    items, total = await service.list_applications(
        user_id=user_id,
        status=status,
        company=company,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order=order,
    )
    return ApplicationListResponse(
        items=items, total=total, page=page, per_page=per_page
    )


@router.get("/stats", response_model=ApplicationStats)
async def get_application_stats(
    current_user: dict = Depends(get_current_user),  # noqa: B008
    service: ApplicationService = Depends(get_application_service),  # noqa: B008
) -> ApplicationStats:
    """
    Get high-level statistics of the application funnel.
    """
    user_id = uuid.UUID(current_user["sub"])
    return await service.get_stats(user_id)


@router.get("/follow-ups", response_model=list[ApplicationResponse])
async def get_upcoming_follow_ups(
    current_user: dict = Depends(get_current_user),  # noqa: B008
    service: ApplicationService = Depends(get_application_service),  # noqa: B008
) -> list[ApplicationResponse]:
    """
    Get applications that require follow-up within the next 3 days.
    """
    user_id = uuid.UUID(current_user["sub"])
    return await service.get_follow_ups(user_id)


@router.get("/{id}", response_model=ApplicationResponse)
async def get_application_details(
    id: uuid.UUID,
    current_user: dict = Depends(get_current_user),  # noqa: B008
    service: ApplicationService = Depends(get_application_service),  # noqa: B008
) -> ApplicationResponse:
    """
    Get detailed information about a specific application.
    """
    user_id = uuid.UUID(current_user["sub"])
    application = await service.get_application(user_id, id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )
    return application


@router.patch("/{id}", response_model=ApplicationResponse)
async def update_application(
    id: uuid.UUID,
    data: ApplicationUpdate,
    current_user: dict = Depends(get_current_user),  # noqa: B008
    service: ApplicationService = Depends(get_application_service),  # noqa: B008
) -> ApplicationResponse:
    """
    Update application details or status.
    """
    user_id = uuid.UUID(current_user["sub"])
    application = await service.update_application(user_id, id, data)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )
    return application


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    id: uuid.UUID,
    current_user: dict = Depends(get_current_user),  # noqa: B008
    service: ApplicationService = Depends(get_application_service),  # noqa: B008
) -> None:
    """
    Remove an application from tracking.
    """
    user_id = uuid.UUID(current_user["sub"])
    success = await service.delete_application(user_id, id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )


@router.get("/{id}/events", response_model=list[ApplicationEventResponse])
async def get_application_history(
    id: uuid.UUID,
    current_user: dict = Depends(get_current_user),  # noqa: B008
    service: ApplicationService = Depends(get_application_service),  # noqa: B008
) -> list[ApplicationEventResponse]:
    """
    Get the status transition history for an application.
    """
    user_id = uuid.UUID(current_user["sub"])
    application = await service.get_application(user_id, id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )
    return application.events


@router.post("/bulk-status", status_code=status.HTTP_200_OK)
async def bulk_update_applications_status(
    data: BulkUpdateStatus,
    current_user: dict = Depends(get_current_user),  # noqa: B008
    service: ApplicationService = Depends(get_application_service),  # noqa: B008
) -> dict:
    """
    Update status for multiple applications at once.
    """
    user_id = uuid.UUID(current_user["sub"])
    count = await service.bulk_update_status(
        user_id, data.application_ids, data.new_status
    )
    return {"updated": count}
