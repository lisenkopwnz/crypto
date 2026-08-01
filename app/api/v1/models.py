from sqlalchemy import Column, Integer, String, DECIMAL, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Currency(Base):
    __tablename__ = "currency"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), index=True, nullable=False)
    price = Column(DECIMAL(12, 4), nullable=False)
    updated_ts = Column(Integer, index=True, nullable=False)