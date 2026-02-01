import asyncio
import json
import logging
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import delete, select, text

from src.core.database.connection import AsyncSessionLocal
from src.core.infrastructure.storage import storage_provider
from src.core.security.audit_log import AuditEvent, AuditLogger
from src.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="verify_audit_chain_integrity")  # type: ignore[untyped-decorator]
def verify_audit_chain_integrity() -> bool:
    """
    Celery task to verify the integrity of the audit log hash chain.
    Runs periodically to detect any tampering.
    """

    async def _verify() -> bool:
        logger.info("Starting audit chain integrity verification...")
        async with AsyncSessionLocal() as db:
            try:
                logger_service = AuditLogger(db)
                is_intact = await logger_service.verify_chain_integrity()

                if is_intact:
                    logger.info("Audit chain integrity verified: INTACT")
                else:
                    logger.critical("AUDIT CHAIN CORRUPTION DETECTED!")
                    # In production, this should trigger high-priority alerts

                return bool(is_intact)
            except Exception as e:
                logger.error(f"Audit integrity verification failed: {str(e)}")
                import traceback

                logger.error(traceback.format_exc())
                return False

    return asyncio.run(_verify())


@celery_app.task(name="cleanup_old_logs")  # type: ignore[untyped-decorator]
def cleanup_old_logs(days: int = 90) -> bool:
    """
    Archive logs older than X days to cold storage and cleanup DB.
    Complies with 90-day hot retention policy.
    """

    async def _cleanup() -> bool:
        cutoff = datetime.now(UTC) - timedelta(days=days)
        logger.info(f"Starting audit log cleanup (cutoff: {cutoff.isoformat()})...")

        async with AsyncSessionLocal() as db:
            try:
                # 1. Fetch old logs
                stmt = select(AuditEvent).filter(AuditEvent.timestamp < cutoff)
                result = await db.execute(stmt)
                old_events = result.scalars().all()

                if not old_events:
                    logger.info("No old logs to archive.")
                    return True

                # 2. Archive to cold storage (JSON format)
                archive_data = []
                for event in old_events:
                    archive_data.append(
                        {
                            "id": str(event.id),
                            "timestamp": event.timestamp.isoformat(),
                            "user_id": event.user_id,
                            "action": event.action,
                            "resource_type": event.resource_type,
                            "resource_id": str(event.resource_id)
                            if event.resource_id
                            else None,
                            "request_id": event.request_id,
                            "ip_address_encrypted": event.ip_address_encrypted,
                            "user_agent_hash": event.user_agent_hash,
                            "old_value_encrypted": event.old_value_encrypted,
                            "new_value_encrypted": event.new_value_encrypted,
                            "metadata_json": event.metadata_json,
                            "hash_chain": event.hash_chain,
                        }
                    )

                file_content = json.dumps(archive_data, indent=2).encode()
                filename = (
                    f"audit_archive_{cutoff.strftime('%Y%m%d')}_{uuid4().hex[:8]}.json"
                )

                success = storage_provider.upload_file(
                    bucket_name="audit-archive",
                    object_name=filename,
                    data=file_content,
                    content_type="application/json",
                )

                if not success:
                    logger.error(
                        "Failed to upload archive to cold storage. Aborting cleanup."
                    )
                    return False

                logger.info(
                    f"Successfully archived {len(old_events)} logs to {filename}"
                )

                # 3. Securely delete from database by temporarily bypassing trigger
                await db.execute(
                    text(
                        "ALTER TABLE audit_events "
                        "DISABLE TRIGGER enforce_append_only_audit_log"
                    )
                )

                delete_stmt = delete(AuditEvent).filter(AuditEvent.timestamp < cutoff)
                await db.execute(delete_stmt)

                await db.execute(
                    text(
                        "ALTER TABLE audit_events "
                        "ENABLE TRIGGER enforce_append_only_audit_log"
                    )
                )

                await db.commit()
                logger.info(
                    f"Successfully removed {len(old_events)} logs from database."
                )
                return True

            except Exception as e:
                logger.error(f"Audit log cleanup failed: {str(e)}")
                await db.rollback()
                # Ensure trigger is re-enabled even on failure
                try:
                    await db.execute(
                        text(
                            "ALTER TABLE audit_events "
                            "ENABLE TRIGGER enforce_append_only_audit_log"
                        )
                    )
                    await db.commit()
                except Exception:
                    pass
                return False

    return asyncio.run(_cleanup())
