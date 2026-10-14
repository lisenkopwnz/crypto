from collections.abc import AsyncIterator
from decimal import Decimal

import httpx
import pytest

from app.api.dependencies import get_session
from app.db.repositories import SqlAlchemyPriceRepository
from app.domain.entities import IndexPrice, Ticker
from app.main import create_app


@pytest.fixture
async def client(settings, db_session) -> AsyncIterator[httpx.AsyncClient]:
    repository = SqlAlchemyPriceRepository(db_session)
    for price in [
        IndexPrice(Ticker.BTC_USD, Decimal("62000"), 1791935999),
        IndexPrice(Ticker.BTC_USD, Decimal("63000"), 1791936000),
        IndexPrice(Ticker.BTC_USD, Decimal("63500.5"), 1791979200),
        IndexPrice(Ticker.ETH_USD, Decimal("2450"), 1791979200),
        IndexPrice(Ticker.BTC_USD, Decimal("64000"), 1792022400),
    ]:
        await repository.add(price)

    app = create_app(settings)
    app.dependency_overrides[get_session] = lambda: db_session
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_get_all_prices(client):
    response = await client.get("/api/v1/prices", params={"ticker": "btc_usd"})

    assert response.status_code == 200
    assert [item["timestamp"] for item in response.json()] == [
        1792022400,
        1791979200,
        1791936000,
        1791935999,
    ]


async def test_get_latest_price(client):
    response = await client.get("/api/v1/prices/latest", params={"ticker": "btc_usd"})

    assert response.status_code == 200
    assert response.json() == {"ticker": "btc_usd", "price": 64000.0, "timestamp": 1792022400}


async def test_get_prices_by_date(client):
    response = await client.get(
        "/api/v1/prices/by-date", params={"ticker": "btc_usd", "date": "2026-10-14"}
    )

    assert response.status_code == 200
    assert response.json() == [
        {"ticker": "btc_usd", "price": 63500.5, "timestamp": 1791979200},
        {"ticker": "btc_usd", "price": 63000.0, "timestamp": 1791936000},
    ]
