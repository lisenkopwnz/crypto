from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.domain.entities import IndexPrice, Ticker
from app.domain.exceptions import ExchangeError
from app.worker.celery_app import COLLECT_PRICE_TASK, create_celery_app


@pytest.fixture
def collect_price(monkeypatch) -> AsyncMock:
    mock = AsyncMock()
    monkeypatch.setattr("app.worker.celery_app.collect_price", mock)
    return mock


def test_beat_runs_task_for_each_ticker_every_minute(settings):
    schedule = create_celery_app(settings).conf.beat_schedule

    assert len(schedule) == 2
    assert {entry["args"] for entry in schedule.values()} == {("btc_usd",), ("eth_usd",)}
    for entry in schedule.values():
        assert entry["task"] == COLLECT_PRICE_TASK
        assert entry["schedule"] == 60


def test_task_collects_price(settings, collect_price):
    collect_price.return_value = IndexPrice(Ticker.BTC_USD, Decimal("63083.39"), 1791936000)
    task = create_celery_app(settings).tasks[COLLECT_PRICE_TASK]

    result = task.apply(args=("btc_usd",))

    assert result.get() == "btc_usd 63083.39 1791936000"
    collect_price.assert_awaited_once_with(Ticker.BTC_USD, settings)


def test_task_retries_on_exchange_error(settings, collect_price):
    collect_price.side_effect = ExchangeError("timeout")
    task = create_celery_app(settings).tasks[COLLECT_PRICE_TASK]

    result = task.apply(args=("eth_usd",))

    assert result.failed()
    assert collect_price.await_count == 4
