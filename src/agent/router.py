from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.database.connection import get_db
from src.agent.models.pipeline import PipelineConfig
from src.agent.models.entities import AgentSession
from src.agent.tasks.pipeline import run_agent_pipeline

router = APIRouter(prefix="/agent/sessions", tags=["Agent Sessions"])


@router.post("/", response_model=dict)
async def create_session(
    config: PipelineConfig,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(get_current_user) # Assuming auth
):
    # Mock user for now
    user_id = UUID("00000000-0000-0000-0000-000000000000")

    session = AgentSession(user_id=user_id, config=config.model_dump(), status="queued")
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Trigger Celery Task
    background_tasks.add_task(run_agent_pipeline, str(session.id), str(user_id))

    return {"session_id": session.id, "status": "queued"}


@router.get("/{session_id}", response_model=dict)
async def get_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentSession).where(AgentSession.id == session_id))
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
