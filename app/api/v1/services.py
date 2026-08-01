from app.api.v1.schemas.requests.currency import TickerParams
from datetime import datetime, time

def get_range_timestamp(ticker_params: TickerParams):
    start_ts = int(datetime.combine(ticker_params.on_date, time.min).timestamp())
    end_ts = int(datetime.combine(ticker_params.on_date, time.max).timestamp())
    return start_ts, end_ts