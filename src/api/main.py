from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from src.core.config import settings
from src.core.security.audit_log import AuditMiddleware
from src.api.exceptions import (
    global_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
)

# Import your modules' routers here as they are implemented
from src.modules.identity.api.routes import router as identity_router
from src.modules.job_search.api.routes import router as job_router
from src.modules.persona.api.routes import router as persona_router
from src.modules.resume.api.routes import router as resume_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Python-based Modular Monolith Backend for Stellapply",
    version="0.1.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit Logging Middleware
app.add_middleware(AuditMiddleware)

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "architecture": "modular_monolith"}


# Include Routers
app.include_router(identity_router, prefix="/api/v1/auth", tags=["Identity"])
app.include_router(persona_router, prefix="/api/v1/persona", tags=["Persona"])
app.include_router(resume_router, prefix="/api/v1/resume", tags=["Resume"])
app.include_router(job_router, prefix="/api/v1/jobs", tags=["Job Search"])
