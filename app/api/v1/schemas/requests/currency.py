from datetime import date

from pydantic import BaseModel, Field, field_validator


class TickerParams(BaseModel):
    ticker: str = Field(..., min_length=3, max_length=10)
    on_date: date | None = None

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, ticker: str) -> str:
        allowed = ["btc_usd", "eth_usd"]
        if ticker not in allowed:
            raise ValueError(f"Ticker must be one of {allowed}")
        return ticker
