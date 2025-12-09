from collections import deque
from typing import Optional
import math

def calculate_sma(prices: deque, window: int = 20) -> Optional[float]:
    if len(prices) < window:
        return None
    return sum(list(prices)[-window:]) / window

def calculate_ema(prices: deque, prev_ema: Optional[float], window: int = 10) -> Optional[float]:
    if len(prices) == 0:
        return None
    current_price = prices[-1]
    if prev_ema is None:
        if len(prices) >= window:
            return sum(list(prices)[-window:]) / window
        return None
    multiplier = 2 / (window + 1)
    return (current_price - prev_ema) * multiplier + prev_ema

def calculate_roc(prices: deque, n: int = 10) -> Optional[float]:
    if len(prices) < n + 1:
        return None
    current = prices[-1]
    past = list(prices)[-(n+1)]
    return ((current - past) / past) * 100

def calculate_volatility(prices: deque, window: int = 50) -> Optional[float]:
    if len(prices) < 2:
        return None
    price_list = list(prices)[-window:]
    if len(price_list) < 2:
        return None
    mean = sum(price_list) / len(price_list)
    variance = sum((p - mean) ** 2 for p in price_list) / len(price_list)
    return math.sqrt(variance)

def calculate_vwap(prices: deque, volumes: deque) -> Optional[float]:
    if len(prices) == 0 or len(volumes) == 0:
        return None
    price_list = list(prices)
    volume_list = list(volumes)
    min_len = min(len(price_list), len(volume_list))
    if min_len == 0:
        return None
    total_pv = sum(price_list[i] * volume_list[i] for i in range(min_len))
    total_v = sum(volume_list[:min_len])
    return total_pv / total_v if total_v > 0 else None

def update_indicators(symbol: str, store) -> dict:
    prices = store.price_buffers[symbol]
    volumes = store.volume_buffers[symbol]
    
    # Initialize indicator_cache for symbol if not exists
    if symbol not in store.indicator_cache:
        store.indicator_cache[symbol] = {}
    
    prev_ema = store.indicator_cache[symbol].get("ema_10")
    
    indicators = {
        "sma_20": calculate_sma(prices, 20),
        "ema_10": calculate_ema(prices, prev_ema, 10),
        "roc": calculate_roc(prices, 10),
        "volatility": calculate_volatility(prices, 50),
        "vwap": calculate_vwap(prices, volumes)
    }
    
    store.indicator_cache[symbol] = indicators
    return indicators
