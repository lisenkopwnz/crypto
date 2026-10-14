from pydantic import BaseModel, ConfigDict

from app.domain.entities import Ticker


class PriceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticker: Ticker
    price: float
    timestamp: int
