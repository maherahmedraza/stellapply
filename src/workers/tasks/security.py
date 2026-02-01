import asyncio
import logging

from src.core.database.connection import AsyncSessionLocal
from src.core.security.audit_log import AuditLogger
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
def cleanup_old_logs(_days: int = 365) -> bool:
    """Placeholder for log retention cleanup if needed."""
    return True
