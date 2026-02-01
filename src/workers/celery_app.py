import os

from celery import Celery

celery_app = Celery(
    "stellapply_workers",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=[
        "src.workers.tasks.job_scraping",
        "src.workers.tasks.auto_apply",
        "src.workers.tasks.embedding_update",
        "src.workers.tasks.security",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
