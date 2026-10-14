import asyncio
from decimal import Decimal

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from app.clients.deribit import DeribitClient
from app.domain.entities import Ticker
from app.domain.exceptions import ExchangeError


@pytest.fixture
async def make_client():
    servers = []
    sessions = []

    async def factory(handler, timeout: float = 5) -> DeribitClient:
        app = web.Application()
        app.router.add_get("/api/v2/public/get_index_price", handler)
        server = TestServer(app)
        await server.start_server()
        servers.append(server)

        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout))
        sessions.append(session)
        return DeribitClient(session, str(server.make_url("/api/v2")))

    yield factory

    for session in sessions:
        await session.close()
    for server in servers:
        await server.close()


async def test_get_index_price(make_client):
    requests = []

    async def handler(request: web.Request) -> web.Response:
        requests.append(dict(request.query))
        return web.json_response(
            {
                "jsonrpc": "2.0",
                "result": {"index_price": 63083.39, "estimated_delivery_price": 63083.39},
                "testnet": False,
            }
        )

    client = await make_client(handler)

    assert await client.get_index_price(Ticker.BTC_USD) == Decimal("63083.39")
    assert requests == [{"index_name": "btc_usd"}]


async def test_deribit_error_response(make_client):
    async def handler(request: web.Request) -> web.Response:
        return web.json_response(
            {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "Invalid params"},
                "testnet": False,
            },
            status=400,
        )

    client = await make_client(handler)

    with pytest.raises(ExchangeError, match="Invalid params"):
        await client.get_index_price(Ticker.ETH_USD)


async def test_not_json_response(make_client):
    async def handler(request: web.Request) -> web.Response:
        return web.Response(text="<html>Bad Gateway</html>", status=502)

    client = await make_client(handler)

    with pytest.raises(ExchangeError):
        await client.get_index_price(Ticker.ETH_USD)


@pytest.mark.parametrize("body", [{"jsonrpc": "2.0", "result": {}}, None, [1, 2]])
async def test_unexpected_response(make_client, body):
    async def handler(request: web.Request) -> web.Response:
        return web.json_response(body)

    client = await make_client(handler)

    with pytest.raises(ExchangeError):
        await client.get_index_price(Ticker.BTC_USD)


async def test_timeout(make_client):
    async def handler(request: web.Request) -> web.Response:
        await asyncio.sleep(1)
        return web.json_response({"result": {"index_price": 1}})

    client = await make_client(handler, timeout=0.1)

    with pytest.raises(ExchangeError):
        await client.get_index_price(Ticker.BTC_USD)


async def test_exchange_unavailable():
    async with aiohttp.ClientSession() as session:
        client = DeribitClient(session, "http://127.0.0.1:1/api/v2")

        with pytest.raises(ExchangeError):
            await client.get_index_price(Ticker.BTC_USD)
