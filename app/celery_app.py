import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

app = Celery(
    'tasks',
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=["app.api.v1.tasks"]
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        'fetch-bitcoin-price-every-minute': {
            'task': 'app.api.v1.tasks.fetch_currency_price',
            'schedule': crontab(minute='*'),
        },
    }
)