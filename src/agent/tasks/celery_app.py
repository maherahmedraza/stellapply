import os
from celery import Celery

# Get Redis URL from environment or default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "stellapply_agent",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "src.agent.tasks.discovery",
        "src.agent.tasks.application",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "src.agent.tasks.discovery.*": {"queue": "discovery"},
        "src.agent.tasks.application.*": {"queue": "application"},
    },
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # Prevent one worker from grabbing too many long tasks
)

if __name__ == "__main__":
    celery_app.start()
