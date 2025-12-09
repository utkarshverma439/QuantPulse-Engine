const API_BASE = 'http://localhost:8000';
let instruments = [];
let currentSymbol = null;
let updateInterval = null;

function addInstrument() {
    const symbol = document.getElementById('symbol').value.trim();
    const entryPrice = parseFloat(document.getElementById('entryPrice').value);
    const quantity = parseInt(document.getElementById('quantity').value);
    
    if (!symbol || !entryPrice || !quantity) {
        alert('Please fill all fields');
        return;
    }
    
    instruments.push({ symbol, entry_price: entryPrice, quantity });
    updateInstrumentList();
    
    document.getElementById('symbol').value = '';
    document.getElementById('entryPrice').value = '';
    document.getElementById('quantity').value = '';
}

function updateInstrumentList() {
    const list = document.getElementById('instrumentList');
    list.innerHTML = instruments.map(i => 
        `<div class="instrument-item">${i.symbol} - Entry: ${i.entry_price} - Qty: ${i.quantity}</div>`
    ).join('');
}

async function loadInstruments() {
    if (instruments.length === 0) {
        alert('No instruments to load');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/instruments/load`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(instruments)
        });
        const data = await response.json();
        alert(`Loaded: ${data.symbols.join(', ')}`);
        updateSymbolDropdown();
    } catch (error) {
        alert('Error loading instruments: ' + error.message);
    }
}

async function subscribe() {
    const symbolsInput = document.getElementById('subscribeSymbols').value.trim();
    const mode = document.getElementById('mode').value;
    const csvFile = document.getElementById('csvFile').value.trim();
    
    if (!symbolsInput) {
        alert('Please enter symbols');
        return;
    }
    
    const symbols = symbolsInput.split(',').map(s => s.trim());
    const payload = { symbols, mode };
    if (mode === 'csv' && csvFile) {
        payload.csv_file = csvFile;
    }
    
    try {
        const response = await fetch(`${API_BASE}/subscribe`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        alert('Subscription results: ' + JSON.stringify(data.results));
        updateSymbolDropdown();
    } catch (error) {
        alert('Error subscribing: ' + error.message);
    }
}

function updateSymbolDropdown() {
    const select = document.getElementById('selectedSymbol');
    const currentValue = select.value;
    
    select.innerHTML = '<option value="">-- Select Symbol --</option>';
    instruments.forEach(inst => {
        const option = document.createElement('option');
        option.value = inst.symbol;
        option.textContent = inst.symbol;
        select.appendChild(option);
    });
    
    if (currentValue) {
        select.value = currentValue;
    }
}

function updateSymbol() {
    const symbol = document.getElementById('selectedSymbol').value;
    if (!symbol) {
        stopUpdates();
        return;
    }
    
    currentSymbol = symbol;
    startUpdates();
}

function startUpdates() {
    stopUpdates();
    updateData();
    updateInterval = setInterval(updateData, 1500);
}

function stopUpdates() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
}

async function updateData() {
    if (!currentSymbol) return;
    
    try {
        const [priceRes, pnlRes, indicatorsRes] = await Promise.all([
            fetch(`${API_BASE}/price/${currentSymbol}`),
            fetch(`${API_BASE}/pnl/${currentSymbol}`),
            fetch(`${API_BASE}/indicators/${currentSymbol}`)
        ]);
        
        const priceData = await priceRes.json();
        const pnlData = await pnlRes.json();
        const indicatorsData = await indicatorsRes.json();
        
        document.getElementById('ltp').textContent = priceData.ltp.toFixed(2);
        document.getElementById('timestamp').textContent = new Date(priceData.timestamp * 1000).toLocaleTimeString();
        
        document.getElementById('entryPriceDisplay').textContent = pnlData.entry_price.toFixed(2);
        document.getElementById('currentPrice').textContent = pnlData.current_price.toFixed(2);
        document.getElementById('quantityDisplay').textContent = pnlData.quantity;
        
        const pnlElement = document.getElementById('pnl');
        pnlElement.textContent = pnlData.pnl.toFixed(2);
        pnlElement.className = 'value pnl-value ' + (pnlData.pnl >= 0 ? 'positive' : 'negative');
        
        const ind = indicatorsData.indicators;
        console.log('Indicators received:', ind);  // Debug log
        document.getElementById('sma20').textContent = (ind.sma_20 !== null && ind.sma_20 !== undefined) ? ind.sma_20.toFixed(2) : '--';
        document.getElementById('ema10').textContent = (ind.ema_10 !== null && ind.ema_10 !== undefined) ? ind.ema_10.toFixed(2) : '--';
        document.getElementById('roc').textContent = (ind.roc !== null && ind.roc !== undefined) ? ind.roc.toFixed(2) + '%' : '--';
        document.getElementById('volatility').textContent = (ind.volatility !== null && ind.volatility !== undefined) ? ind.volatility.toFixed(2) : '--';
        document.getElementById('vwap').textContent = (ind.vwap !== null && ind.vwap !== undefined) ? ind.vwap.toFixed(2) : '--';
    } catch (error) {
        console.error('Error updating data:', error);
    }
}

async function getSnapshot() {
    if (!currentSymbol) {
        alert('Please select a symbol first');
        return;
    }
    
    const timestamp = document.getElementById('snapshotTimestamp').value;
    const url = timestamp 
        ? `${API_BASE}/snapshot/${currentSymbol}?timestamp=${timestamp}`
        : `${API_BASE}/snapshot/${currentSymbol}`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        const result = document.getElementById('snapshotResult');
        result.innerHTML = `
            <div style="padding: 10px;">
                <strong>Symbol:</strong> ${data.symbol}<br>
                <strong>LTP:</strong> ${data.ltp.toFixed(2)}<br>
                <strong>Timestamp:</strong> ${new Date(data.timestamp * 1000).toLocaleString()}<br>
                <strong>SMA-20:</strong> ${data.indicators.sma_20 ? data.indicators.sma_20.toFixed(2) : 'N/A'}<br>
                <strong>EMA-10:</strong> ${data.indicators.ema_10 ? data.indicators.ema_10.toFixed(2) : 'N/A'}<br>
                <strong>ROC:</strong> ${data.indicators.roc ? data.indicators.roc.toFixed(2) + '%' : 'N/A'}<br>
                <strong>Volatility:</strong> ${data.indicators.volatility ? data.indicators.volatility.toFixed(2) : 'N/A'}<br>
                <strong>VWAP:</strong> ${data.indicators.vwap ? data.indicators.vwap.toFixed(2) : 'N/A'}
            </div>
        `;
    } catch (error) {
        alert('Error getting snapshot: ' + error.message);
    }
}
