from fastapi import APIRouter, HTTPException
from typing import List
from app.models import Instrument
from app.data_store.state import store

router = APIRouter(prefix="/instruments", tags=["instruments"])

@router.post("/load")
def load_instruments(instruments: List[Instrument]):
    """Bulk load instruments"""
    for inst in instruments:
        store.add_instrument(inst.symbol, inst.entry_price, inst.quantity)
    return {"message": f"Loaded {len(instruments)} instruments", "symbols": [i.symbol for i in instruments]}

@router.get("/list")
def list_instruments():
    """List all loaded instruments"""
    return {"instruments": store.instruments}
