import os
import time

import requests

from app.api.v1.adapters.currency_db_adapter import CurrencyDBAdapter
from app.api.v1.repositories.currency_db_repository import CurrencyDBRepository
from app.api.v1.schemas.entity.currency import CurrencyEntity
from app.celery_app import app as celery_app


@celery_app.task(bind=True)
def fetch_currency_price(self):
    try:
        get_ticker_data("btc_usd", currency_adapter=CurrencyDBAdapter())
        get_ticker_data("eth_usd", currency_adapter=CurrencyDBAdapter())
    except requests.exceptions.RequestException as e:
        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True)
def fetch_ethereum_price(self):
    try:
        get_ticker_data("eth_usd", currency_adapter=CurrencyDBAdapter())
    except requests.exceptions.RequestException as e:
        raise self.retry(exc=e, countdown=60, max_retries=100)


def get_ticker_data(ticker: str, currency_adapter: CurrencyDBRepository):
    base_url = os.getenv("DERIBIT_BASE_URL")
    get_index_price_url = f"{base_url}/get_index_price?index_name={ticker}"

    response = requests.get(get_index_price_url, timeout=10)
    response.raise_for_status()
    data = response.json()

    currency = CurrencyEntity(
        ticker=ticker,
        price = data['result']['index_price'],
        on_date = int(time.time())
    )
    currency_adapter.create_data(currency)




