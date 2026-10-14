from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.domain.entities import IndexPrice, Ticker
from app.domain.exceptions import ExchangeError
from app.domain.interfaces import ExchangeClient, PriceRepository
from app.services.price_collector import PriceCollector


@pytest.fixture
def client() -> AsyncMock:
    return AsyncMock(spec=ExchangeClient)


@pytest.fixture
def repository() -> AsyncMock:
    return AsyncMock(spec=PriceRepository)


async def test_collect_saves_price_with_current_time(client, repository, monkeypatch):
    client.get_index_price.return_value = Decimal("63083.39")
    monkeypatch.setattr("app.services.price_collector.time.time", lambda: 1791936000.75)

    price = await PriceCollector(client, repository).collect(Ticker.BTC_USD)

    expected = IndexPrice(Ticker.BTC_USD, Decimal("63083.39"), 1791936000)
    assert price == expected
    client.get_index_price.assert_awaited_once_with(Ticker.BTC_USD)
    repository.add.assert_awaited_once_with(expected)


async def test_collect_does_not_save_when_exchange_fails(client, repository):
    client.get_index_price.side_effect = ExchangeError("timeout")

    with pytest.raises(ExchangeError):
        await PriceCollector(client, repository).collect(Ticker.ETH_USD)

    repository.add.assert_not_awaited()
