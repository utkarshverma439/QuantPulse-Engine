from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from app.models import SubscribeRequest, IndicatorsResponse, SnapshotResponse
from app.data_store.state import store
from app.tick_engine.simulator import simulate_ticks
from app.tick_engine.csv_replay import replay_csv_ticks, load_csv, get_snapshot_at_timestamp
import asyncio

router = APIRouter(tags=["market"])


@router.post("/subscribe")
async def subscribe(request: SubscribeRequest, background_tasks: BackgroundTasks):
    """Subscribe to symbols and start tick generation"""
    results = []

    # Load CSV if in CSV mode
    if request.mode == "csv" and request.csv_file:
        load_csv(request.csv_file, store)

    for symbol in request.symbols:
        if symbol not in store.instruments:
            results.append(
                {
                    "symbol": symbol,
                    "status": "error",
                    "message": "Instrument not loaded",
                }
            )
            continue

        if symbol in store.subscriptions:
            results.append({"symbol": symbol, "status": "already_subscribed"})
            continue

        store.subscriptions.add(symbol)

        # Start tick generation
        if request.mode == "simulation":
            task = asyncio.create_task(simulate_ticks(symbol, store))
        else:  # csv mode
            task = asyncio.create_task(replay_csv_ticks(symbol, store))

        store.tick_tasks[symbol] = task
        results.append(
            {"symbol": symbol, "status": "subscribed", "mode": request.mode}
        )

    return {"results": results}


@router.post("/unsubscribe/{symbol}")
async def unsubscribe(symbol: str):
    """Unsubscribe from a symbol"""
    if symbol in store.subscriptions:
        store.subscriptions.remove(symbol)
        if symbol in store.tick_tasks:
            store.tick_tasks[symbol].cancel()
            del store.tick_tasks[symbol]
        return {"message": f"Unsubscribed from {symbol}"}
    return {"message": f"{symbol} was not subscribed"}


@router.get("/price/{symbol}")
def get_price(symbol: str):
    """Get latest price for a symbol"""
    if symbol not in store.ltp_cache:
        raise HTTPException(status_code=404, detail="Symbol not found")
    return {
        "symbol": symbol,
        "ltp": store.ltp_cache[symbol],
        "timestamp": store.timestamps.get(symbol),
    }


@router.get("/pnl/{symbol}")
def get_pnl(symbol: str):
    """Get PnL for a symbol"""
    pnl = store.get_pnl(symbol)
    if pnl is None:
        raise HTTPException(status_code=404, detail="Symbol not found")
    return {
        "symbol": symbol,
        "pnl": pnl,
        "entry_price": store.instruments[symbol]["entry_price"],
        "current_price": store.ltp_cache[symbol],
        "quantity": store.instruments[symbol]["quantity"],
    }


@router.get("/indicators/{symbol}")
def get_indicators(symbol: str):
    """Get indicators for a symbol"""
    if symbol not in store.instruments:
        raise HTTPException(status_code=404, detail="Symbol not found")
    
    # Return empty indicators if not yet calculated
    if symbol not in store.indicator_cache:
        return {
            "symbol": symbol,
            "indicators": {
                "sma_20": None,
                "ema_10": None,
                "roc": None,
                "volatility": None,
                "vwap": None
            },
        }
    
    return {
        "symbol": symbol,
        "indicators": store.indicator_cache[symbol],
    }


@router.get("/snapshot/{symbol}")
def get_snapshot(symbol: str, timestamp: Optional[float] = None):
    """
    Get snapshot:
    - agar timestamp diya ho -> CSV-replay se uske closest tick ka LTP + indicators
    - agar timestamp na ho -> latest LTP + indicators
    """
    if timestamp is not None:
        # CSV mode - get historical snapshot
        snapshot = get_snapshot_at_timestamp(symbol, timestamp, store)
        if not snapshot:
            raise HTTPException(
                status_code=404, detail="No data found for timestamp"
            )

        # Yaha snapshot me indicators dictionary already hai
        return SnapshotResponse(
            symbol=snapshot["symbol"],
            ltp=snapshot["ltp"],
            timestamp=snapshot["timestamp"],
            indicators=IndicatorsResponse(**snapshot["indicators"]),
        )
    else:
        # Latest snapshot
        if symbol not in store.ltp_cache:
            raise HTTPException(status_code=404, detail="Symbol not found")

        return SnapshotResponse(
            symbol=symbol,
            ltp=store.ltp_cache[symbol],
            timestamp=store.timestamps.get(symbol, 0),
            indicators=IndicatorsResponse(
                **store.indicator_cache.get(symbol, {})
            ),
        )
