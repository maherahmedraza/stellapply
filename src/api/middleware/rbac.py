"""
Reusable RBAC (Role-Based Access Control) dependencies for FastAPI.

Usage:
    @router.get("/admin-only", dependencies=[Depends(require_admin)])
    async def admin_endpoint():
        ...

    @router.get("/active-only", dependencies=[Depends(require_active)])
    async def active_endpoint():
        ...
"""

from typing import Any

from fastapi import Depends, HTTPException, status

from src.api.middleware.auth import get_current_user


def require_role(role: str):
    """Create a dependency that requires a specific role."""

    async def _check_role(
        current_user: dict[str, Any] = Depends(get_current_user),  # noqa: B008
    ) -> dict[str, Any]:
        roles = current_user.get("realm_access", {}).get("roles", [])
        if role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required",
            )
        return current_user

    return _check_role


# Pre-built role dependencies
require_admin = require_role("admin")


async def require_active(
    current_user: dict[str, Any] = Depends(get_current_user),  # noqa: B008
) -> dict[str, Any]:
    """Ensure the user's account is not suspended or banned."""
    user_status = current_user.get("status", "active")
    if user_status in ("suspended", "banned"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user_status}",
        )
    return current_user
