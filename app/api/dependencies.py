from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import SqlAlchemyPriceRepository
from app.services.price_service import PriceService


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.database.session() as session:
        yield session


def get_price_service(session: Annotated[AsyncSession, Depends(get_session)]) -> PriceService:
    return PriceService(SqlAlchemyPriceRepository(session))
