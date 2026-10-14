import asyncio

from celery import Celery

from app.config import Settings
from app.domain.entities import Ticker
from app.domain.exceptions import ExchangeError
from app.worker.jobs import collect_price

COLLECT_PRICE_TASK = "collect_price"


def create_celery_app(settings: Settings | None = None) -> Celery:
    settings = settings or Settings()

    celery_app = Celery("test_crypto", broker=settings.broker_url)
    celery_app.conf.update(
        timezone="UTC",
        task_ignore_result=True,
        broker_connection_retry_on_startup=True,
        beat_schedule={
            f"collect-{ticker}": {
                "task": COLLECT_PRICE_TASK,
                "schedule": settings.collect_interval,
                "args": (ticker.value,),
                "options": {"expires": settings.collect_interval},
            }
            for ticker in Ticker
        },
    )

    @celery_app.task(
        name=COLLECT_PRICE_TASK,
        autoretry_for=(ExchangeError,),
        max_retries=3,
        retry_backoff=5,
    )
    def collect_price_task(ticker: str) -> str:
        price = asyncio.run(collect_price(Ticker(ticker), settings))
        return f"{price.ticker} {price.price} {price.timestamp}"

    return celery_app
