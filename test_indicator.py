"""Test CSV replay with indicators"""
import asyncio
from app.tick_engine.csv_replay import load_csv, replay_csv_ticks
from app.data_store.state import store

async def test_csv_replay():
    # 1. Load instrument
    store.add_instrument("RELIANCE", 1530.0, 25)
    print(f"Instrument loaded: {store.instruments}")
    print(f"Initial buffers - prices: {len(store.price_buffers['RELIANCE'])}, volumes: {len(store.volume_buffers['RELIANCE'])}")
    
    # 2. Load CSV
    load_csv("RELIANCE.csv", store)
    print(f"\nCSV loaded: {len(store.csv_data.get('RELIANCE', []))} ticks")
    
    # 3. Subscribe and replay first 30 ticks
    store.subscriptions.add("RELIANCE")
    
    # Manually replay first 30 ticks to test
    for i, tick in enumerate(store.csv_data["RELIANCE"][:30]):
        store.ltp_cache["RELIANCE"] = tick["price"]
        store.timestamps["RELIANCE"] = tick["timestamp"]
        store.price_buffers["RELIANCE"].append(tick["price"])
        store.volume_buffers["RELIANCE"].append(tick["volume"])
        
        from app.indicator_engine.indicators import update_indicators
        indicators = update_indicators("RELIANCE", store)
        
        if i in [9, 19, 29]:  # Print at 10, 20, 30 ticks
            print(f"\nAfter {i+1} ticks:")
            print(f"  Price buffer size: {len(store.price_buffers['RELIANCE'])}")
            print(f"  Volume buffer size: {len(store.volume_buffers['RELIANCE'])}")
            print(f"  LTP: {store.ltp_cache['RELIANCE']}")
            print(f"  Indicators: {indicators}")

if __name__ == "__main__":
    asyncio.run(test_csv_replay())
