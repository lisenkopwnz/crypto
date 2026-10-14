from decimal import Decimal

import pytest

from app.db.repositories import SqlAlchemyPriceRepository
from app.domain.entities import IndexPrice, Ticker


@pytest.fixture
def repository(db_session) -> SqlAlchemyPriceRepository:
    return SqlAlchemyPriceRepository(db_session)


async def add_prices(repository, *prices: IndexPrice) -> None:
    for price in prices:
        await repository.add(price)


async def test_get_all_returns_only_ticker_prices_newest_first(repository):
    await add_prices(
        repository,
        IndexPrice(Ticker.BTC_USD, Decimal("63000.12345678"), 1791936000),
        IndexPrice(Ticker.ETH_USD, Decimal("2450.5"), 1791936030),
        IndexPrice(Ticker.BTC_USD, Decimal("63100"), 1791936060),
    )

    prices = await repository.get_all(Ticker.BTC_USD)

    assert prices == [
        IndexPrice(Ticker.BTC_USD, Decimal("63100"), 1791936060),
        IndexPrice(Ticker.BTC_USD, Decimal("63000.12345678"), 1791936000),
    ]


async def test_get_latest(repository):
    await add_prices(
        repository,
        IndexPrice(Ticker.ETH_USD, Decimal("2450"), 1791936060),
        IndexPrice(Ticker.ETH_USD, Decimal("2460"), 1791936120),
        IndexPrice(Ticker.BTC_USD, Decimal("63000"), 1791936180),
    )

    assert await repository.get_latest(Ticker.ETH_USD) == IndexPrice(
        Ticker.ETH_USD, Decimal("2460"), 1791936120
    )


async def test_get_latest_without_data(repository):
    assert await repository.get_latest(Ticker.BTC_USD) is None


async def test_get_by_period_includes_start_and_excludes_end(repository):
    await add_prices(
        repository,
        IndexPrice(Ticker.BTC_USD, Decimal("1"), 1791935999),
        IndexPrice(Ticker.BTC_USD, Decimal("2"), 1791936000),
        IndexPrice(Ticker.BTC_USD, Decimal("3"), 1792022399),
        IndexPrice(Ticker.BTC_USD, Decimal("4"), 1792022400),
    )

    prices = await repository.get_by_period(Ticker.BTC_USD, 1791936000, 1792022400)

    assert [price.timestamp for price in prices] == [1792022399, 1791936000]
