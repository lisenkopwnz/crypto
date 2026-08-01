from fastapi import APIRouter, Depends

from app.api.v1.adapters.currency_db_adapter import CurrencyDBAdapter
from app.api.v1.repositories.currency_db_repository import CurrencyDBRepository
from app.api.v1.schemas.requests.currency import TickerParams
from app.api.v1.usecase.currency_data_usecase import CurrencyDataUseCase
from app.api.v1.usecase.last_currency_price import LastCurrencyPriceUseCase

router = APIRouter()


@router.get("/")
async def get_currency(ticker: TickerParams = Depends()):
    adapter = CurrencyDBAdapter()
    use_case = CurrencyDataUseCase(ticker, adapter)
    return use_case.get_history_currency()


@router.get("/latest-price/")
async def get_latest_price(ticker: TickerParams = Depends()):
    adapter = CurrencyDBAdapter()
    use_case = LastCurrencyPriceUseCase(ticker, adapter)
    return use_case.get_last_price()
