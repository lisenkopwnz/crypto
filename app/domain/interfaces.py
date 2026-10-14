from abc import ABC, abstractmethod
from decimal import Decimal

from app.domain.entities import IndexPrice, Ticker


class PriceRepository(ABC):
    @abstractmethod
    async def add(self, price: IndexPrice) -> None: ...

    @abstractmethod
    async def get_all(self, ticker: Ticker) -> list[IndexPrice]: ...

    @abstractmethod
    async def get_latest(self, ticker: Ticker) -> IndexPrice | None: ...

    @abstractmethod
    async def get_by_period(self, ticker: Ticker, start: int, end: int) -> list[IndexPrice]: ...


class ExchangeClient(ABC):
    @abstractmethod
    async def get_index_price(self, ticker: Ticker) -> Decimal: ...
