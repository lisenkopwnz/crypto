from abc import ABC, abstractmethod
from typing import List

from app.api.v1.schemas.entity.currency import CurrencyEntity
from app.api.v1.schemas.requests.currency import TickerParams
from app.api.v1.schemas.responses.currency import CurrencyDTO


class CurrencyDBRepository(ABC):
    @abstractmethod
    def get_all_by_ticker(self, ticker_params: TickerParams) -> List[CurrencyDTO] | None:
        raise NotImplementedError

    @abstractmethod
    def get_last_price(self, ticker_params: TickerParams) -> CurrencyDTO | None:
        raise NotImplementedError

    @abstractmethod
    def create_data(self, entity: CurrencyEntity) -> None:
        raise NotImplementedError
