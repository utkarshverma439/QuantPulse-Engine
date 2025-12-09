import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_root():
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_load_instruments():
    print("\n=== Testing Load Instruments ===")
    instruments = [
        {"symbol": "AAPL", "entry_price": 150.0, "quantity": 50},
        {"symbol": "GOOGL", "entry_price": 2800.0, "quantity": 10}
    ]
    response = requests.post(f"{BASE_URL}/instruments/load", json=instruments)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_list_instruments():
    print("\n=== Testing List Instruments ===")
    response = requests.get(f"{BASE_URL}/instruments/list")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Instruments: {json.dumps(data, indent=2)}")
    assert response.status_code == 200

def test_subscribe_simulation():
    print("\n=== Testing Subscribe (Simulation Mode) ===")
    payload = {
        "symbols": ["AAPL", "GOOGL"],
        "mode": "simulation"
    }
    response = requests.post(f"{BASE_URL}/subscribe", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_price():
    print("\n=== Testing Price Endpoint ===")
    time.sleep(2)  # Wait for ticks
    response = requests.get(f"{BASE_URL}/price/AAPL")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"AAPL Price: {json.dumps(data, indent=2)}")
    assert response.status_code == 200
    assert "ltp" in data

def test_pnl():
    print("\n=== Testing PnL Endpoint ===")
    response = requests.get(f"{BASE_URL}/pnl/AAPL")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"AAPL PnL: {json.dumps(data, indent=2)}")
    assert response.status_code == 200
    assert "pnl" in data

def test_indicators():
    print("\n=== Testing Indicators Endpoint ===")
    time.sleep(3)  # Wait for more ticks to build indicators
    response = requests.get(f"{BASE_URL}/indicators/AAPL")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"AAPL Indicators: {json.dumps(data, indent=2)}")
    assert response.status_code == 200
    assert "indicators" in data

def test_snapshot():
    print("\n=== Testing Snapshot Endpoint ===")
    response = requests.get(f"{BASE_URL}/snapshot/AAPL")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"AAPL Snapshot: {json.dumps(data, indent=2)}")
    assert response.status_code == 200
    assert "ltp" in data
    assert "indicators" in data

def test_csv_mode():
    print("\n=== Testing CSV Replay Mode ===")
    # Load RELIANCE instrument
    instruments = [{"symbol": "RELIANCE", "entry_price": 1530.0, "quantity": 100}]
    response = requests.post(f"{BASE_URL}/instruments/load", json=instruments)
    print(f"Load Status: {response.status_code}")
    
    # Subscribe in CSV mode
    payload = {
        "symbols": ["RELIANCE"],
        "mode": "csv",
        "csv_file": "RELIANCE.csv"
    }
    response = requests.post(f"{BASE_URL}/subscribe", json=payload)
    print(f"Subscribe Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Wait for CSV replay
    time.sleep(2)
    
    # Check price
    response = requests.get(f"{BASE_URL}/price/RELIANCE")
    print(f"RELIANCE Price: {response.json()}")
    
    # Check indicators
    response = requests.get(f"{BASE_URL}/indicators/RELIANCE")
    print(f"RELIANCE Indicators: {response.json()}")
    
    # Test snapshot with timestamp
    response = requests.get(f"{BASE_URL}/snapshot/RELIANCE?timestamp=1764915720")
    print(f"RELIANCE Snapshot at timestamp: {response.json()}")

def test_unsubscribe():
    print("\n=== Testing Unsubscribe ===")
    response = requests.post(f"{BASE_URL}/unsubscribe/AAPL")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

if __name__ == "__main__":
    print("=" * 60)
    print("QuantPulse Engine - Comprehensive Test Suite")
    print("=" * 60)
    
    try:
        test_root()
        test_load_instruments()
        test_list_instruments()
        test_subscribe_simulation()
        test_price()
        test_pnl()
        test_indicators()
        test_snapshot()
        test_unsubscribe()
        test_csv_mode()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
