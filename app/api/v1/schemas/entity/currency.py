from datetime import date

from pydantic import BaseModel, Field, field_validator


class CurrencyEntity(BaseModel):
    ticker: str = Field(..., min_length=3, max_length=10)
    price: float
    on_date: int
