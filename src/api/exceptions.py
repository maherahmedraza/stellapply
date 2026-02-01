import logging
import traceback

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception caught: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error", "path": request.url.path},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Sanitize errors to ensure JSON serializability (e.g., removing 'input' if it's bytes)
    errors = []
    for error in exc.errors():
        if "input" in error:
            # Cast input to string if it's not JSON serializable (like bytes)
            if isinstance(error["input"], bytes):
                error["input"] = error["input"].decode(errors="replace")
            elif not isinstance(
                error["input"], (str, int, float, bool, type(None), list, dict)
            ):
                error["input"] = str(error["input"])
        errors.append(error)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors, "path": request.url.path},
    )


async def sqlalchemy_exception_handler(request: Request, _exc: SQLAlchemyError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database Error", "path": request.url.path},
    )
