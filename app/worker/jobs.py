import aiohttp
from sqlalchemy.pool import NullPool

from app.clients.deribit import DeribitClient
from app.config import Settings
from app.db.database import Database
from app.db.repositories import SqlAlchemyPriceRepository
from app.domain.entities import IndexPrice, Ticker
from app.services.price_collector import PriceCollector


async def collect_price(ticker: Ticker, settings: Settings) -> IndexPrice:
    database = Database(settings.database_url, poolclass=NullPool)
    timeout = aiohttp.ClientTimeout(total=settings.deribit_timeout)
    async with (
        aiohttp.ClientSession(timeout=timeout) as http_session,
        database.session() as db_session,
    ):
        collector = PriceCollector(
            DeribitClient(http_session, settings.deribit_base_url),
            SqlAlchemyPriceRepository(db_session),
        )
        return await collector.collect(ticker)
