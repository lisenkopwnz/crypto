from datetime import datetime
from pydantic import BaseModel


class CurrencyDTO(BaseModel):
    ticker: str
    price: float
    updated: datetime