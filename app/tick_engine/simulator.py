import asyncio
import random
from datetime import datetime
from app.indicator_engine.indicators import update_indicators

async def simulate_ticks(symbol: str, store):
    """Simulate live market ticks with random price movements"""
    while symbol in store.subscriptions:
        try:
            async with store.locks[symbol]:
                # Generate tick
                current_price = store.ltp_cache[symbol]
                drift = random.uniform(-0.001, 0.001)  # ±0.1%
                new_price = current_price * (1 + drift)
                volume = random.randint(50, 200)
                
                # Update state
                store.ltp_cache[symbol] = new_price
                store.timestamps[symbol] = datetime.now().timestamp()
                store.price_buffers[symbol].append(new_price)
                store.volume_buffers[symbol].append(volume)
                
                # Update indicators
                update_indicators(symbol, store)
            
            # Random interval 50-300ms
            await asyncio.sleep(random.uniform(0.05, 0.3))
        except Exception as e:
            print(f"Error in tick simulation for {symbol}: {e}")
            break
