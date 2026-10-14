from decimal import Decimal, InvalidOperation

import aiohttp

from app.domain.entities import Ticker
from app.domain.exceptions import ExchangeError
from app.domain.interfaces import ExchangeClient


class DeribitClient(ExchangeClient):
    def __init__(self, session: aiohttp.ClientSession, base_url: str) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")

    async def get_index_price(self, ticker: Ticker) -> Decimal:
        url = f"{self._base_url}/public/get_index_price"
        try:
            async with self._session.get(url, params={"index_name": ticker.value}) as response:
                data = await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as e:
            raise ExchangeError(f"Deribit request failed: {e!r}") from e

        if isinstance(data, dict) and "error" in data:
            raise ExchangeError(f"Deribit error: {data['error']}")
        try:
            return Decimal(str(data["result"]["index_price"]))
        except (KeyError, TypeError, InvalidOperation) as e:
            raise ExchangeError(f"Unexpected Deribit response: {data}") from e
