from app.api.v1.repositories.currency_db_repository import CurrencyDBRepository
from app.api.v1.schemas.requests.currency import TickerParams


class CurrencyDataUseCase:
    def __init__(
            self,
            ticker: TickerParams,
            currency_db_adapter: CurrencyDBRepository
    ):
        self.ticker = ticker
        self.currency_db_adapter = currency_db_adapter

    def get_history_currency(self):
        return self.currency_db_adapter.get_all_by_ticker(self.ticker)