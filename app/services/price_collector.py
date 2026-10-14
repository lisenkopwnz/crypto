import time

from app.domain.entities import IndexPrice, Ticker
from app.domain.interfaces import ExchangeClient, PriceRepository


class PriceCollector:
    def __init__(self, client: ExchangeClient, repository: PriceRepository) -> None:
        self._client = client
        self._repository = repository

    async def collect(self, ticker: Ticker) -> IndexPrice:
        price = await self._client.get_index_price(ticker)
        index_price = IndexPrice(ticker=ticker, price=price, timestamp=int(time.time()))
        await self._repository.add(index_price)
        return index_price
