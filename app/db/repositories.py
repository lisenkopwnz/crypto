from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PriceModel
from app.domain.entities import IndexPrice, Ticker
from app.domain.interfaces import PriceRepository


class SqlAlchemyPriceRepository(PriceRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, price: IndexPrice) -> None:
        self._session.add(
            PriceModel(ticker=price.ticker.value, price=price.price, timestamp=price.timestamp)
        )
        await self._session.flush()

    async def get_all(self, ticker: Ticker) -> list[IndexPrice]:
        return await self._fetch(self._select(ticker))

    async def get_latest(self, ticker: Ticker) -> IndexPrice | None:
        prices = await self._fetch(self._select(ticker).limit(1))
        return prices[0] if prices else None

    async def get_by_period(self, ticker: Ticker, start: int, end: int) -> list[IndexPrice]:
        query = self._select(ticker).where(
            PriceModel.timestamp >= start, PriceModel.timestamp < end
        )
        return await self._fetch(query)

    @staticmethod
    def _select(ticker: Ticker) -> Select[tuple[PriceModel]]:
        return (
            select(PriceModel)
            .where(PriceModel.ticker == ticker.value)
            .order_by(PriceModel.timestamp.desc())
        )

    async def _fetch(self, query: Select[tuple[PriceModel]]) -> list[IndexPrice]:
        rows = await self._session.scalars(query)
        return [
            IndexPrice(ticker=Ticker(row.ticker), price=row.price, timestamp=row.timestamp)
            for row in rows
        ]
