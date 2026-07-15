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
        "app.tasks.resource_tasks",
        "app.tasks.statistics_tasks",
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

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "daily-cost-summary": {
        "task": "app.tasks.statistics_tasks.generate_daily_summary",
        "schedule": 86400.0,  # every 24 hours
    },
    "cleanup-old-cache": {
        "task": "app.tasks.statistics_tasks.cleanup_cache",
        "schedule": 3600.0,  # every hour
    },
}
