from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.domain.entities import IndexPrice, Ticker
from app.domain.interfaces import PriceRepository
from app.services.price_service import PriceService


@pytest.fixture
def repository() -> AsyncMock:
    return AsyncMock(spec=PriceRepository)


async def test_get_all(repository):
    prices = [IndexPrice(Ticker.BTC_USD, Decimal("63000"), 1791936000)]
    repository.get_all.return_value = prices

    assert await PriceService(repository).get_all(Ticker.BTC_USD) == prices
    repository.get_all.assert_awaited_once_with(Ticker.BTC_USD)


async def test_get_latest(repository):
    price = IndexPrice(Ticker.ETH_USD, Decimal("2450"), 1791936000)
    repository.get_latest.return_value = price

    assert await PriceService(repository).get_latest(Ticker.ETH_USD) == price


async def test_get_latest_without_data(repository):
    repository.get_latest.return_value = None

    assert await PriceService(repository).get_latest(Ticker.ETH_USD) is None


async def test_get_by_date_uses_utc_day_bounds(repository):
    repository.get_by_period.return_value = []

    await PriceService(repository).get_by_date(Ticker.BTC_USD, date(2026, 10, 14))

    repository.get_by_period.assert_awaited_once_with(Ticker.BTC_USD, 1791936000, 1792022400)
