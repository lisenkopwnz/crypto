from typing import List

from app.api.database import SessionLocal
from app.api.v1.models import Currency
from app.api.v1.repositories.currency_db_repository import CurrencyDBRepository
from app.api.v1.schemas.entity.currency import CurrencyEntity
from app.api.v1.schemas.requests.currency import TickerParams
from app.api.v1.schemas.responses.currency import CurrencyDTO

from sqlalchemy import desc

from app.api.v1.services import get_range_timestamp


class CurrencyDBAdapter(CurrencyDBRepository):
    def get_all_by_ticker(self, ticker_params: TickerParams) -> List[CurrencyDTO] | None:
        with SessionLocal() as db:
            query = db.query(Currency).filter(
                Currency.ticker == ticker_params.ticker
            )

            if ticker_params.on_date:
                start_ts, end_ts = get_range_timestamp(ticker_params)
                query = query.filter(
                    Currency.updated_ts.between(start_ts, end_ts)
                )

            currencies = query.order_by(
                desc(Currency.updated_ts)
            ).all()

            return [
                CurrencyDTO(
                    ticker=currency.ticker,
                    price=float(currency.price),
                    updated=currency.updated_ts
                ) for currency in currencies
            ]

    def get_last_price(self, ticker_params: TickerParams) -> CurrencyDTO | None:
        db = SessionLocal()
        try:
            currency = db.query(Currency).filter(
                Currency.ticker == ticker_params.ticker
            ).order_by(
                desc(Currency.updated_ts)
            ).first()
            if currency:
                return CurrencyDTO(
                    ticker=currency.ticker,
                    price=float(currency.price),
                    updated=currency.updated_ts
                )
        finally:
            db.close()

    def create_data(self, entity: CurrencyEntity) -> None:
         db = SessionLocal()
         try:
             currency = Currency(
                 ticker=entity.ticker,
                 price=entity.price,
                 updated_ts=entity.on_date
             )
             db.add(currency)
             db.commit()
             db.refresh(currency)
         finally:
             db.close()