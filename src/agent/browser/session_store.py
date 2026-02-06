import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import structlog
from playwright.async_api import BrowserContext
from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, select, text
from sqlalchemy.dialects.postgresql import JSONB

from src.core.database.base_model import Base
from src.core.database.connection import get_db_context
from src.core.security.encryption import EncryptedString

logger = structlog.get_logger(__name__)


# DB Model for Session Persistence
class PortalSession(Base):
    __tablename__ = "portal_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    domain = Column(String, nullable=False, index=True)

    # Encrypted fields
    cookies = Column(EncryptedString, nullable=True)  # Storing as encrypted JSON string
    local_storage = Column(EncryptedString, nullable=True)

    is_logged_in = Column(Boolean, default=False)
    last_used = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)


class SessionStore:
    """
    Persists browser sessions (cookies + localStorage).
    """

    async def save_session(self, user_id: str, domain: str, context: BrowserContext):
        """
        Extract cookies/storage from context and save to DB.
        """
        try:
            cookies = await context.cookies()
            # Local storage extraction requires script execution
            # This works if we have a page open, but context level storage state is better
            storage_state = await context.storage_state()

            # storage_state contains { cookies: [], origins: [ { origin: '...', localStorage: [] } ] }

            # We separate them
            cookies_json = json.dumps(storage_state.get("cookies", []))
            # Store full origins as 'local_storage' blob for simplicity
            storage_json = json.dumps(storage_state.get("origins", []))

            async with get_db_context() as session:
                # Upsert logic
                result = await session.execute(
                    select(PortalSession).where(
                        PortalSession.user_id == user_id, PortalSession.domain == domain
                    )
                )
                db_session = result.scalars().first()

                if not db_session:
                    db_session = PortalSession(user_id=user_id, domain=domain)
                    session.add(db_session)

                db_session.cookies = cookies_json
                db_session.local_storage = storage_json
                db_session.last_used = datetime.utcnow()
                db_session.is_logged_in = (
                    True  # Assumption: if we save, we might be logged in
                )

                await session.commit()

            logger.info("Session saved", user_id=user_id, domain=domain)

        except Exception as e:
            logger.error("Save session failed", error=str(e))

    async def restore_session(
        self, user_id: str, domain: str, context: BrowserContext
    ) -> bool:
        """
        Load cookies/storage into context. Returns True if restored.
        """
        try:
            async with get_db_context() as session:
                result = await session.execute(
                    select(PortalSession).where(
                        PortalSession.user_id == user_id, PortalSession.domain == domain
                    )
                )
                db_session = result.scalars().first()

            if not db_session or not db_session.cookies:
                return False

            # Construct storage state object
            state = {
                "cookies": json.loads(db_session.cookies),
                "origins": json.loads(db_session.local_storage)
                if db_session.local_storage
                else [],
            }

            # Apply to context. context.add_cookies is simpler but storage_state is comprehensive
            # Unfortunately context.connection won't allow full set_state easily on active context
            # We usually pass storage_state at context CREATION time.
            # But if context exists, we use add_cookies and inject localStorage via script.

            await context.add_cookies(state["cookies"])

            # Note: LocalStorage injection typically needs a Page.
            # We'll skip complex LS injection on already-open context for MVP,
            # or rely on `new_context(storage_state=...)` in Pool.
            # Since SessionStore is usually called BY the Pool when creating context, this is fine.

            return True

        except Exception as e:
            logger.error("Restore session failed", error=str(e))
            return False

    async def get_storage_state(self, user_id: str, domain: str) -> Optional[Dict]:
        """Helper to get state dict for context creation."""
        async with get_db_context() as session:
            result = await session.execute(
                select(PortalSession).where(
                    PortalSession.user_id == user_id, PortalSession.domain == domain
                )
            )
            db_session = result.scalars().first()

        if not db_session or not db_session.cookies:
            return None

        return {
            "cookies": json.loads(db_session.cookies),
            "origins": json.loads(db_session.local_storage)
            if db_session.local_storage
            else [],
        }
