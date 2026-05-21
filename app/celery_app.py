import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
API_URL = os.getenv("API_URL", "http://api:8000")
PRIME_CACHE_INTERVAL = int(os.getenv("PRIME_CACHE_INTERVAL", "600"))

celery = Celery(
    "wegrow",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "prime-endpoints-periodic": {
            "task": "app.tasks.prime_endpoints",
            "schedule": PRIME_CACHE_INTERVAL,
            "args": ([],),
        },
    },
)

celery.autodiscover_tasks(["app.tasks"])
