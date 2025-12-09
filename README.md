# ⚡ QuantPulse Engine

Real-time PnL & Indicators Engine built with FastAPI and vanilla JavaScript.

## Features

- **Dual Mode Operation**: Simulation mode (live random ticks) or CSV replay mode
- **Real-time Indicators**: SMA-20, EMA-10, ROC, Volatility, VWAP
- **Live PnL Tracking**: Track profit/loss in real-time
- **Simple Dashboard**: Clean, dark-themed web interface
- **In-Memory Processing**: Fast, no database required

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Backend

```bash
uvicorn app.main:app --reload
```

Backend runs at: `http://localhost:8000`

### 3. Start Frontend

Open `frontend/index.html` in your browser, or serve it:

```bash
cd frontend
python -m http.server 8080
```

Frontend runs at: `http://localhost:8080`

## Usage Flow

### Load Instruments
1. Enter symbol (e.g., RELIANCE)
2. Enter entry price (e.g., 2900)
3. Enter quantity (e.g., 100)
4. Click "Add Instrument"
5. Repeat for more symbols
6. Click "Load All Instruments"

### Subscribe to Symbols
1. Enter symbols (comma-separated, e.g., RELIANCE,TCS)
2. Select mode: Simulation or CSV Replay
3. For CSV mode, enter filename (e.g., RELIANCE.csv)
4. Click "Subscribe"

### Monitor Live Data
1. Select symbol from dropdown
2. View real-time updates:
   - Latest price (LTP)
   - PnL (green=profit, red=loss)
   - All 5 indicators

### CSV Replay Mode
Your CSV should have columns: `Date,Time,Open,High,Low,Close,Volume`

Example format (RELIANCE.csv):
```csv
Date,Time,Open,High,Low,Close,Volume,Open Interest
20251205,09:15,1530.4,1532,1522.4,1526,447582,0
20251205,09:16,1526,1529.9,1526,1528,81335,0
```

The engine will:
- Auto-detect symbol from filename (RELIANCE.csv → RELIANCE)
- Parse Date (YYYYMMDD) and Time (HH:MM) into timestamps
- Use Close price and Volume for tick replay

## API Endpoints

### Instruments
- `POST /instruments/load` - Load instruments
- `GET /instruments/list` - List all instruments

### Market Data
- `POST /subscribe` - Subscribe to symbols
- `POST /unsubscribe/{symbol}` - Unsubscribe
- `GET /price/{symbol}` - Get latest price
- `GET /pnl/{symbol}` - Get PnL
- `GET /indicators/{symbol}` - Get all indicators
- `GET /snapshot/{symbol}?timestamp=` - Get snapshot

## Example API Calls

### Load Instruments
```bash
curl -X POST http://localhost:8000/instruments/load \
  -H "Content-Type: application/json" \
  -d '[{"symbol":"RELIANCE","entry_price":2900,"quantity":100}]'
```

### Subscribe (Simulation Mode)
```bash
curl -X POST http://localhost:8000/subscribe \
  -H "Content-Type: application/json" \
  -d '{"symbols":["RELIANCE"],"mode":"simulation"}'
```

### Subscribe (CSV Mode)
```bash
curl -X POST http://localhost:8000/subscribe \
  -H "Content-Type: application/json" \
  -d '{"symbols":["RELIANCE"],"mode":"csv","csv_file":"RELIANCE.csv"}'
```

### Get Price
```bash
curl http://localhost:8000/price/RELIANCE
```

### Get PnL
```bash
curl http://localhost:8000/pnl/RELIANCE
```

### Get Indicators
```bash
curl http://localhost:8000/indicators/RELIANCE
```

## Architecture

```
app/
├── main.py                 # FastAPI app
├── models.py              # Pydantic models
├── routers/
│   ├── instruments.py     # Instrument management
│   └── market.py          # Market data endpoints
├── tick_engine/
│   ├── simulator.py       # Live tick simulation
│   └── csv_replay.py      # CSV replay logic
├── indicator_engine/
│   └── indicators.py      # All 5 indicators
└── data_store/
    └── state.py           # In-memory state

frontend/
├── index.html             # Dashboard UI
├── style.css              # Dark theme styles
└── app.js                 # API integration
```

## Indicators Explained

- **SMA-20**: Simple Moving Average over last 20 prices
- **EMA-10**: Exponential Moving Average (10-period)
- **ROC**: Rate of Change vs 10 ticks ago (%)
- **Volatility**: Standard deviation of last 50 prices
- **VWAP**: Volume-Weighted Average Price

## Notes

- All data is in-memory (resets on restart)
- Simulation mode: ticks every 50-300ms with ±0.1% drift
- CSV mode: replays historical data with 100ms intervals
- Indicators need minimum data points to calculate
- Frontend auto-refreshes every 1.5 seconds
