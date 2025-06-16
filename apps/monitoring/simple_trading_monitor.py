#!/usr/bin/env python3
"""
Simple Trading Monitor - Εικονικό σύστημα παρακολούθησης συναλλαγών
Δημιουργεί εικονικές συναλλαγές και τις εμφανίζει σε web interface
"""

import json
import time
import random
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify
import sqlite3
from pathlib import Path

class SimpleTradingMonitor:
    def __init__(self):
        self.db_path = "simple_trades.sqlite"
        self.running = False
        self.balance = 1000.0  # Starting balance in USDC
        self.open_trades = {}
        self.closed_trades = []
        self.trade_id_counter = 1

        # Trading pairs to simulate
        self.pairs = ["BTC/USDC", "ETH/USDC", "BNB/USDC", "ADA/USDC", "SOL/USDC"]

        # Initialize database
        self.init_database()

    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY,
                pair TEXT,
                amount REAL,
                entry_price REAL,
                current_price REAL,
                profit_usdt REAL,
                status TEXT,
                open_time TEXT,
                close_time TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def get_random_price(self, pair: str) -> float:
        """Get simulated price for a trading pair"""
        base_prices = {
            "BTC/USDC": 45000,
            "ETH/USDC": 2800,
            "BNB/USDC": 320,
            "ADA/USDC": 0.45,
            "SOL/USDC": 95
        }

        base_price = base_prices.get(pair, 100)
        # Add random variation ±3%
        variation = random.uniform(-0.03, 0.03)
        return round(base_price * (1 + variation), 6)

    def create_trade(self):
        """Create a new simulated trade"""
        if len(self.open_trades) >= 3:  # Max 3 open trades
            return

        pair = random.choice(self.pairs)
        entry_price = self.get_random_price(pair)
        amount = round(random.uniform(0.001, 0.01), 6)

        trade = {
            'id': self.trade_id_counter,
            'pair': pair,
            'amount': amount,
            'entry_price': entry_price,
            'current_price': entry_price,
            'profit_usdt': 0.0,
            'status': 'open',
            'open_time': datetime.now().isoformat(),
            'close_time': None
        }

        self.open_trades[self.trade_id_counter] = trade
        self.trade_id_counter += 1

        # Save to database
        self.save_trade_to_db(trade)

        print(f"📈 New trade: {pair} - {amount} @ {entry_price} USDC")

    def update_trade_prices(self):
        """Update current prices for open trades"""
        for trade_id, trade in self.open_trades.items():
            new_price = self.get_random_price(trade['pair'])
            trade['current_price'] = new_price

            # Calculate profit
            profit_pct = (new_price - trade['entry_price']) / trade['entry_price']
            trade['profit_usdt'] = round(trade['amount'] * trade['entry_price'] * profit_pct, 2)

    def close_trade(self, trade_id: int):
        """Close an open trade"""
        if trade_id not in self.open_trades:
            return

        trade = self.open_trades[trade_id]
        trade['status'] = 'closed'
        trade['close_time'] = datetime.now().isoformat()

        # Move to closed trades
        self.closed_trades.append(trade.copy())
        del self.open_trades[trade_id]

        # Update database
        self.update_trade_in_db(trade)

        status = "🟢 PROFIT" if trade['profit_usdt'] > 0 else "🔴 LOSS"
        print(f"{status}: {trade['pair']} closed - {trade['profit_usdt']:+.2f} USDC")

    def save_trade_to_db(self, trade):
        """Save trade to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO trades
            (id, pair, amount, entry_price, current_price, profit_usdt, status, open_time, close_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade['id'], trade['pair'], trade['amount'], trade['entry_price'],
            trade['current_price'], trade['profit_usdt'], trade['status'],
            trade['open_time'], trade['close_time']
        ))

        conn.commit()
        conn.close()

    def update_trade_in_db(self, trade):
        """Update trade in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE trades SET current_price=?, profit_usdt=?, status=?, close_time=?
            WHERE id=?
        ''', (trade['current_price'], trade['profit_usdt'], trade['status'],
              trade['close_time'], trade['id']))

        conn.commit()
        conn.close()

    def get_open_trades(self):
        """Get list of open trades"""
        return list(self.open_trades.values())

    def get_recent_trades(self, limit=10):
        """Get recent closed trades"""
        return self.closed_trades[-limit:] if self.closed_trades else []

    def get_profit_summary(self):
        """Get profit summary"""
        total_profit = sum(trade['profit_usdt'] for trade in self.closed_trades)
        winning_trades = len([t for t in self.closed_trades if t['profit_usdt'] > 0])
        losing_trades = len([t for t in self.closed_trades if t['profit_usdt'] < 0])

        return {
            'total_profit_usdt': round(total_profit, 2),
            'total_trades': len(self.closed_trades),
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': round(winning_trades / max(len(self.closed_trades), 1) * 100, 1),
            'current_balance': round(self.balance + total_profit, 2)
        }

    def trading_loop(self):
        """Main trading simulation loop"""
        print("🚀 Simple Trading Monitor Started!")
        print("💰 Starting balance: 1000 USDC")

        while self.running:
            try:
                # Update prices for open trades
                self.update_trade_prices()

                # Random actions
                action = random.choice(['create', 'close', 'wait'])

                if action == 'create' and random.random() < 0.2:  # 20% chance
                    self.create_trade()
                elif action == 'close' and self.open_trades and random.random() < 0.3:  # 30% chance
                    trade_id = random.choice(list(self.open_trades.keys()))
                    self.close_trade(trade_id)

                # Auto-close old trades
                for trade_id, trade in list(self.open_trades.items()):
                    open_time = datetime.fromisoformat(trade['open_time'])
                    if datetime.now() - open_time > timedelta(minutes=random.randint(2, 10)):
                        self.close_trade(trade_id)

                time.sleep(random.randint(5, 15))  # Wait 5-15 seconds

            except Exception as e:
                print(f"❌ Error in trading loop: {e}")
                time.sleep(5)

    def start(self):
        """Start the trading simulation"""
        if self.running:
            return

        self.running = True
        self.trading_thread = threading.Thread(target=self.trading_loop, daemon=True)
        self.trading_thread.start()

    def stop(self):
        """Stop the trading simulation"""
        self.running = False
        if hasattr(self, 'trading_thread'):
            self.trading_thread.join(timeout=5)

# Flask Web App
app = Flask(__name__)
monitor = SimpleTradingMonitor()

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="el">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Simple Trading Monitor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .demo-notice {
            background: linear-gradient(45deg, #ff9a9e 0%, #fecfef 100%);
            color: #333;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
            font-weight: bold;
        }

        .status-bar {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            text-align: center;
        }

        .status-item {
            padding: 15px;
            border-radius: 10px;
            color: white;
        }

        .status-item.balance {
            background: linear-gradient(45deg, #43e97b 0%, #38f9d7 100%);
        }

        .status-item.trades {
            background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
        }

        .status-item.profit {
            background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
        }

        .status-item h3 {
            font-size: 0.9em;
            margin-bottom: 5px;
            opacity: 0.9;
        }

        .status-item .value {
            font-size: 1.8em;
            font-weight: bold;
        }

        .section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .section h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }

        .trades-grid {
            display: grid;
            gap: 15px;
        }

        .trade-card {
            background: linear-gradient(45deg, #f8f9fa, #e9ecef);
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #667eea;
            transition: transform 0.2s;
        }

        .trade-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        .trade-card.profit {
            border-left-color: #28a745;
            background: linear-gradient(45deg, #d4edda, #c3e6cb);
        }

        .trade-card.loss {
            border-left-color: #dc3545;
            background: linear-gradient(45deg, #f8d7da, #f5c6cb);
        }

        .trade-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .trade-pair {
            font-weight: bold;
            font-size: 1.1em;
            color: #333;
        }

        .trade-profit {
            font-weight: bold;
            font-size: 1.1em;
        }

        .trade-profit.positive { color: #28a745; }
        .trade-profit.negative { color: #dc3545; }

        .trade-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
            font-size: 0.9em;
            color: #666;
        }

        .no-trades {
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 40px;
        }

        .refresh-info {
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 20px;
            font-size: 0.9em;
        }

        @media (max-width: 768px) {
            .container { padding: 10px; }
            .header h1 { font-size: 2em; }
            .status-grid { grid-template-columns: repeat(2, 1fr); }
            .trade-details { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Simple Trading Monitor</h1>
            <p>Εικονικό Σύστημα Παρακολούθησης Συναλλαγών</p>
        </div>

        <div class="demo-notice">
            ⚠️ DEMO MODE: Εικονικές συναλλαγές - Χωρίς πραγματικά χρήματα!
        </div>

        <div class="status-bar">
            <div class="status-grid">
                <div class="status-item balance">
                    <h3>Υπόλοιπο</h3>
                    <div class="value" id="balance">1000.00 USDC</div>
                </div>
                <div class="status-item trades">
                    <h3>Ανοιχτές Θέσεις</h3>
                    <div class="value" id="open-trades">0</div>
                </div>
                <div class="status-item profit">
                    <h3>Συνολικό Κέρδος</h3>
                    <div class="value" id="total-profit">+0.00 USDC</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📈 Ανοιχτές Θέσεις</h2>
            <div id="open-trades-list" class="trades-grid">
                <div class="no-trades">Δεν υπάρχουν ανοιχτές θέσεις</div>
            </div>
        </div>

        <div class="section">
            <h2>📊 Πρόσφατες Συναλλαγές</h2>
            <div id="recent-trades-list" class="trades-grid">
                <div class="no-trades">Δεν υπάρχουν πρόσφατες συναλλαγές</div>
            </div>
        </div>

        <div class="refresh-info">
            🔄 Αυτόματη ανανέωση κάθε 5 δευτερόλεπτα
        </div>
    </div>

    <script>
        function formatTime(isoString) {
            const date = new Date(isoString);
            return date.toLocaleTimeString('el-GR');
        }

        function formatProfit(profit) {
            const sign = profit >= 0 ? '+' : '';
            return `${sign}${profit.toFixed(2)} USDC`;
        }

        function createTradeCard(trade, isOpen = false) {
            const profitClass = isOpen ? (trade.profit_usdt >= 0 ? 'profit' : 'loss') : (trade.profit_usdt >= 0 ? 'profit' : 'loss');
            const profitText = formatProfit(trade.profit_usdt);
            const profitColorClass = trade.profit_usdt >= 0 ? 'positive' : 'negative';

            return `
                <div class="trade-card ${profitClass}">
                    <div class="trade-header">
                        <span class="trade-pair">${trade.pair}</span>
                        <span class="trade-profit ${profitColorClass}">${profitText}</span>
                    </div>
                    <div class="trade-details">
                        <div><strong>Ποσότητα:</strong> ${trade.amount}</div>
                        <div><strong>Τιμή Εισόδου:</strong> ${trade.entry_price} USDC</div>
                        <div><strong>Τρέχουσα Τιμή:</strong> ${trade.current_price} USDC</div>
                        <div><strong>Ώρα:</strong> ${formatTime(trade.open_time)}</div>
                        ${!isOpen && trade.close_time ? `<div><strong>Κλείσιμο:</strong> ${formatTime(trade.close_time)}</div>` : ''}
                    </div>
                </div>
            `;
        }

        function updateDashboard() {
            // Update open trades
            fetch('/api/open_trades')
                .then(response => response.json())
                .then(trades => {
                    const container = document.getElementById('open-trades-list');
                    if (trades.length === 0) {
                        container.innerHTML = '<div class="no-trades">Δεν υπάρχουν ανοιχτές θέσεις</div>';
                    } else {
                        container.innerHTML = trades.map(trade => createTradeCard(trade, true)).join('');
                    }

                    // Update open trades count
                    document.getElementById('open-trades').textContent = trades.length;
                })
                .catch(error => console.error('Error updating open trades:', error));

            // Update recent trades
            fetch('/api/recent_trades')
                .then(response => response.json())
                .then(trades => {
                    const container = document.getElementById('recent-trades-list');
                    if (trades.length === 0) {
                        container.innerHTML = '<div class="no-trades">Δεν υπάρχουν πρόσφατες συναλλαγές</div>';
                    } else {
                        container.innerHTML = trades.map(trade => createTradeCard(trade, false)).join('');
                    }
                })
                .catch(error => console.error('Error updating recent trades:', error));

            // Update profit summary
            fetch('/api/profit_summary')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('balance').textContent = `${data.current_balance.toFixed(2)} USDC`;
                    document.getElementById('total-profit').textContent = formatProfit(data.total_profit_usdt);
                })
                .catch(error => console.error('Error updating profit summary:', error));
        }

        // Initial load
        updateDashboard();

        // Auto refresh every 5 seconds
        setInterval(updateDashboard, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/open_trades')
def api_open_trades():
    return jsonify(monitor.get_open_trades())

@app.route('/api/recent_trades')
def api_recent_trades():
    return jsonify(monitor.get_recent_trades())

@app.route('/api/profit_summary')
def api_profit_summary():
    return jsonify(monitor.get_profit_summary())

if __name__ == '__main__':
    print("🚀 Starting Simple Trading Monitor...")

    # Start trading simulation
    monitor.start()

    print("📊 Trading simulation started!")
    print("🌐 Starting web server on http://localhost:8080")
    print("🎯 Open your browser and go to: http://localhost:8080")
    print("⚠️  This is DEMO mode - no real money involved!")

    try:
        app.run(host='0.0.0.0', port=8080, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Stopping trading monitor...")
        monitor.stop()
        print("✅ Trading monitor stopped!")