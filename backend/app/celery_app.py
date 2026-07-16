"""
Celery 应用配置

Usage:
  # 启动 worker
  celery -A app.celery_app worker --loglevel=info -P solo

  # 启动 beat（定时任务调度器）
  celery -A app.celery_app beat --loglevel=info
"""

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "eduagent",
    broker=settings.redis_url or "redis://127.0.0.1:6379/0",
    backend=settings.redis_url or "redis://127.0.0.1:6379/0",
    include=[
        "app.tasks.embedding_tasks",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=270,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)
