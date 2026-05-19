from celery import Celery

REDIS_BROKEN_URL = "redis://localhost:6379/0"
REDIS_RESULT_URL = "redis://localhost:6379/1"

celery_app = Celery(
    "level5_ai_pipeline",
    broker= REDIS_BROKEN_URL,
    backend = REDIS_RESULT_URL
)

celery_app.conf.update(
    task_track_started = True, 
    task_serializer = "json",
    result_serializer = "json",
    accept_content = ["json"], 
    timezone = "Asia/Singapore",
    enable_utc = True,

    worker_prefetch_multiplier = 1,
    task_acks_late = True,

    task_time_limit = 20,
    task_soft_time_limit = 15
)
