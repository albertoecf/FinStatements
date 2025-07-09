from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class StockMarket(str, Enum):
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    TSE = "TSE"  # Tokyo Stock Exchange
    SSE = "SSE"  # Shanghai Stock Exchange
    LSE = "LSE"  # London Stock Exchange
    OTHER = "OTHER"


class Company(BaseModel):
    name: str = Field(..., description="Name of the company")
    is_public: bool = Field(..., description="Indicates if the company is public")
    industry: Optional[str] = Field(None, description="NAICS industry code")
    symbol: Optional[str] = Field(None, description="Stock ticker symbol, if public")
    stock_market: StockMarket = Field(StockMarket.NYSE,
                                      description="Stock market where the company is listed (default NYSE)")

    class Config:
        schema_extra = {
            "example": {
                "name": "Apple Inc.",
                "is_public": True,
                "industry": "334111",
                "symbol": "AAPL",
                "stock_market": "NASDAQ"
            }
        }
