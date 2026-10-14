from datetime import UTC, date, datetime, time, timedelta

from app.domain.entities import IndexPrice, Ticker
from app.domain.interfaces import PriceRepository


class PriceService:
    def __init__(self, repository: PriceRepository) -> None:
        self._repository = repository

    async def get_all(self, ticker: Ticker) -> list[IndexPrice]:
        return await self._repository.get_all(ticker)

    async def get_latest(self, ticker: Ticker) -> IndexPrice | None:
        return await self._repository.get_latest(ticker)

    async def get_by_date(self, ticker: Ticker, day: date) -> list[IndexPrice]:
        start = datetime.combine(day, time.min, tzinfo=UTC)
        end = start + timedelta(days=1)
        return await self._repository.get_by_period(
            ticker, int(start.timestamp()), int(end.timestamp())
        )
