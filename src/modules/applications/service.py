import uuid
from datetime import UTC, datetime, timedelta
from typing import Optional

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.security.audit_log import AuditAction, AuditLogger
from src.modules.applications.models import (
    Application,
    ApplicationEvent,
    ApplicationStatus,
)
from src.modules.applications.schemas import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationStats,
)


class ApplicationService:
    """
    Service layer for managing job applications and their lifecycle.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_logger = AuditLogger(db)

    async def create_application(
        self, user_id: uuid.UUID, data: ApplicationCreate
    ) -> Application:
        """
        Create a new application and record the initial event.
        """
        application = Application(
            user_id=user_id, **data.model_dump(exclude_unset=True)
        )

        # Ensure applied_at is set if status is 'applied' and not provided
        if (
            application.status == ApplicationStatus.APPLIED
            and not application.applied_at
        ):
            application.applied_at = datetime.now(UTC)

        self.db.add(application)
        await self.db.flush()  # Get application ID

        # Create initial event
        event = ApplicationEvent(
            application_id=application.id,
            from_status=None,
            to_status=application.status,
            notes="Initial application creation",
            created_by=user_id,
        )
        self.db.add(event)

        # Audit log
        await self.audit_logger.log_event(
            action=AuditAction.CREATE,
            resource_type="application",
            resource_id=application.id,
            user_id=str(user_id),
            new_value=data.model_dump(mode="json"),
        )

        await self.db.commit()
        await self.db.refresh(application)
        return application

    async def get_application(
        self, user_id: uuid.UUID, application_id: uuid.UUID
    ) -> Application | None:
        """
        Get a specific application for a user with its event history.
        """
        stmt = (
            select(Application)
            .filter(
                and_(Application.id == application_id, Application.user_id == user_id)
            )
            .options(selectinload(Application.events))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_applications(
        self,
        user_id: uuid.UUID,
        status: ApplicationStatus | None = None,
        company: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Application], int]:
        """
        List applications for a user with filtering, sorting, and pagination.
        """
        stmt = select(Application).filter(Application.user_id == user_id)

        if status:
            stmt = stmt.filter(Application.status == status)
        if company:
            stmt = stmt.filter(Application.company_name.ilike(f"%{company}%"))
        if date_from:
            stmt = stmt.filter(Application.created_at >= date_from)
        if date_to:
            stmt = stmt.filter(Application.created_at <= date_to)

        # Sorting
        sort_attr = getattr(Application, sort_by, Application.created_at)
        if order == "desc":
            stmt = stmt.order_by(desc(sort_attr))
        else:
            stmt = stmt.order_by(sort_attr)

        # Total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self.db.execute(count_stmt)
        total_count = total.scalar() or 0

        # Pagination
        stmt = stmt.offset((page - 1) * per_page).limit(per_page)

        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total_count

    async def update_application(
        self, user_id: uuid.UUID, application_id: uuid.UUID, data: ApplicationUpdate
    ) -> Application | None:
        """
        Update an application. If status changes, record a new event.
        """
        application = await self.get_application(user_id, application_id)
        if not application:
            return None

        old_data = {
            "status": application.status,
            "company_name": application.company_name,
            "job_title": application.job_title,
        }

        update_dict = data.model_dump(exclude_unset=True)

        if "status" in update_dict and update_dict["status"] != application.status:
            # Status change detected
            event = ApplicationEvent(
                application_id=application.id,
                from_status=application.status,
                to_status=update_dict["status"],
                notes=update_dict.get("notes", "Status updated"),
                created_by=user_id,
            )
            self.db.add(event)

            # If moving to applied, set applied_at if not already set
            if (
                update_dict["status"] == ApplicationStatus.APPLIED
                and not application.applied_at
            ):
                application.applied_at = datetime.now(UTC)

        # Update fields
        for key, value in update_dict.items():
            setattr(application, key, value)

        # Audit log
        await self.audit_logger.log_event(
            action=AuditAction.UPDATE,
            resource_type="application",
            resource_id=application.id,
            user_id=str(user_id),
            old_value=old_data,
            new_value=update_dict,
        )

        await self.db.commit()
        await self.db.refresh(application)
        return application

    async def delete_application(
        self, user_id: uuid.UUID, application_id: uuid.UUID
    ) -> bool:
        """
        Soft delete an application.
        """
        application = await self.get_application(user_id, application_id)
        if not application:
            return False

        application.soft_delete(user_id)

        # Audit log
        await self.audit_logger.log_event(
            action=AuditAction.DELETE,
            resource_type="application",
            resource_id=application.id,
            user_id=str(user_id),
        )

        await self.db.commit()
        return True

    async def bulk_update_status(
        self,
        user_id: uuid.UUID,
        application_ids: list[uuid.UUID],
        new_status: ApplicationStatus,
    ) -> int:
        """
        Update status for multiple applications at once.
        """
        # Fetch current statuses to create events
        stmt = select(Application).filter(
            and_(Application.id.in_(application_ids), Application.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        apps = result.scalars().all()

        count = 0
        for app in apps:
            if app.status != new_status:
                event = ApplicationEvent(
                    application_id=app.id,
                    from_status=app.status,
                    to_status=new_status,
                    notes="Bulk status update",
                    created_by=user_id,
                )
                self.db.add(event)
                app.status = new_status
                count += 1

        if count > 0:
            await self.audit_logger.log_event(
                action=AuditAction.UPDATE,
                resource_type="application_bulk",
                user_id=str(user_id),
                metadata={
                    "count": count,
                    "new_status": new_status,
                    "ids": [str(i) for i in application_ids],
                },
            )
            await self.db.commit()

        return count

    async def get_stats(self, user_id: uuid.UUID) -> ApplicationStats:
        """
        Calculate application metrics and statistics.
        """
        # Total counts by status
        stmt = (
            select(Application.status, func.count())
            .filter(Application.user_id == user_id)
            .group_by(Application.status)
        )
        result = await self.db.execute(stmt)
        by_status = {status.value: count for status, count in result.all()}
        total = sum(by_status.values())

        # Weekly applied
        one_week_ago = datetime.now(UTC) - timedelta(days=7)
        weekly_stmt = select(func.count()).filter(
            and_(Application.user_id == user_id, Application.applied_at >= one_week_ago)
        )
        weekly_applied = (await self.db.execute(weekly_stmt)).scalar() or 0

        # Response rate (Screening or further / Total Applied)
        responded_statuses = [
            ApplicationStatus.SCREENING,
            ApplicationStatus.INTERVIEW,
            ApplicationStatus.OFFER,
            ApplicationStatus.REJECTED,
            ApplicationStatus.ACCEPTED,
        ]
        responded_count = sum(by_status.get(s, 0) for s in responded_statuses)

        response_rate = (responded_count / total * 100) if total > 0 else 0.0

        # Avg time to response (Placeholder)
        avg_time = 0.0

        return ApplicationStats(
            total=total,
            by_status=by_status,
            weekly_applied=weekly_applied,
            response_rate=round(response_rate, 2),
            avg_time_to_response_days=avg_time,
        )

    async def get_follow_ups(self, user_id: uuid.UUID) -> list[Application]:
        """
        Get applications requiring follow-up within next 3 days.
        """
        three_days_from_now = datetime.now(UTC) + timedelta(days=3)
        stmt = (
            select(Application)
            .filter(
                and_(
                    Application.user_id == user_id,
                    Application.next_follow_up <= three_days_from_now,
                    Application.status.in_(
                        [
                            ApplicationStatus.APPLIED,
                            ApplicationStatus.SCREENING,
                            ApplicationStatus.INTERVIEW,
                        ]
                    ),
                )
            )
            .order_by(Application.next_follow_up)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
