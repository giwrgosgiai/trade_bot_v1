#!/usr/bin/env python3
"""
Strategy Monitor - Real-time monitoring of E0V1E_Enhanced strategy conditions
"""

import os
import sys
import time
import json
import logging
import requests
import pandas as pd
from datetime import datetime
from flask import Flask, render_template_string, jsonify
from threading import Thread
import random

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/strategy_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class StrategyMonitor:
    def __init__(self):
        self.freqtrade_api = "http://localhost:8080"
        self.auth = ("freqtrade", "ruriu7AY")

        # Updated pairs list with new coins
        self.pairs = [
            'BTC/USDC', 'ETH/USDC', 'ADA/USDC', 'DOT/USDC', 'SOL/USDC', 'LINK/USDC',
            'AVAX/USDC', 'BNB/USDC', 'XRP/USDC', 'UNI/USDC', 'ATOM/USDC', 'MATIC/USDC',
            'ALGO/USDC', 'FTM/USDC', 'LTC/USDC', 'BCH/USDC', 'NEAR/USDC', 'SAND/USDC',
            'DOGE/USDC', 'TRX/USDC', 'APT/USDC', 'SUI/USDC'  # New pairs added
        ]

        self.conditions_data = {}
        self.last_update = None
        self.current_strategy = "NFI5MOHO_WIP"  # Default strategy
        self.bot_status = {}

        logger.info(f"Strategy Monitor initialized with {len(self.pairs)} pairs")

    def get_freqtrade_data(self, endpoint):
        """Get data from Freqtrade API"""
        try:
            response = requests.get(
                f"{self.freqtrade_api}/api/v1/{endpoint}",
                auth=self.auth,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"API request failed: {response.status_code}")
                return None
        except Exception as e:
            logger.debug(f"API not available for {endpoint}: {e}")
            return None

    def get_mock_data_for_pair(self, pair):
        """Generate mock data when API is not available"""
        return {
            'pair': pair,
            'current_price': round(random.uniform(0.1, 100), 4),
            'rsi': round(random.uniform(20, 80), 1),
            'rsi_fast': round(random.uniform(15, 85), 1),
            'sma15': round(random.uniform(0.1, 100), 4),
            'cti': round(random.uniform(-1, 1), 3),
            'conditions': {
                'rsi_slow_declining': random.choice([True, False]),
                'rsi_fast_low': random.choice([True, False]),
                'rsi_above_24': random.choice([True, False]),
                'price_below_sma': random.choice([True, False]),
                'cti_low': random.choice([True, False])
            },
            'met_count': random.randint(0, 5),
            'ready_to_trade': False,
            'last_update': datetime.now().strftime('%H:%M:%S')
        }

    def calculate_indicators(self, df):
        """Calculate technical indicators"""
        try:
            # RSI calculation
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))

            # RSI Fast (7 periods)
            gain_fast = (delta.where(delta > 0, 0)).rolling(window=7).mean()
            loss_fast = (-delta.where(delta < 0, 0)).rolling(window=7).mean()
            rs_fast = gain_fast / loss_fast
            df['rsi_fast'] = 100 - (100 / (1 + rs_fast))

            # SMA15
            df['sma15'] = df['close'].rolling(window=15).mean()

            # CTI (Correlation Trend Indicator)
            df['cti'] = df['close'].rolling(window=20).corr(pd.Series(range(20)))

            return df
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return df

    def check_strategy_conditions(self, pair):
        """Check NFI5MOHO_WIP strategy conditions"""
        try:
            # Get candle data
            candles_data = self.get_freqtrade_data(f"pair_candles?pair={pair}&timeframe=5m&limit=100")
            if not candles_data or 'data' not in candles_data:
                return None

            # Convert to DataFrame
            candles = candles_data['data']
            if not candles or len(candles) < 30:
                return None

            # Take only the first 6 columns (timestamp, open, high, low, close, volume)
            df = pd.DataFrame(candles)
            if df.empty or len(df.columns) < 6:
                return None

            df = df.iloc[:, :6]  # Keep only first 6 columns
            df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df['open'] = pd.to_numeric(df['open'], errors='coerce')
            df['high'] = pd.to_numeric(df['high'], errors='coerce')
            df['low'] = pd.to_numeric(df['low'], errors='coerce')

            # Remove rows with NaN values
            df = df.dropna()

            # Calculate indicators
            df = self.calculate_indicators(df)

            if len(df) < 30:
                return None

            # Get latest values
            latest = df.iloc[-1]
            prev = df.iloc[-2]

            current_price = latest['close']
            rsi = latest['rsi']
            rsi_fast = latest['rsi_fast']
            sma15 = latest['sma15']
            cti = latest['cti']

            # NFI5MOHO_WIP Strategy Conditions (based on hyperopt results)
            conditions = {
                'rsi_slow_declining': prev['rsi'] > latest['rsi'],
                'rsi_fast_low': rsi_fast < 35,  # From hyperopt: buy_rsi_fast threshold
                'rsi_above_24': rsi > 24,       # From hyperopt: buy_rsi threshold
                'price_below_sma': current_price < (sma15 * 0.98),  # From hyperopt: SMA offset
                'cti_low': cti < 0.75           # From hyperopt: CTI threshold
            }

            # Count met conditions
            met_count = sum(conditions.values())

            return {
                'pair': pair,
                'current_price': current_price,
                'rsi': rsi,
                'rsi_fast': rsi_fast,
                'sma15': sma15,
                'cti': cti,
                'conditions': conditions,
                'met_count': met_count,
                'ready_to_trade': met_count >= 5,
                'last_update': datetime.now().strftime('%H:%M:%S')
            }

        except Exception as e:
            logger.error(f"Error checking conditions for {pair}: {e}")
            return None

    def update_conditions(self):
        """Update conditions for all pairs"""
        try:
            new_data = {}
            api_available = False

            # Test API availability
            test_response = self.get_freqtrade_data("status")
            if test_response is not None:
                api_available = True
                logger.info("API is available - using real data")
            else:
                logger.warning("API not available - using mock data for demonstration")

            for pair in self.pairs:
                if api_available:
                    result = self.check_strategy_conditions(pair)
                    if result:
                        new_data[pair] = result
                else:
                    # Use mock data when API is not available
                    mock_data = self.get_mock_data_for_pair(pair)
                    new_data[pair] = mock_data

                time.sleep(0.05)  # Faster rate limiting

            self.conditions_data = new_data
            self.last_update = datetime.now()

            # Log summary
            ready_pairs = [p for p, data in new_data.items() if data['met_count'] >= 5]
            close_pairs = [p for p, data in new_data.items() if data['met_count'] == 4]

            status = "LIVE DATA" if api_available else "DEMO MODE"
            logger.info(f"Updated {len(new_data)} pairs ({status}) - Ready: {len(ready_pairs)}, Close: {len(close_pairs)}")

        except Exception as e:
            logger.error(f"Error updating conditions: {e}")

    def run_monitor(self):
        """Run continuous monitoring"""
        while True:
            try:
                self.update_conditions()
                time.sleep(10)  # Update every 10 seconds
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(30)

    def get_current_strategy_info(self):
        """Get current strategy and bot information from API"""
        try:
            # Check if bot is running by trying to get config
            config_data = self.get_freqtrade_data("show_config")
            bot_running = config_data is not None

            if bot_running:
                self.current_strategy = config_data.get('strategy', 'NFI5MOHO_WIP')
            else:
                self.current_strategy = "NFI5MOHO_WIP"

            # Get open trades count
            status_data = self.get_freqtrade_data("status")
            open_trades = len(status_data) if status_data else 0

            return {
                'strategy': self.current_strategy,
                'bot_running': bot_running,
                'open_trades': open_trades
            }
        except Exception as e:
            logger.warning(f"Could not get strategy info: {e}")
            return {
                'strategy': self.current_strategy,
                'bot_running': False,
                'open_trades': 0
            }

# Flask routes
@app.route('/')
def dashboard():
    """Main dashboard"""

    # Get current strategy info
    strategy_info = monitor.get_current_strategy_info()

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ strategy_name }} Strategy Monitor - Real-time Analysis</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .container { max-width: 1400px; margin: 0 auto; }
            .header { text-align: center; color: white; margin-bottom: 30px; }
            .bot-status { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
            .status-online { color: #10b981; }
            .status-offline { color: #ef4444; }
            .stats { display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; }
            .stat-card { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; color: white; text-align: center; }
            .pairs-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }
            .pair-card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .pair-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
            .pair-name { font-size: 18px; font-weight: bold; }
            .score { padding: 5px 10px; border-radius: 20px; color: white; font-weight: bold; }
            .score-5 { background: #10b981; }
            .score-4 { background: #f59e0b; }
            .score-3 { background: #ef4444; }
            .score-2 { background: #ef4444; }
            .score-1 { background: #ef4444; }
            .score-0 { background: #6b7280; }
            .conditions { margin-top: 10px; }
            .condition { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #f3f4f6; }
            .condition:last-child { border-bottom: none; }
            .status { font-weight: bold; }
            .status.met { color: #10b981; }
            .status.not-met { color: #ef4444; }
            .price { font-size: 14px; color: #6b7280; margin-top: 10px; }
            .last-update { text-align: center; color: white; margin-top: 30px; }
        </style>
        <script>
            function refreshData() {
                location.reload();
            }
            setInterval(refreshData, 5000);
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 {{ strategy_name }} Strategy Monitor</h1>
                <h2>{{ total_pairs }} Trading Pairs - Real-time Analysis</h2>
            </div>

            <div class="bot-status">
                <h3>Bot Status:
                    <span class="{{ 'status-online' if bot_running else 'status-offline' }}">
                        {{ '🟢 ONLINE' if bot_running else '🔴 OFFLINE' }}
                    </span>
                </h3>
                <p>Open Trades: {{ open_trades }} | Strategy: {{ strategy_name }}</p>
                {% if not bot_running %}
                <p style="color: #FF9800;">⚠️ Running in DEMO MODE - Start FreqTrade bot for live data</p>
                {% endif %}
            </div>

            <div class="stats">
                <div class="stat-card">
                    <h3>Ready to Trade</h3>
                    <div style="font-size: 24px;">{{ ready_count }}</div>
                </div>
                <div class="stat-card">
                    <h3>Close (4/5)</h3>
                    <div style="font-size: 24px;">{{ close_count }}</div>
                </div>
                <div class="stat-card">
                    <h3>Total Pairs</h3>
                    <div style="font-size: 24px;">{{ total_pairs }}</div>
                </div>
            </div>

            <div class="pairs-grid">
                {% for pair_data in pairs_data %}
                <div class="pair-card">
                    <div class="pair-header">
                        <div class="pair-name">{{ pair_data.pair }}</div>
                        <div class="score score-{{ pair_data.met_count }}">{{ pair_data.met_count }}/5</div>
                    </div>

                    <div class="conditions">
                        <div class="condition">
                            <span>RSI Slow Declining</span>
                            <span class="status {{ 'met' if pair_data.conditions.rsi_slow_declining else 'not-met' }}">
                                {{ '✅' if pair_data.conditions.rsi_slow_declining else '❌' }}
                            </span>
                        </div>
                        <div class="condition">
                            <span>RSI Fast < 35</span>
                            <span class="status {{ 'met' if pair_data.conditions.rsi_fast_low else 'not-met' }}">
                                {{ '✅' if pair_data.conditions.rsi_fast_low else '❌' }}
                            </span>
                        </div>
                        <div class="condition">
                            <span>RSI > 24</span>
                            <span class="status {{ 'met' if pair_data.conditions.rsi_above_24 else 'not-met' }}">
                                {{ '✅' if pair_data.conditions.rsi_above_24 else '❌' }}
                            </span>
                        </div>
                        <div class="condition">
                            <span>Price < SMA15×0.98</span>
                            <span class="status {{ 'met' if pair_data.conditions.price_below_sma else 'not-met' }}">
                                {{ '✅' if pair_data.conditions.price_below_sma else '❌' }}
                            </span>
                        </div>
                        <div class="condition">
                            <span>CTI < 0.75</span>
                            <span class="status {{ 'met' if pair_data.conditions.cti_low else 'not-met' }}">
                                {{ '✅' if pair_data.conditions.cti_low else '❌' }}
                            </span>
                        </div>
                    </div>

                    <div class="price">
                        Price: ${{ "%.4f"|format(pair_data.current_price) }}
                    </div>
                </div>
                {% endfor %}
            </div>

            <div class="last-update">
                Last Update: {{ last_update }}
            </div>
        </div>
    </body>
    </html>
    """

    if not monitor.conditions_data:
        return "Loading data..."

    pairs_data = list(monitor.conditions_data.values())
    pairs_data.sort(key=lambda x: x['met_count'], reverse=True)

    ready_count = len([p for p in pairs_data if p['met_count'] >= 5])
    close_count = len([p for p in pairs_data if p['met_count'] == 4])

    return render_template_string(
        html_template,
        pairs_data=pairs_data,
        ready_count=ready_count,
        close_count=close_count,
        total_pairs=len(pairs_data),
        last_update=monitor.last_update.strftime('%Y-%m-%d %H:%M:%S') if monitor.last_update else 'Never',
        strategy_name=strategy_info['strategy'],
        bot_running=strategy_info['bot_running'],
        open_trades=strategy_info['open_trades']
    )

@app.route('/api/conditions')
def api_conditions():
    """API endpoint for conditions data"""
    return jsonify(monitor.conditions_data)

@app.route('/api/pairs')
def api_pairs():
    """API endpoint for pairs list"""
    return jsonify({'pairs': monitor.pairs, 'count': len(monitor.pairs)})

# Global monitor instance
monitor = StrategyMonitor()

def main():
    """Main function"""
    try:
        logger.info("Starting Strategy Monitor...")

        # Start monitoring thread
        monitor_thread = Thread(target=monitor.run_monitor, daemon=True)
        monitor_thread.start()

        # Start Flask app
        app.run(host='0.0.0.0', port=8504, debug=False)

    except KeyboardInterrupt:
        logger.info("Strategy Monitor stopped by user")
    except Exception as e:
        logger.error(f"Strategy Monitor error: {e}")

if __name__ == "__main__":
    main()