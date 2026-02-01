from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings

# Import your modules' routers here as they are implemented
from src.modules.identity.api.routes import router as identity_router
from src.modules.persona.api.routes import router as persona_router

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


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "architecture": "modular_monolith"}


# Include Routers
app.include_router(identity_router, prefix="/api/v1/auth", tags=["Identity"])
app.include_router(persona_router, prefix="/api/v1/persona", tags=["Persona"])
