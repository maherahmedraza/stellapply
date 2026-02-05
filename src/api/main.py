from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from src.api.exceptions import (
    global_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
)
from src.core.config import settings
from src.core.security.audit_log import AuditMiddleware

# Include Routers
# Import all models to ensure they are registered with the declarative base
import src.core.database.all_models  # noqa
from src.modules.gdpr.api.routes import router as gdpr_router
from src.modules.identity.api.routes import router as identity_router
from src.modules.identity.api.settings_routes import router as settings_router
from src.modules.billing.api.routes import router as billing_router
from src.modules.job_search.api.routes import router as job_router
from src.modules.persona.api.routes import router as persona_router
from src.modules.resume.api.routes import router as resume_router
from src.modules.resume.api.truth_grounded_routes import (
    router as truth_grounded_resume_router,
)
from src.agent.api import router as agent_router
from src.agent.orchestrator import orchestrator
from src.modules.applications.router import router as application_router

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


@app.on_event("startup")
async def startup_event():
    await orchestrator.initialize()


@app.on_event("shutdown")
async def shutdown_event():
    await orchestrator.shutdown()


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "architecture": "modular_monolith"}


# Include Routers
app.include_router(identity_router, prefix="/api/v1/auth", tags=["Identity"])
app.include_router(settings_router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(billing_router, prefix="/api/v1/billing", tags=["Billing"])
app.include_router(persona_router, prefix="/api/v1/persona", tags=["Persona"])
app.include_router(resume_router, prefix="/api/v1/resume", tags=["Resume"])
app.include_router(
    truth_grounded_resume_router, prefix="/api/v1/resume", tags=["Resume Enhancement"]
)
app.include_router(
    application_router, prefix="/api/v1/applications", tags=["Applications"]
)
app.include_router(job_router, prefix="/api/v1/jobs", tags=["Job Search"])
app.include_router(gdpr_router, prefix="/api/v1/gdpr", tags=["GDPR/DSGVO"])
app.include_router(agent_router, prefix="/api/v1/agent", tags=["Autonomous Agent"])
