#!/usr/bin/env python3
"""
Strategy Conditions Monitor for E0V1E
Monitors trading conditions in real-time on port 8503
"""

from flask import Flask, render_template_string, jsonify
import requests
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Freqtrade API configuration - try Enhanced bot first, fallback to original
FREQTRADE_API_URLS = [
    "http://localhost:8080/api/v1",  # Enhanced bot
    "http://localhost:8081/api/v1"   # Original bot
]
FREQTRADE_AUTH = ("freqtrade", "ruriu7AY")

# Current API URL (will be set dynamically)
FREQTRADE_API_URL = FREQTRADE_API_URLS[0]

# Strategy parameters - auto-detect from API or use defaults
STRATEGY_PARAMS = {
    'E0V1E': {
        'buy_rsi_fast_32': 30,
        'buy_rsi_32': 24,
        'buy_sma15_32': 0.96,
        'buy_cti_32': 0.69
    },
    'E0V1E_Enhanced': {
        'buy_rsi_fast_32': 35,
        'buy_rsi_32': 24,
        'buy_sma15_32': 0.98,
        'buy_cti_32': 0.75
    }
}

# Global variable to store conditions data
conditions_data = {}

def get_pair_data(pair):
    """Get current market data and indicators for a pair"""
    global FREQTRADE_API_URL

    # Try both API endpoints
    for api_url in FREQTRADE_API_URLS:
        try:
            url = f"{api_url}/pair_candles"
            params = {
                'pair': pair,
                'timeframe': '5m',
                'limit': 3
            }
            response = requests.get(url, auth=FREQTRADE_AUTH, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) >= 2:
                    current = data['data'][-1]  # Latest candle
                    previous = data['data'][-2]  # Previous candle

                    # Update global API URL to the working one
                    FREQTRADE_API_URL = api_url

                    return {
                        'price': current[4],  # close
                        'rsi': current[8],
                        'rsi_fast': current[9],
                        'rsi_slow': current[10],
                        'rsi_slow_prev': previous[10],
                        'cti': current[7],
                        'sma_15': current[6],
                        'close_sma15_ratio': current[4] / current[6] if current[6] > 0 else 0
                    }
        except Exception as e:
            print(f"Error getting data for {pair} from {api_url}: {e}")
            continue

    return None

def get_current_strategy():
    """Get current strategy name from API"""
    try:
        response = requests.get(f"{FREQTRADE_API_URL}/show_config", auth=FREQTRADE_AUTH, timeout=5)
        if response.status_code == 200:
            config = response.json()
            return config.get('strategy', 'NFI5MOHO_WIP')
    except:
        pass
    return 'NFI5MOHO_WIP'

def check_conditions(pair_data):
    """Check which strategy entry conditions are met"""
    if not pair_data:
        return {}

    # Get current strategy parameters
    current_strategy = get_current_strategy()
    params = STRATEGY_PARAMS.get(current_strategy, STRATEGY_PARAMS['E0V1E'])

    conditions = {}

    # Condition 1: RSI slow declining
    conditions['rsi_slow_declining'] = pair_data['rsi_slow'] < pair_data['rsi_slow_prev']

    # Condition 2: RSI fast < threshold
    conditions['rsi_fast_low'] = pair_data['rsi_fast'] < params['buy_rsi_fast_32']

    # Condition 3: RSI > threshold
    conditions['rsi_above_min'] = pair_data['rsi'] > params['buy_rsi_32']

    # Condition 4: Close < SMA15 * threshold
    conditions['price_below_sma'] = pair_data['close_sma15_ratio'] < params['buy_sma15_32']

    # Condition 5: CTI < threshold
    conditions['cti_low'] = pair_data['cti'] < params['buy_cti_32']

    # Count met conditions
    met_conditions = sum(1 for condition in conditions.values() if condition)

    return {
        'conditions': conditions,
        'met_count': met_conditions,
        'total_count': len(conditions),
        'ready_to_trade': met_conditions == len(conditions),
        'strategy': current_strategy,
        'params': params
    }

def update_conditions():
    """Update conditions for all pairs"""
    global conditions_data

    try:
        # Get whitelist
        response = requests.get(f"{FREQTRADE_API_URL}/whitelist", auth=FREQTRADE_AUTH, timeout=5)
        if response.status_code == 200:
            whitelist = response.json().get('whitelist', [])

            new_data = {}
            for pair in whitelist:
                pair_data = get_pair_data(pair)
                if pair_data:
                    conditions = check_conditions(pair_data)
                    new_data[pair] = {
                        'pair_data': pair_data,
                        'conditions': conditions,
                        'last_update': datetime.now().strftime('%H:%M:%S')
                    }

            conditions_data = new_data

    except Exception as e:
        print(f"Error updating conditions: {e}")

def background_updater():
    """Background thread to update conditions every 10 seconds"""
    while True:
        update_conditions()
        time.sleep(10)

# Start background updater
updater_thread = threading.Thread(target=background_updater, daemon=True)
updater_thread.start()

@app.route('/')
def index():
    """Main dashboard page"""
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>NFI5MOHO_WIP Strategy Conditions Monitor</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header p {
            margin: 10px 0;
            font-size: 1.2em;
            opacity: 0.9;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .pair-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }
        .pair-card:hover {
            transform: translateY(-5px);
        }
        .pair-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .pair-name {
            font-size: 1.5em;
            font-weight: bold;
        }
        .conditions-score {
            font-size: 1.2em;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }
        .score-ready {
            background: #4CAF50;
            color: white;
        }
        .score-close {
            background: #FF9800;
            color: white;
        }
        .score-far {
            background: #f44336;
            color: white;
        }
        .price-info {
            margin-bottom: 15px;
            font-size: 1.1em;
        }
        .conditions-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .condition-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .condition-item:last-child {
            border-bottom: none;
        }
        .condition-status {
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.9em;
            font-weight: bold;
        }
        .status-met {
            background: #4CAF50;
            color: white;
        }
        .status-not-met {
            background: #f44336;
            color: white;
        }
        .last-update {
            text-align: center;
            margin-top: 15px;
            font-size: 0.9em;
            opacity: 0.7;
        }
        .loading {
            text-align: center;
            font-size: 1.2em;
            margin: 50px 0;
        }
        .strategy-params {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 30px;
            max-width: 1400px;
            margin-left: auto;
            margin-right: auto;
        }
        .strategy-params h3 {
            margin-top: 0;
            text-align: center;
        }
        .params-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }
        .param-item {
            text-align: center;
            padding: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 NFI5MOHO_WIP Strategy Monitor</h1>
        <p>Real-time Trading Conditions Dashboard</p>
    </div>

    <div class="strategy-params">
        <h3>📊 Strategy Parameters (From Hyperopt Results)</h3>
        <div class="params-grid">
            <div class="param-item">RSI Fast < <strong>35</strong></div>
            <div class="param-item">RSI > <strong>24</strong></div>
            <div class="param-item">Price < SMA15 × <strong>0.98</strong></div>
            <div class="param-item">CTI < <strong>0.75</strong></div>
            <div class="param-item">RSI Slow <strong>Declining</strong></div>
        </div>
    </div>

    <div id="dashboard">
        <div class="loading">⏳ Loading conditions data...</div>
    </div>

    <script>
        function updateDashboard() {
            fetch('/api/conditions')
                .then(response => response.json())
                .then(data => {
                    const dashboard = document.getElementById('dashboard');

                    if (Object.keys(data).length === 0) {
                        dashboard.innerHTML = '<div class="loading">📡 Waiting for data...</div>';
                        return;
                    }

                    let html = '<div class="grid">';

                    Object.entries(data).forEach(([pair, info]) => {
                        const conditions = info.conditions;
                        const pairData = info.pair_data;
                        const metCount = conditions.met_count;
                        const totalCount = conditions.total_count;

                        let scoreClass = 'score-far';
                        if (metCount === totalCount) scoreClass = 'score-ready';
                        else if (metCount >= totalCount - 1) scoreClass = 'score-close';

                        html += `
                            <div class="pair-card">
                                <div class="pair-header">
                                    <div class="pair-name">${pair}</div>
                                    <div class="conditions-score ${scoreClass}">
                                        ${metCount}/${totalCount}
                                        ${conditions.ready_to_trade ? '🚀' : '⏳'}
                                    </div>
                                </div>

                                <div class="price-info">
                                    💰 Price: <strong>$${pairData.price.toFixed(4)}</strong>
                                </div>

                                <ul class="conditions-list">
                                    <li class="condition-item">
                                        <span>RSI Slow Declining</span>
                                        <span class="condition-status ${conditions.conditions.rsi_slow_declining ? 'status-met' : 'status-not-met'}">
                                            ${conditions.conditions.rsi_slow_declining ? '✅' : '❌'}
                                        </span>
                                    </li>
                                    <li class="condition-item">
                                        <span>RSI Fast < 35 (${pairData.rsi_fast.toFixed(1)})</span>
                                        <span class="condition-status ${conditions.conditions.rsi_fast_low ? 'status-met' : 'status-not-met'}">
                                            ${conditions.conditions.rsi_fast_low ? '✅' : '❌'}
                                        </span>
                                    </li>
                                    <li class="condition-item">
                                        <span>RSI > 24 (${pairData.rsi.toFixed(1)})</span>
                                        <span class="condition-status ${conditions.conditions.rsi_above_min ? 'status-met' : 'status-not-met'}">
                                            ${conditions.conditions.rsi_above_min ? '✅' : '❌'}
                                        </span>
                                    </li>
                                    <li class="condition-item">
                                        <span>Price < SMA15×0.98 (${(pairData.close_sma15_ratio).toFixed(4)})</span>
                                        <span class="condition-status ${conditions.conditions.price_below_sma ? 'status-met' : 'status-not-met'}">
                                            ${conditions.conditions.price_below_sma ? '✅' : '❌'}
                                        </span>
                                    </li>
                                    <li class="condition-item">
                                        <span>CTI < 0.75 (${pairData.cti.toFixed(3)})</span>
                                        <span class="condition-status ${conditions.conditions.cti_low ? 'status-met' : 'status-not-met'}">
                                            ${conditions.conditions.cti_low ? '✅' : '❌'}
                                        </span>
                                    </li>
                                </ul>

                                <div class="last-update">
                                    🕒 Last Update: ${info.last_update}
                                </div>
                            </div>
                        `;
                    });

                    html += '</div>';
                    dashboard.innerHTML = html;
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                    document.getElementById('dashboard').innerHTML =
                        '<div class="loading">❌ Error loading data. Check connection.</div>';
                });
        }

        // Update every 5 seconds
        updateDashboard();
        setInterval(updateDashboard, 5000);
    </script>
</body>
</html>
    """
    return render_template_string(html_template)

@app.route('/api/conditions')
def api_conditions():
    """API endpoint to get current conditions data"""
    return jsonify(conditions_data)

@app.route('/api/strategy-params')
def api_strategy_params():
    """API endpoint to get strategy parameters"""
    return jsonify(STRATEGY_PARAMS)

if __name__ == '__main__':
    print("🚀 Starting NFI5MOHO_WIP Strategy Conditions Monitor on port 8507...")
    print("📊 Dashboard: http://localhost:8507")
    print("🔄 Auto-refresh every 10 seconds")

    # Initial data load
    update_conditions()

    app.run(host='0.0.0.0', port=8507, debug=False, threaded=True)