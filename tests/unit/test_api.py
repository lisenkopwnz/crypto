from collections.abc import AsyncIterator
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock

import httpx
import pytest

from app.api.dependencies import get_price_service
from app.domain.entities import IndexPrice, Ticker
from app.main import create_app
from app.services.price_service import PriceService

ENDPOINTS = ["/api/v1/prices", "/api/v1/prices/latest", "/api/v1/prices/by-date?date=2026-10-14"]


@pytest.fixture
def service() -> AsyncMock:
    return AsyncMock(spec=PriceService)


@pytest.fixture
async def client(settings, service) -> AsyncIterator[httpx.AsyncClient]:
    app = create_app(settings)
    app.dependency_overrides[get_price_service] = lambda: service
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_get_prices(client, service):
    service.get_all.return_value = [
        IndexPrice(Ticker.BTC_USD, Decimal("63083.39"), 1791936060),
        IndexPrice(Ticker.BTC_USD, Decimal("63080.10"), 1791936000),
    ]

    response = await client.get("/api/v1/prices", params={"ticker": "btc_usd"})

    assert response.status_code == 200
    assert response.json() == [
        {"ticker": "btc_usd", "price": 63083.39, "timestamp": 1791936060},
        {"ticker": "btc_usd", "price": 63080.1, "timestamp": 1791936000},
    ]
    service.get_all.assert_awaited_once_with(Ticker.BTC_USD)


async def test_get_prices_empty(client, service):
    service.get_all.return_value = []

    response = await client.get("/api/v1/prices", params={"ticker": "eth_usd"})

    assert response.status_code == 200
    assert response.json() == []


async def test_get_latest_price(client, service):
    service.get_latest.return_value = IndexPrice(Ticker.ETH_USD, Decimal("2450.5"), 1791936060)

    response = await client.get("/api/v1/prices/latest", params={"ticker": "eth_usd"})

    assert response.status_code == 200
    assert response.json() == {"ticker": "eth_usd", "price": 2450.5, "timestamp": 1791936060}
    service.get_latest.assert_awaited_once_with(Ticker.ETH_USD)


async def test_get_latest_price_not_found(client, service):
    service.get_latest.return_value = None

    response = await client.get("/api/v1/prices/latest", params={"ticker": "eth_usd"})

    assert response.status_code == 404


async def test_get_prices_by_date(client, service):
    service.get_by_date.return_value = [
        IndexPrice(Ticker.BTC_USD, Decimal("63000"), 1791979200),
    ]

    response = await client.get(
        "/api/v1/prices/by-date", params={"ticker": "btc_usd", "date": "2026-10-14"}
    )

    assert response.status_code == 200
    assert response.json() == [{"ticker": "btc_usd", "price": 63000.0, "timestamp": 1791979200}]
    service.get_by_date.assert_awaited_once_with(Ticker.BTC_USD, date(2026, 10, 14))


@pytest.mark.parametrize("date_value", [None, "14.10.2026", "2026-13-01"])
async def test_get_prices_by_date_requires_valid_date(client, service, date_value):
    params = {"ticker": "btc_usd"}
    if date_value is not None:
        params["date"] = date_value

    response = await client.get("/api/v1/prices/by-date", params=params)

    assert response.status_code == 422
    service.get_by_date.assert_not_awaited()


@pytest.mark.parametrize("url", ENDPOINTS)
async def test_ticker_is_required(client, url):
    response = await client.get(url)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "ticker"]


@pytest.mark.parametrize("url", ENDPOINTS)
async def test_unknown_ticker(client, url):
    response = await client.get(url, params={"ticker": "doge_usd"})

    assert response.status_code == 422


def test_all_methods_are_get_with_required_ticker(settings):
    paths = create_app(settings).openapi()["paths"]

    assert set(paths) == {"/api/v1/prices", "/api/v1/prices/latest", "/api/v1/prices/by-date"}
    for operations in paths.values():
        assert list(operations) == ["get"]
        ticker = next(p for p in operations["get"]["parameters"] if p["name"] == "ticker")
        assert ticker["in"] == "query"
        assert ticker["required"] is True
