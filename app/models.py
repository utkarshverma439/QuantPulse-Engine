from pydantic import BaseModel
from typing import List, Optional

class Instrument(BaseModel):
    symbol: str
    entry_price: float
    quantity: int

class SubscribeRequest(BaseModel):
    symbols: List[str]
    mode: str = "simulation"
    csv_file: Optional[str] = None

class IndicatorsResponse(BaseModel):
    sma_20: Optional[float] = None
    ema_10: Optional[float] = None
    roc: Optional[float] = None
    volatility: Optional[float] = None
    vwap: Optional[float] = None

class SnapshotResponse(BaseModel):
    symbol: str
    ltp: float
    timestamp: float
    indicators: IndicatorsResponse
