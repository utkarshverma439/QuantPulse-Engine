import asyncio
from typing import Dict, List, Optional
from collections import deque
from datetime import datetime

class DataStore:
    def __init__(self):
        self.instruments: Dict[str, dict] = {}
        self.subscriptions: set = set()
        self.ltp_cache: Dict[str, float] = {}
        self.timestamps: Dict[str, float] = {}
        self.price_buffers: Dict[str, deque] = {}
        self.volume_buffers: Dict[str, deque] = {}
        self.indicator_cache: Dict[str, dict] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
        self.tick_tasks: Dict[str, asyncio.Task] = {}
        self.csv_data: Dict[str, List[dict]] = {}
        
    def add_instrument(self, symbol: str, entry_price: float, quantity: int):
        self.instruments[symbol] = {
            "entry_price": entry_price,
            "quantity": quantity
        }
        self.ltp_cache[symbol] = entry_price
        self.timestamps[symbol] = datetime.now().timestamp()
        self.price_buffers[symbol] = deque(maxlen=50)
        self.volume_buffers[symbol] = deque(maxlen=50)
        self.indicator_cache[symbol] = {}
        self.locks[symbol] = asyncio.Lock()
        
    def get_pnl(self, symbol: str) -> Optional[float]:
        if symbol not in self.instruments or symbol not in self.ltp_cache:
            return None
        inst = self.instruments[symbol]
        current_price = self.ltp_cache[symbol]
        return (current_price - inst["entry_price"]) * inst["quantity"]

store = DataStore()
