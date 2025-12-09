import asyncio
import csv
from collections import deque
from datetime import datetime
from app.indicator_engine.indicators import update_indicators


def load_csv(csv_file: str, store):
    """Load CSV data into memory - supports Date,Time,Open,High,Low,Close,Volume format"""
    data = []
    try:
        with open(csv_file, "r", encoding="latin-1") as f:
            reader = csv.DictReader(f)

            # Detect symbol from filename
            symbol = csv_file.replace(".csv", "").upper()

            for i, row in enumerate(reader):
                try:
                    # Strip all keys to handle spaces in column names
                    row = {k.strip(): v for k, v in row.items()}
                    
                    # Handle BOM and special characters in column names
                    date_key = next((k for k in row.keys() if "Date" in k), "Date")
                    time_key = next((k for k in row.keys() if "Time" in k), "Time")
                    close_key = next((k for k in row.keys() if "Close" in k), "Close")
                    volume_key = next((k for k in row.keys() if "Volume" in k), "Volume")

                    date_str = row[date_key].strip()
                    time_str = row[time_key].strip()

                    # Parse datetime (expects YYYYMMDD + HH:MM)
                    dt = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H:%M")
                    timestamp = dt.timestamp()

                    # Get close price and volume
                    close_price = float(row[close_key].strip())
                    volume = int(row[volume_key].strip())

                    data.append(
                        {
                            "timestamp": timestamp,
                            "symbol": symbol,
                            "price": close_price,
                            "volume": volume,
                        }
                    )
                except Exception as e:
                    # Only print a few initial parse errors
                    if i < 5:
                        print(f"Error parsing row {i}: {e}")
                    continue

        # Sort by timestamp (time-ordered ticks)
        data.sort(key=lambda x: x["timestamp"])

        # Group by symbol into store.csv_data
        for row in data:
            sym = row["symbol"]
            if sym not in store.csv_data:
                store.csv_data[sym] = []
            store.csv_data[sym].append(row)

        print(f"Loaded {len(data)} ticks for {symbol} from CSV")
    except Exception as e:
        print(f"Error loading CSV: {e}")

    return data

async def replay_csv_ticks(symbol: str, store):
    """Replay ticks from CSV data"""
    if symbol not in store.csv_data:
        print(f"No CSV data for {symbol}")
        return
    
    print(f"Starting CSV replay for {symbol} with {len(store.csv_data[symbol])} ticks")
    
    for tick in store.csv_data[symbol]:
        if symbol not in store.subscriptions:
            break
        
        async with store.locks[symbol]:
            store.ltp_cache[symbol] = tick["price"]
            store.timestamps[symbol] = tick["timestamp"]
            store.price_buffers[symbol].append(tick["price"])
            store.volume_buffers[symbol].append(tick["volume"])
            update_indicators(symbol, store)
        
        await asyncio.sleep(0.1)

# async def replay_csv_ticks(symbol: str, store):
#     """Replay ticks from CSV data"""
#     if symbol not in store.csv_data:
#         print(f"No CSV data for {symbol}")
#         return

#     for tick in store.csv_data[symbol]:
#         # Agar beech me unsubscribe ho gaya to break
#         if symbol not in store.subscriptions:
#             break

#         try:
#             async with store.locks[symbol]:
#                 # Update state from CSV tick
#                 store.ltp_cache[symbol] = tick["price"]
#                 store.timestamps[symbol] = tick["timestamp"]
#                 store.price_buffers[symbol].append(tick["price"])
#                 store.volume_buffers[symbol].append(tick["volume"])

#                 # Update indicators for this tick
#                 update_indicators(symbol, store)

#             # Small delay between ticks (simulate streaming)
#             await asyncio.sleep(0.1)
#         except Exception as e:
#             print(f"Error in CSV replay for {symbol}: {e}")
#             break


def get_snapshot_at_timestamp(symbol: str, timestamp: float, store) -> dict:
    """
    Get snapshot (LTP + indicators) for the tick closest to a timestamp from CSV data.
    Ye function ab sirf price nahi, balki us point tak ka full indicator state bhi banata hai.
    """
    if symbol not in store.csv_data:
        return None

    ticks = store.csv_data[symbol]
    if not ticks:
        return None

    # 1) Find closest tick index by timestamp
    closest_idx = 0
    min_diff = float("inf")
    for idx, tick in enumerate(ticks):
        diff = abs(tick["timestamp"] - timestamp)
        if diff < min_diff:
            min_diff = diff
            closest_idx = idx

    # 2) Use all ticks up to that index to rebuild rolling buffers
    used_ticks = ticks[: closest_idx + 1]
    last_tick = used_ticks[-1]

    prices = deque((t["price"] for t in used_ticks), maxlen=50)
    volumes = deque((t["volume"] for t in used_ticks), maxlen=50)

    # 3) Temporary store-like object so we can reuse update_indicators()
    class _TempStore:
        def __init__(self, sym, prices_buf, volumes_buf):
            self.price_buffers = {sym: prices_buf}
            self.volume_buffers = {sym: volumes_buf}
            self.indicator_cache = {sym: {}}

    temp_store = _TempStore(symbol, prices, volumes)

    # 4) Reuse the existing indicator computation
    indicators = update_indicators(symbol, temp_store)

    # 5) Return full snapshot for that timestamp
    return {
        "symbol": symbol,
        "ltp": last_tick["price"],
        "timestamp": last_tick["timestamp"],
        "volume": last_tick["volume"],
        "indicators": indicators,
    }
