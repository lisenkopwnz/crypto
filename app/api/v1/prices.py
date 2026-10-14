import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_price_service
from app.api.schemas import PriceResponse
from app.domain.entities import Ticker
from app.services.price_service import PriceService


async def get_prices(
    ticker: Ticker,
    service: Annotated[PriceService, Depends(get_price_service)],
) -> list[PriceResponse]:
    prices = await service.get_all(ticker)
    return [PriceResponse.model_validate(price) for price in prices]


async def get_latest_price(
    ticker: Ticker,
    service: Annotated[PriceService, Depends(get_price_service)],
) -> PriceResponse:
    price = await service.get_latest(ticker)
    if price is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No prices for {ticker} yet")
    return PriceResponse.model_validate(price)


async def get_prices_by_date(
    ticker: Ticker,
    date: datetime.date,
    service: Annotated[PriceService, Depends(get_price_service)],
) -> list[PriceResponse]:
    prices = await service.get_by_date(ticker, date)
    return [PriceResponse.model_validate(price) for price in prices]


def create_router() -> APIRouter:
    router = APIRouter(prefix="/prices", tags=["prices"])
    router.add_api_route("", get_prices, methods=["GET"])
    router.add_api_route("/latest", get_latest_price, methods=["GET"])
    router.add_api_route("/by-date", get_prices_by_date, methods=["GET"])
    return router
