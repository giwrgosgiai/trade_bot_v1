#!/usr/bin/env python3
"""
🚀 TradingView Pro Style UI - Advanced Trading Monitor
€500 Budget | Real Trading Simulation | Professional Analytics
"""

import requests
import time
import os
import logging
import json
import random
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import threading

# Configure logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('flask').setLevel(logging.ERROR)

app = Flask(__name__)
CORS(app)
app.logger.disabled = True

# === CONFIGURATION ===
INITIAL_BUDGET = 500.0  # €500 starting budget
FREQTRADE_API_URL = "http://127.0.0.1:8080"
DATA_FILE = "trading_data_persistent.json"

# === GLOBAL DATA ===
STRATEGIES = {
    'UltimateProfitStrategy': {
        'name': 'MEGA Strategy',
        'budget': 500.0,
        'current_balance': 500.0,
        'trades': [],
        'open_positions': [],
        'performance': {'total_profit': 0, 'win_rate': 0, 'trade_count': 0, 'best_trade': 0, 'worst_trade': 0, 'avg_trade': 0, 'profit_factor': 0, 'sharpe_ratio': 0, 'max_drawdown': 0},
        'active': True,
        'description': 'AI-powered strategy with smart money flow detection',
        'timeframe': '5m',
        'pairs': ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'DOT/USDT', 'LINK/USDT', 'BNB/USDT', 'XRP/USDT', 'SOL/USDT', 'MATIC/USDT', 'AVAX/USDT', 'UNI/USDT', 'ATOM/USDT']
    }
}

CURRENT_PRICES = {}
MARKET_CONDITIONS = {}
BOT_THINKING = []
SYSTEM_STATUS = {'last_update': None, 'api_connected': False, 'trades_today': 0, 'uptime': datetime.now()}
PRICE_HISTORY = {}  # For charts

def save_data():
    """Save all data with enhanced metrics"""
    try:
        data = {
            'strategies': STRATEGIES,
            'current_prices': CURRENT_PRICES,
            'market_conditions': MARKET_CONDITIONS,
            'bot_thinking': BOT_THINKING[-100:],  # Keep last 100 thoughts
            'system_status': SYSTEM_STATUS,
            'price_history': PRICE_HISTORY,
            'last_saved': datetime.now().isoformat()
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"💾 Data saved: {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"❌ Save error: {e}")

def load_data():
    """Load data from previous session"""
    global STRATEGIES, CURRENT_PRICES, MARKET_CONDITIONS, BOT_THINKING, SYSTEM_STATUS, PRICE_HISTORY

    if not os.path.exists(DATA_FILE):
        print("📊 Fresh start - no previous data found")
        return

    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)

        STRATEGIES = data.get('strategies', STRATEGIES)
        CURRENT_PRICES = data.get('current_prices', {})
        MARKET_CONDITIONS = data.get('market_conditions', {})
        BOT_THINKING = data.get('bot_thinking', [])
        SYSTEM_STATUS = data.get('system_status', SYSTEM_STATUS)
        PRICE_HISTORY = data.get('price_history', {})

        print(f"📈 Data loaded from: {data.get('last_saved', 'unknown time')}")

        # Calculate enhanced performance metrics
        for strategy_name, strategy in STRATEGIES.items():
            calculate_advanced_metrics(strategy)
            balance = strategy['current_balance']
            profit = balance - strategy['budget']
            trades = len(strategy['trades'])
            win_rate = strategy['performance']['win_rate']
            print(f"💰 {strategy['name']}: €{balance:.2f} ({profit:+.2f}€) - {trades} trades - {win_rate:.1f}% win rate")

    except Exception as e:
        print(f"❌ Load error: {e}")

def calculate_advanced_metrics(strategy):
    """Calculate advanced trading metrics like TradingView"""
    trades = strategy['trades']
    if not trades:
        return

    profits = [t['profit_loss'] for t in trades]
    winning_trades = [p for p in profits if p > 0]
    losing_trades = [p for p in profits if p < 0]

    # Basic metrics
    strategy['performance']['best_trade'] = max(profits) if profits else 0
    strategy['performance']['worst_trade'] = min(profits) if profits else 0
    strategy['performance']['avg_trade'] = sum(profits) / len(profits) if profits else 0

    # Profit factor
    gross_profit = sum(winning_trades) if winning_trades else 0
    gross_loss = abs(sum(losing_trades)) if losing_trades else 1
    strategy['performance']['profit_factor'] = gross_profit / gross_loss if gross_loss > 0 else 0

    # Max drawdown simulation
    balance_curve = []
    running_balance = strategy['budget']
    for trade in trades:
        running_balance += trade['profit_loss']
        balance_curve.append(running_balance)

    if balance_curve:
        peak = balance_curve[0]
        max_dd = 0
        for balance in balance_curve:
            if balance > peak:
                peak = balance
            drawdown = (peak - balance) / peak * 100
            max_dd = max(max_dd, drawdown)
        strategy['performance']['max_drawdown'] = max_dd

def fetch_live_prices():
    """Fetch live prices from Binance with price history"""
    global CURRENT_PRICES, PRICE_HISTORY
    try:
        pairs = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT', 'BNBUSDT', 'XRPUSDT', 'SOLUSDT', 'MATICUSDT', 'AVAXUSDT', 'UNIUSDT', 'ATOMUSDT']
        url = "https://api.binance.com/api/v3/ticker/price"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            current_time = datetime.now().isoformat()

            for item in data:
                if item['symbol'] in pairs:
                    pair_name = item['symbol'].replace('USDT', '/USDT')
                    price = float(item['price'])
                    CURRENT_PRICES[pair_name] = price

                    # Store price history for charts
                    if pair_name not in PRICE_HISTORY:
                        PRICE_HISTORY[pair_name] = []

                    PRICE_HISTORY[pair_name].append({
                        'time': current_time,
                        'price': price
                    })

                    # Keep only last 100 price points
                    PRICE_HISTORY[pair_name] = PRICE_HISTORY[pair_name][-100:]

            SYSTEM_STATUS['last_update'] = current_time
            print(f"🔄 Prices updated: {len(CURRENT_PRICES)} pairs")
            return True
    except Exception as e:
        print(f"❌ Price fetch error: {e}")
        return False

def analyze_market_conditions():
    """Advanced market analysis like TradingView"""
    global MARKET_CONDITIONS

    for pair, price in CURRENT_PRICES.items():
        # Advanced technical indicators simulation
        rsi = random.uniform(25, 75)
        macd = random.uniform(-2, 2)
        bb_position = random.uniform(0, 1)  # Bollinger Bands position
        volume_ratio = random.uniform(0.3, 5.0)
        trend_strength = random.randint(1, 10)
        volatility = random.uniform(0.2, 8.0)
        momentum = random.uniform(-5, 5)

        # Support/Resistance levels
        support = price * random.uniform(0.95, 0.99)
        resistance = price * random.uniform(1.01, 1.05)

        # Market sentiment
        sentiment_score = random.uniform(-1, 1)

        # Entry conditions (more sophisticated)
        entry_conditions = {
            'rsi_optimal': 30 <= rsi <= 70,
            'macd_bullish': macd > 0,
            'volume_strong': volume_ratio >= 1.2,
            'trend_positive': trend_strength >= 5,
            'volatility_normal': volatility <= 4.0,
            'momentum_positive': momentum > 0,
            'above_support': price > support,
            'sentiment_positive': sentiment_score > 0
        }

        # Exit conditions
        exit_conditions = {
            'rsi_extreme': rsi > 75 or rsi < 25,
            'macd_bearish': macd < -0.5,
            'volume_weak': volume_ratio < 0.6,
            'trend_negative': trend_strength <= 3,
            'high_volatility': volatility > 6.0,
            'momentum_negative': momentum < -2,
            'near_resistance': price >= resistance * 0.99,
            'sentiment_negative': sentiment_score < -0.3
        }

        entry_score = sum(entry_conditions.values())
        exit_score = sum(exit_conditions.values())

        # Price change calculation
        price_change_24h = random.uniform(-5, 5)  # Simulate 24h change

        MARKET_CONDITIONS[pair] = {
            'price': price,
            'price_change_24h': price_change_24h,
            'rsi': round(rsi, 1),
            'macd': round(macd, 3),
            'bb_position': round(bb_position, 2),
            'volume_ratio': round(volume_ratio, 2),
            'trend_strength': trend_strength,
            'volatility': round(volatility, 2),
            'momentum': round(momentum, 2),
            'support': round(support, 4),
            'resistance': round(resistance, 4),
            'sentiment_score': round(sentiment_score, 2),
            'entry_score': entry_score,
            'exit_score': exit_score,
            'entry_ready': entry_score >= 5,
            'exit_ready': exit_score >= 4,
            'conditions': entry_conditions,
            'exit_conditions': exit_conditions,
            'signal': 'BUY' if entry_score >= 6 else 'SELL' if exit_score >= 5 else 'HOLD'
        }

def bot_thinking_process():
    """Enhanced bot thinking with professional analysis"""
    global BOT_THINKING

    current_time = datetime.now().strftime('%H:%M:%S')

    for pair, conditions in MARKET_CONDITIONS.items():
        pair_name = pair.replace('/USDT', '')

        # Professional analysis explanations
        if conditions['entry_ready']:
            analysis_details = []
            if conditions['conditions']['rsi_optimal']:
                analysis_details.append(f"RSI {conditions['rsi']} in optimal range")
            if conditions['conditions']['macd_bullish']:
                analysis_details.append(f"MACD bullish at {conditions['macd']}")
            if conditions['conditions']['volume_strong']:
                analysis_details.append(f"Strong volume {conditions['volume_ratio']}x")
            if conditions['conditions']['trend_positive']:
                analysis_details.append(f"Trend strength {conditions['trend_strength']}/10")

            thinking = {
                'time': current_time,
                'pair': pair_name,
                'action': 'ANALYZING BUY SIGNAL',
                'signal': 'BUY',
                'confidence': f"{conditions['entry_score']}/8",
                'price': f"${conditions['price']:.4f}",
                'analysis': " | ".join(analysis_details[:3]),
                'support_resistance': f"S: ${conditions['support']:.4f} | R: ${conditions['resistance']:.4f}",
                'color': '#26A69A',
                'simple_explanation': f"{pair_name} shows strong bullish signals with {conditions['entry_score']}/8 conditions met"
            }
            BOT_THINKING.append(thinking)

            # Execute trade
            simulate_trade_entry(pair, conditions)

        elif conditions['exit_ready']:
            analysis_details = []
            if conditions['exit_conditions']['rsi_extreme']:
                analysis_details.append(f"RSI extreme at {conditions['rsi']}")
            if conditions['exit_conditions']['macd_bearish']:
                analysis_details.append(f"MACD bearish {conditions['macd']}")
            if conditions['exit_conditions']['volume_weak']:
                analysis_details.append(f"Weak volume {conditions['volume_ratio']}x")

            thinking = {
                'time': current_time,
                'pair': pair_name,
                'action': 'ANALYZING SELL SIGNAL',
                'signal': 'SELL',
                'confidence': f"{conditions['exit_score']}/8",
                'price': f"${conditions['price']:.4f}",
                'analysis': " | ".join(analysis_details[:3]),
                'support_resistance': f"S: ${conditions['support']:.4f} | R: ${conditions['resistance']:.4f}",
                'color': '#EF5350',
                'simple_explanation': f"{pair_name} showing exit signals with {conditions['exit_score']}/8 conditions met"
            }
            BOT_THINKING.append(thinking)

            # Execute trade exit
            simulate_trade_exit(pair, conditions)

        else:
            # Market monitoring with professional insights
            if random.random() < 0.05:  # 5% chance for monitoring update
                thinking = {
                    'time': current_time,
                    'pair': pair_name,
                    'action': 'MARKET MONITORING',
                    'signal': conditions['signal'],
                    'confidence': f"{max(conditions['entry_score'], conditions['exit_score'])}/8",
                    'price': f"${conditions['price']:.4f}",
                    'analysis': f"RSI: {conditions['rsi']} | MACD: {conditions['macd']} | Vol: {conditions['volume_ratio']}x",
                    'support_resistance': f"S: ${conditions['support']:.4f} | R: ${conditions['resistance']:.4f}",
                    'color': '#2962FF',
                    'simple_explanation': f"{pair_name} in {conditions['signal']} mode, waiting for stronger signals"
                }
                BOT_THINKING.append(thinking)

    # Keep only last 200 thoughts
    BOT_THINKING = BOT_THINKING[-200:]

def simulate_trade_entry(pair, conditions):
    """Simulate trade entry with realistic execution"""
    strategy = STRATEGIES['UltimateProfitStrategy']

    # Check position limits
    has_position = any(pos['pair'] == pair for pos in strategy['open_positions'])
    if has_position or len(strategy['open_positions']) >= 3:
        return

    # Dynamic position sizing based on volatility and confidence
    base_amount = 50  # Base €50
    confidence_multiplier = conditions['entry_score'] / 8.0
    volatility_adjustment = max(0.5, 1.0 - (conditions['volatility'] / 10.0))

    trade_amount = base_amount * confidence_multiplier * volatility_adjustment
    trade_amount = min(trade_amount, strategy['current_balance'] * 0.25)  # Max 25% per trade

    if trade_amount < 10:  # Minimum €10 per trade
        return

    # Simulate slippage (realistic trading)
    slippage = random.uniform(0.0001, 0.001)  # 0.01% to 0.1% slippage
    entry_price = conditions['price'] * (1 + slippage)

    position = {
        'id': len(strategy['trades']) + len(strategy['open_positions']) + 1,
        'pair': pair,
        'entry_price': entry_price,
        'amount': trade_amount,
        'entry_time': datetime.now().isoformat(),
        'strategy': 'UltimateProfitStrategy',
        'entry_conditions': conditions['entry_score'],
        'stop_loss': entry_price * 0.98,  # 2% stop loss
        'take_profit': entry_price * 1.04  # 4% take profit
    }

    strategy['open_positions'].append(position)
    strategy['current_balance'] -= trade_amount
    SYSTEM_STATUS['trades_today'] = SYSTEM_STATUS.get('trades_today', 0) + 1

    print(f"🟢 BUY: {pair.replace('/USDT', '')} - €{trade_amount:.2f} @ ${entry_price:.4f} (Confidence: {conditions['entry_score']}/8)")

def simulate_trade_exit(pair, conditions):
    """Simulate trade exit with realistic execution"""
    strategy = STRATEGIES['UltimateProfitStrategy']

    # Find open position
    position = None
    for pos in strategy['open_positions']:
        if pos['pair'] == pair:
            position = pos
            break

    if not position:
        return

    # Simulate slippage on exit
    slippage = random.uniform(0.0001, 0.001)
    exit_price = conditions['price'] * (1 - slippage)

    # Calculate profit/loss with fees simulation
    fee_rate = 0.001  # 0.1% fee (like Binance)
    entry_fee = position['amount'] * fee_rate
    exit_fee = position['amount'] * fee_rate

    price_change = (exit_price - position['entry_price']) / position['entry_price']
    gross_profit_loss = position['amount'] * price_change
    net_profit_loss = gross_profit_loss - entry_fee - exit_fee

    exit_value = position['amount'] + net_profit_loss

    # Create detailed trade record with strategy analysis
    entry_strategy = f"RSI:{conditions.get('rsi', 0):.1f} | MACD:{conditions.get('macd', 0):.3f} | Vol:{conditions.get('volume_ratio', 0):.1f}x | Trend:{conditions.get('trend_strength', 0)}/10"
    exit_strategy = f"Exit Score:{conditions['exit_score']}/8 | Volatility:{conditions.get('volatility', 0):.1f}% | Momentum:{conditions.get('momentum', 0):.1f}"

    trade = {
        'id': position['id'],
        'pair': pair,
        'entry_price': position['entry_price'],
        'exit_price': exit_price,
        'amount': position['amount'],
        'profit_loss': net_profit_loss,
        'profit_percent': price_change * 100,
        'entry_time': position['entry_time'],
        'exit_time': datetime.now().isoformat(),
        'strategy': 'UltimateProfitStrategy',
        'entry_conditions': position.get('entry_conditions', 0),
        'exit_conditions': conditions['exit_score'],
        'fees_paid': entry_fee + exit_fee,
        'hold_time_minutes': (datetime.now() - datetime.fromisoformat(position['entry_time'].replace('Z', '+00:00').replace('+00:00', ''))).total_seconds() / 60,
        'entry_strategy': entry_strategy,
        'exit_strategy': exit_strategy,
        'support_level': conditions.get('support', 0),
        'resistance_level': conditions.get('resistance', 0),
        'trade_type': 'SCALP' if trade.get('hold_time_minutes', 0) < 5 else 'SWING'
    }

    strategy['trades'].append(trade)
    strategy['current_balance'] += exit_value
    strategy['open_positions'].remove(position)

    # Update performance metrics
    calculate_advanced_metrics(strategy)

    status = "PROFIT" if net_profit_loss > 0 else "LOSS"
    print(f"🔴 SELL: {pair.replace('/USDT', '')} - {status} €{net_profit_loss:+.2f} ({price_change*100:+.1f}%) - Hold: {trade['hold_time_minutes']:.1f}min")

def update_loop():
    """Main update loop with enhanced monitoring"""
    while True:
        try:
            if fetch_live_prices():
                analyze_market_conditions()
                bot_thinking_process()
                save_data()

            time.sleep(10)  # Update every 10 seconds for more responsive UI
        except Exception as e:
            print(f"❌ Update error: {e}")
            time.sleep(30)

# === API ROUTES ===

@app.route('/')
def dashboard():
    return render_template_string(TRADINGVIEW_PRO_HTML)

@app.route('/api/strategies')
def api_strategies():
    return jsonify(STRATEGIES)

@app.route('/api/market_conditions')
def api_market_conditions():
    return jsonify(MARKET_CONDITIONS)

@app.route('/api/bot_thinking')
def api_bot_thinking():
    return jsonify({
        'thoughts': BOT_THINKING[-30:],  # Last 30 thoughts
        'system_status': SYSTEM_STATUS
    })

@app.route('/api/performance')
def api_performance():
    performance_data = {}
    for name, strategy in STRATEGIES.items():
        performance_data[name] = {
            'name': strategy['name'],
            'budget': strategy['budget'],
            'current_balance': strategy['current_balance'],
            'profit_loss': strategy['current_balance'] - strategy['budget'],
            'profit_percent': ((strategy['current_balance'] - strategy['budget']) / strategy['budget']) * 100,
            'performance': strategy['performance'],
            'open_positions': len(strategy['open_positions']),
            'active': strategy['active'],
            'timeframe': strategy.get('timeframe', '5m'),
            'pairs': strategy.get('pairs', [])
        }
    return jsonify(performance_data)

@app.route('/api/trades/<strategy_name>')
def api_trades(strategy_name):
    if strategy_name in STRATEGIES:
        return jsonify({
            'trades': STRATEGIES[strategy_name]['trades'][-100:],  # Last 100 trades
            'open_positions': STRATEGIES[strategy_name]['open_positions']
        })
    return jsonify({'error': 'Strategy not found'})

@app.route('/api/price_history/<pair>')
def api_price_history(pair):
    """Get price history for charts"""
    pair_formatted = pair.replace('-', '/') + '/USDT' if '/USDT' not in pair else pair
    return jsonify(PRICE_HISTORY.get(pair_formatted, []))

@app.route('/api/system_stats')
def api_system_stats():
    """System statistics for dashboard"""
    uptime = datetime.now() - datetime.fromisoformat(SYSTEM_STATUS['uptime']) if isinstance(SYSTEM_STATUS['uptime'], str) else datetime.now() - SYSTEM_STATUS['uptime']

    return jsonify({
        'uptime_hours': uptime.total_seconds() / 3600,
        'trades_today': SYSTEM_STATUS.get('trades_today', 0),
        'api_connected': SYSTEM_STATUS.get('api_connected', False),
        'last_update': SYSTEM_STATUS.get('last_update'),
        'active_pairs': len(CURRENT_PRICES),
        'total_thoughts': len(BOT_THINKING)
    })

@app.route('/api/live_pnl/<strategy_name>')
def api_live_pnl(strategy_name):
    """Get live P&L for open positions"""
    if strategy_name not in STRATEGIES:
        return jsonify({'error': 'Strategy not found'})

    strategy = STRATEGIES[strategy_name]
    live_pnl = []

    for position in strategy['open_positions']:
        pair = position['pair']
        current_price = CURRENT_PRICES.get(pair, position['entry_price'])

        # Calculate live P&L
        price_change = (current_price - position['entry_price']) / position['entry_price']
        unrealized_pnl = position['amount'] * price_change

        # Calculate fees
        fee_rate = 0.001
        total_fees = position['amount'] * fee_rate * 2  # Entry + Exit fees
        net_unrealized_pnl = unrealized_pnl - total_fees

        live_pnl.append({
            'id': position['id'],
            'pair': pair,
            'entry_price': position['entry_price'],
            'current_price': current_price,
            'amount': position['amount'],
            'unrealized_pnl': net_unrealized_pnl,
            'unrealized_percent': price_change * 100,
            'entry_time': position['entry_time'],
            'hold_time_minutes': (datetime.now() - datetime.fromisoformat(position['entry_time'].replace('Z', '+00:00').replace('+00:00', ''))).total_seconds() / 60,
            'stop_loss': position.get('stop_loss', 0),
            'take_profit': position.get('take_profit', 0)
        })

    return jsonify(live_pnl)

@app.route('/api/trade_analysis/<int:trade_id>')
def api_trade_analysis(trade_id):
    """Get detailed analysis for a specific trade"""
    for strategy in STRATEGIES.values():
        for trade in strategy['trades']:
            if trade['id'] == trade_id:
                return jsonify({
                    'trade': trade,
                    'analysis': {
                        'entry_reason': trade.get('entry_strategy', 'N/A'),
                        'exit_reason': trade.get('exit_strategy', 'N/A'),
                        'support_resistance': f"S: ${trade.get('support_level', 0):.4f} | R: ${trade.get('resistance_level', 0):.4f}",
                        'trade_type': trade.get('trade_type', 'UNKNOWN'),
                        'performance_rating': 'EXCELLENT' if trade['profit_percent'] > 2 else 'GOOD' if trade['profit_percent'] > 0 else 'POOR'
                    }
                })
    return jsonify({'error': 'Trade not found'})

# === TRADINGVIEW PRO STYLE HTML ===
TRADINGVIEW_PRO_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TradingView Pro - Advanced Trading Monitor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0D1421; color: #D1D4DC; overflow: hidden;
        }

        .main-layout {
            display: grid;
            grid-template-areas:
                "header header header"
                "sidebar main-content watchlist"
                "sidebar charts watchlist";
            grid-template-columns: 280px 1fr 300px;
            grid-template-rows: 50px 1fr 1fr;
            height: 100vh; gap: 1px; background: #1E222D;
        }

        /* Header */
        .header {
            grid-area: header; background: #131722; display: flex;
            align-items: center; justify-content: space-between; padding: 0 20px;
            border-bottom: 1px solid #2A2E39;
        }
        .logo { font-size: 1.2em; font-weight: 600; color: #2962FF; }
        .header-stats { display: flex; gap: 20px; font-size: 0.85em; }
        .stat { display: flex; flex-direction: column; align-items: center; }
        .stat-value { font-weight: 600; color: #26A69A; }
        .stat-label { opacity: 0.7; font-size: 0.75em; }

        /* Sidebar */
        .sidebar {
            grid-area: sidebar; background: #131722; padding: 15px;
            border-right: 1px solid #2A2E39; overflow-y: auto;
        }
        .sidebar-section { margin-bottom: 20px; }
        .section-title { font-size: 0.9em; font-weight: 600; margin-bottom: 10px;
                        color: #787B86; text-transform: uppercase; }

        .strategy-card {
            background: #1E222D; padding: 12px; border-radius: 6px; margin-bottom: 8px;
            border-left: 3px solid #26A69A;
        }
        .strategy-name { font-weight: 600; margin-bottom: 5px; }
        .strategy-balance { font-size: 1.1em; font-weight: 700; color: #26A69A; }
        .strategy-metrics { font-size: 0.8em; opacity: 0.8; margin-top: 5px; }

        /* Main Content */
        .main-content {
            grid-area: main-content; background: #0D1421; padding: 15px;
            overflow-y: auto;
        }

        .analysis-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px; margin-bottom: 20px;
        }

        .analysis-card {
            background: #131722; border-radius: 8px; padding: 15px;
            border: 1px solid #2A2E39;
        }
        .card-header {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 12px;
        }
        .pair-name { font-weight: 600; font-size: 1.1em; }
        .price-info { text-align: right; }
        .current-price { font-size: 1.1em; font-weight: 600; }
        .price-change { font-size: 0.85em; }

        .indicators-grid {
            display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
            margin-bottom: 12px; font-size: 0.85em;
        }
        .indicator { display: flex; justify-content: space-between; }

        .signal-section {
            display: flex; justify-content: space-between; align-items: center;
            padding-top: 10px; border-top: 1px solid #2A2E39;
        }
        .signal-badge {
            padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 600;
        }
        .signal-buy { background: #26A69A; color: #000; }
        .signal-sell { background: #EF5350; color: #fff; }
        .signal-hold { background: #2962FF; color: #fff; }

        .confidence-bar {
            width: 60px; height: 6px; background: #2A2E39; border-radius: 3px;
            overflow: hidden;
        }
        .confidence-fill {
            height: 100%; background: #26A69A; transition: width 0.3s;
        }

        /* Charts Area */
        .charts {
            grid-area: charts; background: #131722; padding: 15px;
            border-top: 1px solid #2A2E39;
        }

        /* Watchlist */
        .watchlist {
            grid-area: watchlist; background: #131722; padding: 15px;
            border-left: 1px solid #2A2E39; overflow-y: auto;
        }

        .thinking-feed {
            max-height: 400px; overflow-y: auto;
        }
        .thinking-item {
            background: #1E222D; padding: 10px; border-radius: 6px; margin-bottom: 8px;
            border-left: 3px solid var(--signal-color);
        }
        .thinking-header {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 5px; font-size: 0.85em;
        }
        .thinking-pair { font-weight: 600; }
        .thinking-time { opacity: 0.6; }
        .thinking-action { font-size: 0.8em; margin-bottom: 3px; }
        .thinking-analysis { font-size: 0.75em; opacity: 0.8; }

        .trades-table {
            width: 100%; font-size: 0.8em;
        }
        .trades-table th, .trades-table td {
            padding: 6px; text-align: left; border-bottom: 1px solid #2A2E39;
        }
        .trades-table th { color: #787B86; font-weight: 500; }

        .positive { color: #26A69A; }
        .negative { color: #EF5350; }
        .neutral { color: #2962FF; }

        /* Live Positions Panel */
        .live-positions-panel {
            background: #131722; padding: 15px; border-radius: 8px;
            margin-bottom: 20px; border: 1px solid #2A2E39;
        }
        .positions-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 12px; margin-top: 10px;
        }
        .position-card {
            background: #1E222D; padding: 12px; border-radius: 6px;
            border-left: 4px solid var(--pnl-color);
        }
        .position-header {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 8px;
        }
        .position-pair { font-weight: 600; font-size: 1.1em; }
        .position-pnl { font-weight: 700; font-size: 1.1em; }
        .position-details {
            display: grid; grid-template-columns: 1fr 1fr; gap: 6px;
            font-size: 0.8em; margin-bottom: 8px;
        }
        .position-progress {
            width: 100%; height: 4px; background: #2A2E39; border-radius: 2px;
            overflow: hidden; margin-top: 8px;
        }
        .position-progress-fill {
            height: 100%; transition: width 0.3s;
        }

        /* Trade History */
        .trade-history-feed {
            max-height: 300px; overflow-y: auto;
        }
        .trade-item {
            background: #1E222D; padding: 8px; border-radius: 4px; margin-bottom: 6px;
            border-left: 3px solid var(--trade-color); cursor: pointer;
            transition: background 0.2s;
        }
        .trade-item:hover { background: #252A36; }
        .trade-header {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 4px; font-size: 0.85em;
        }
        .trade-pair { font-weight: 600; }
        .trade-pnl { font-weight: 600; }
        .trade-details { font-size: 0.75em; opacity: 0.8; }
        .trade-strategy { font-size: 0.7em; opacity: 0.6; margin-top: 2px; }

        /* Enhanced Analysis Cards */
        .analysis-card {
            background: linear-gradient(135deg, #131722 0%, #1E222D 100%);
            border-radius: 8px; padding: 15px; border: 1px solid #2A2E39;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .analysis-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        /* Price Chart Mini */
        .price-chart {
            height: 40px; margin: 8px 0; position: relative;
            background: linear-gradient(90deg, transparent 0%, rgba(41, 98, 255, 0.1) 50%, transparent 100%);
            border-radius: 4px; overflow: hidden;
        }
        .price-line {
            position: absolute; bottom: 0; left: 0; right: 0;
            height: 2px; background: #2962FF;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; }
        }

        /* Glowing effects */
        .glow-green { box-shadow: 0 0 10px rgba(38, 166, 154, 0.3); }
        .glow-red { box-shadow: 0 0 10px rgba(239, 83, 80, 0.3); }
        .glow-blue { box-shadow: 0 0 10px rgba(41, 98, 255, 0.3); }

        /* Responsive */
        @media (max-width: 1200px) {
            .main-layout {
                grid-template-areas:
                    "header header"
                    "main-content watchlist";
                grid-template-columns: 1fr 300px;
                grid-template-rows: 50px 1fr;
            }
            .sidebar, .charts { display: none; }
        }

        @media (max-width: 768px) {
            .main-layout {
                grid-template-areas: "header" "main-content";
                grid-template-columns: 1fr;
                grid-template-rows: 50px 1fr;
            }
            .watchlist { display: none; }
        }
    </style>
</head>
<body>
    <div class="main-layout">
        <!-- Header -->
        <div class="header">
            <div class="logo">📈 TradingView Pro</div>
            <div class="header-stats">
                <div class="stat">
                    <div class="stat-value" id="totalBalance">€500.00</div>
                    <div class="stat-label">Balance</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="totalProfit">€0.00</div>
                    <div class="stat-label">P&L</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="winRate">0%</div>
                    <div class="stat-label">Win Rate</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="tradesCount">0</div>
                    <div class="stat-label">Trades</div>
                </div>
            </div>
        </div>

        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-section">
                <div class="section-title">Active Strategies</div>
                <div id="strategiesList">
                    <div style="text-align: center; padding: 20px; opacity: 0.6;">Loading...</div>
                </div>
            </div>

            <div class="sidebar-section">
                <div class="section-title">Recent Trades</div>
                <div id="recentTrades">
                    <div style="text-align: center; padding: 20px; opacity: 0.6;">Loading...</div>
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <!-- Live Positions Panel -->
            <div class="live-positions-panel" id="livePositions">
                <div class="section-title">🔄 Live Positions & P&L</div>
                <div class="positions-grid" id="positionsGrid">
                    <div style="text-align: center; padding: 20px; opacity: 0.6;">Loading positions...</div>
                </div>
            </div>

            <!-- Market Analysis Grid -->
            <div class="analysis-grid" id="marketAnalysis">
                <div style="text-align: center; padding: 40px; opacity: 0.6;">Loading market data...</div>
            </div>
        </div>

        <!-- Charts -->
        <div class="charts">
            <div class="section-title">Performance Chart</div>
            <div style="text-align: center; padding: 40px; opacity: 0.6;">
                Chart visualization would go here<br>
                <small>Price history and performance metrics</small>
            </div>
        </div>

        <!-- Watchlist -->
        <div class="watchlist">
            <div class="sidebar-section">
                <div class="section-title">📊 Trade History</div>
                <div class="trade-history-feed" id="tradeHistory">
                    <div style="text-align: center; padding: 20px; opacity: 0.6;">Loading trades...</div>
                </div>
            </div>

            <div class="sidebar-section">
                <div class="section-title">🧠 Bot Analysis</div>
                <div class="thinking-feed" id="botThinking">
                    <div style="text-align: center; padding: 20px; opacity: 0.6;">Loading analysis...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function fetchData(endpoint) {
            try {
                const response = await fetch(endpoint);
                return await response.json();
            } catch (error) {
                console.error('Fetch error:', error);
                return null;
            }
        }

        function formatCurrency(value) {
            return `€${Math.abs(value).toFixed(2)}`;
        }

        function formatPercent(value) {
            return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
        }

        function getColorClass(value) {
            return value >= 0 ? 'positive' : 'negative';
        }

        async function updateHeader() {
            const performance = await fetchData('/api/performance');
            if (performance && performance.UltimateProfitStrategy) {
                const perf = performance.UltimateProfitStrategy;
                document.getElementById('totalBalance').textContent = formatCurrency(perf.current_balance);
                document.getElementById('totalProfit').textContent =
                    `${perf.profit_loss >= 0 ? '+' : ''}${formatCurrency(perf.profit_loss)}`;
                document.getElementById('totalProfit').className = `stat-value ${getColorClass(perf.profit_loss)}`;
                document.getElementById('winRate').textContent = `${perf.performance.win_rate.toFixed(1)}%`;
                document.getElementById('tradesCount').textContent = perf.performance.trade_count;
            }
        }

        async function updateStrategies() {
            const performance = await fetchData('/api/performance');
            if (performance) {
                const strategiesList = document.getElementById('strategiesList');
                strategiesList.innerHTML = '';

                Object.entries(performance).forEach(([name, perf]) => {
                    const card = document.createElement('div');
                    card.className = 'strategy-card';
                    card.innerHTML = `
                        <div class="strategy-name">${perf.name}</div>
                        <div class="strategy-balance">${formatCurrency(perf.current_balance)}</div>
                        <div class="strategy-metrics">
                            P&L: <span class="${getColorClass(perf.profit_loss)}">${formatPercent(perf.profit_percent)}</span><br>
                            Trades: ${perf.performance.trade_count} | Win: ${perf.performance.win_rate.toFixed(0)}%<br>
                            Open: ${perf.open_positions}/3 positions
                        </div>
                    `;
                    strategiesList.appendChild(card);
                });
            }
        }

        async function updateMarketAnalysis() {
            const market = await fetchData('/api/market_conditions');
            if (market) {
                const marketDiv = document.getElementById('marketAnalysis');
                marketDiv.innerHTML = '';

                Object.entries(market).forEach(([pair, conditions]) => {
                    const card = document.createElement('div');
                    card.className = 'analysis-card';

                    const signalClass = conditions.signal === 'BUY' ? 'signal-buy' :
                                       conditions.signal === 'SELL' ? 'signal-sell' : 'signal-hold';

                    const confidencePercent = Math.max(conditions.entry_score, conditions.exit_score) / 8 * 100;

                    card.innerHTML = `
                        <div class="card-header">
                            <div class="pair-name">${pair.replace('/USDT', '')}</div>
                            <div class="price-info">
                                <div class="current-price">$${conditions.price.toFixed(conditions.price < 1 ? 4 : 2)}</div>
                                <div class="price-change ${getColorClass(conditions.price_change_24h)}">
                                    ${formatPercent(conditions.price_change_24h)}
                                </div>
                            </div>
                        </div>

                        <!-- Mini Price Chart -->
                        <div class="price-chart">
                            <div class="price-line" style="animation-delay: ${Math.random()}s;"></div>
                        </div>

                        <div class="indicators-grid">
                            <div class="indicator"><span>RSI:</span><span style="color: ${conditions.rsi > 70 ? '#EF5350' : conditions.rsi < 30 ? '#26A69A' : '#D1D4DC'}">${conditions.rsi}</span></div>
                            <div class="indicator"><span>MACD:</span><span style="color: ${conditions.macd > 0 ? '#26A69A' : '#EF5350'}">${conditions.macd}</span></div>
                            <div class="indicator"><span>Volume:</span><span style="color: ${conditions.volume_ratio > 1.5 ? '#26A69A' : '#D1D4DC'}">${conditions.volume_ratio}x</span></div>
                            <div class="indicator"><span>Trend:</span><span style="color: ${conditions.trend_strength > 6 ? '#26A69A' : conditions.trend_strength < 4 ? '#EF5350' : '#D1D4DC'}">${conditions.trend_strength}/10</span></div>
                            <div class="indicator"><span>Support:</span><span>$${conditions.support.toFixed(4)}</span></div>
                            <div class="indicator"><span>Resistance:</span><span>$${conditions.resistance.toFixed(4)}</span></div>
                        </div>

                        <div class="signal-section">
                            <div class="signal-badge ${signalClass}">${conditions.signal}</div>
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: ${confidencePercent}%"></div>
                            </div>
                            <div style="font-size: 0.8em;">${confidencePercent.toFixed(0)}%</div>
                        </div>
                    `;
                    marketDiv.appendChild(card);
                });
            }
        }

        async function updateBotThinking() {
            const thinking = await fetchData('/api/bot_thinking');
            if (thinking && thinking.thoughts) {
                const thinkingDiv = document.getElementById('botThinking');

                if (thinking.thoughts.length > 0) {
                    thinkingDiv.innerHTML = thinking.thoughts.reverse().slice(0, 10).map(thought => {
                        const signalColor = thought.signal === 'BUY' ? '#26A69A' :
                                          thought.signal === 'SELL' ? '#EF5350' : '#2962FF';

                        return `
                            <div class="thinking-item" style="--signal-color: ${signalColor};">
                                <div class="thinking-header">
                                    <span class="thinking-pair">${thought.pair}</span>
                                    <span class="thinking-time">${thought.time}</span>
                                </div>
                                <div class="thinking-action">${thought.action} (${thought.confidence})</div>
                                <div class="thinking-analysis">${thought.analysis}</div>
                            </div>
                        `;
                    }).join('');
                } else {
                    thinkingDiv.innerHTML = '<div style="text-align: center; padding: 20px; opacity: 0.6;">Monitoring markets...</div>';
                }
            }
        }

        async function updateRecentTrades() {
            const trades = await fetchData('/api/trades/UltimateProfitStrategy');
            if (trades && trades.trades) {
                const tradesDiv = document.getElementById('recentTrades');

                if (trades.trades.length > 0) {
                    const recentTrades = trades.trades.slice(-5).reverse();
                    tradesDiv.innerHTML = recentTrades.map(trade => `
                        <div style="background: #1E222D; padding: 8px; border-radius: 4px; margin-bottom: 6px; font-size: 0.8em;">
                            <div style="display: flex; justify-content: space-between;">
                                <span>${trade.pair.replace('/USDT', '')}</span>
                                <span class="${getColorClass(trade.profit_loss)}">${formatCurrency(trade.profit_loss)}</span>
                            </div>
                            <div style="opacity: 0.7; font-size: 0.75em;">
                                ${formatPercent(trade.profit_percent)} | ${trade.hold_time_minutes?.toFixed(0) || 0}min
                            </div>
                        </div>
                    `).join('');
                } else {
                    tradesDiv.innerHTML = '<div style="text-align: center; padding: 20px; opacity: 0.6;">No trades yet</div>';
                }
            }
        }

        async function updateLivePositions() {
            const livePnl = await fetchData('/api/live_pnl/UltimateProfitStrategy');
            if (livePnl && livePnl.length > 0) {
                const positionsDiv = document.getElementById('positionsGrid');
                positionsDiv.innerHTML = livePnl.map(position => {
                    const pnlColor = position.unrealized_pnl >= 0 ? '#26A69A' : '#EF5350';
                    const progressPercent = Math.abs(position.unrealized_percent);
                    const glowClass = position.unrealized_pnl >= 0 ? 'glow-green' : 'glow-red';

                    return `
                        <div class="position-card ${glowClass}" style="--pnl-color: ${pnlColor};">
                            <div class="position-header">
                                <span class="position-pair">${position.pair.replace('/USDT', '')}</span>
                                <span class="position-pnl" style="color: ${pnlColor};">
                                    €${position.unrealized_pnl >= 0 ? '+' : ''}${position.unrealized_pnl.toFixed(3)}
                                </span>
                            </div>
                            <div class="position-details">
                                <div>Entry: $${position.entry_price.toFixed(4)}</div>
                                <div>Current: $${position.current_price.toFixed(4)}</div>
                                <div>Amount: €${position.amount.toFixed(0)}</div>
                                <div>Hold: ${position.hold_time_minutes.toFixed(0)}min</div>
                                <div>Stop: $${position.stop_loss.toFixed(4)}</div>
                                <div>Target: $${position.take_profit.toFixed(4)}</div>
                            </div>
                            <div style="text-align: center; font-weight: 600; color: ${pnlColor};">
                                ${position.unrealized_percent >= 0 ? '+' : ''}${position.unrealized_percent.toFixed(2)}%
                            </div>
                            <div class="position-progress">
                                <div class="position-progress-fill" style="width: ${Math.min(progressPercent * 10, 100)}%; background: ${pnlColor};"></div>
                            </div>
                        </div>
                    `;
                }).join('');
            } else {
                document.getElementById('positionsGrid').innerHTML =
                    '<div style="text-align: center; padding: 20px; opacity: 0.6;">No open positions</div>';
            }
        }

        async function updateTradeHistory() {
            const trades = await fetchData('/api/trades/UltimateProfitStrategy');
            if (trades && trades.trades) {
                const tradesDiv = document.getElementById('tradeHistory');

                if (trades.trades.length > 0) {
                    const recentTrades = trades.trades.slice(-10).reverse();
                    tradesDiv.innerHTML = recentTrades.map(trade => {
                        const tradeColor = trade.profit_loss >= 0 ? '#26A69A' : '#EF5350';
                        const tradeIcon = trade.profit_loss >= 0 ? '✅' : '❌';
                        const tradeType = trade.trade_type || 'TRADE';

                        return `
                            <div class="trade-item" style="--trade-color: ${tradeColor};" onclick="showTradeDetails(${trade.id})">
                                <div class="trade-header">
                                    <span class="trade-pair">${tradeIcon} ${trade.pair.replace('/USDT', '')}</span>
                                    <span class="trade-pnl" style="color: ${tradeColor};">
                                        €${trade.profit_loss >= 0 ? '+' : ''}${trade.profit_loss.toFixed(3)}
                                    </span>
                                </div>
                                <div class="trade-details">
                                    ${formatPercent(trade.profit_percent)} | ${trade.hold_time_minutes?.toFixed(0) || 0}min | ${tradeType}
                                </div>
                                <div class="trade-strategy">
                                    ${trade.entry_strategy || 'Strategy N/A'}
                                </div>
                            </div>
                        `;
                    }).join('');
                } else {
                    tradesDiv.innerHTML = '<div style="text-align: center; padding: 20px; opacity: 0.6;">No trades yet</div>';
                }
            }
        }

        function showTradeDetails(tradeId) {
            // Show detailed trade analysis in a modal or alert
            fetchData(`/api/trade_analysis/${tradeId}`).then(data => {
                if (data && data.trade) {
                    const trade = data.trade;
                    const analysis = data.analysis;

                    alert(`
🔍 TRADE ANALYSIS #${trade.id}

📊 Basic Info:
• Pair: ${trade.pair}
• Type: ${analysis.trade_type}
• Rating: ${analysis.performance_rating}

💰 Financial:
• Entry: $${trade.entry_price.toFixed(4)}
• Exit: $${trade.exit_price.toFixed(4)}
• P&L: €${trade.profit_loss >= 0 ? '+' : ''}${trade.profit_loss.toFixed(4)} (${trade.profit_percent.toFixed(2)}%)
• Fees: €${trade.fees_paid.toFixed(4)}

⏱️ Timing:
• Hold Time: ${trade.hold_time_minutes.toFixed(0)} minutes
• Entry: ${new Date(trade.entry_time).toLocaleTimeString()}
• Exit: ${new Date(trade.exit_time).toLocaleTimeString()}

🎯 Strategy:
• Entry Reason: ${analysis.entry_reason}
• Exit Reason: ${analysis.exit_reason}
• Support/Resistance: ${analysis.support_resistance}
                    `);
                }
            });
        }

        async function updateAll() {
            await Promise.all([
                updateHeader(),
                updateStrategies(),
                updateLivePositions(),
                updateMarketAnalysis(),
                updateTradeHistory(),
                updateBotThinking(),
                updateRecentTrades()
            ]);
        }

        // Initial load
        updateAll();

        // Auto-refresh
        setInterval(updateAll, 8000);  // Every 8 seconds
        setInterval(updateBotThinking, 4000);  // Bot thinking every 4 seconds
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🚀 TradingView Pro Style UI - Advanced Trading Monitor")
    print("💰 Budget: €500 | Professional Analytics | Real Trading Simulation")
    print("🌐 Available at: http://localhost:5001")
    print("📊 Features: Advanced metrics, Professional UI, Real-time analysis")

    # Load previous data
    load_data()

    # Start background update thread
    threading.Thread(target=update_loop, daemon=True).start()

    try:
        app.run(host='0.0.0.0', port=5001, debug=False, threaded=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
        save_data()
    except Exception as e:
        print(f"❌ Server error: {e}")
        save_data()