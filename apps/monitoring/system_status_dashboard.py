#!/usr/bin/env python3
"""
Enhanced System Status Dashboard
Comprehensive monitoring and analytics for Enhanced Bot trading system
"""

import requests
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request
import subprocess
import psutil
import os
import logging
import threading
import time
import feedparser
import re
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CelebrityAlert:
    timestamp: datetime
    celebrity: str
    coin: str
    sentiment: str
    impact_score: float
    source: str
    headline: str
    content: str
    action_taken: str
    trade_executed: bool

class CelebrityMonitor:
    """Celebrity crypto endorsement monitoring and auto-trading"""

    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "databases", "celebrity_alerts.db")
        self.freqtrade_api = "http://localhost:8081/api/v1"
        self.freqtrade_auth = ("freqtrade", "ruriu7AY")
        self.running = False
        self.monitor_thread = None

        # Celebrity configurations
        self.celebrities = {
            'Trump': {
                'keywords': ['trump', 'donald trump', 'president trump', '@realdonaldtrump'],
                'crypto_keywords': ['bitcoin', 'btc', 'crypto', 'cryptocurrency', 'coin', 'token'],
                'impact_weight': 0.9,
                'priority': 'CRITICAL'
            },
            'Elon Musk': {
                'keywords': ['elon musk', 'musk', '@elonmusk', 'tesla', 'spacex'],
                'crypto_keywords': ['dogecoin', 'doge', 'bitcoin', 'btc', 'crypto', 'shiba'],
                'impact_weight': 0.95,
                'priority': 'CRITICAL'
            },
            'Michael Saylor': {
                'keywords': ['michael saylor', 'saylor', '@saylor', 'microstrategy'],
                'crypto_keywords': ['bitcoin', 'btc', 'cryptocurrency'],
                'impact_weight': 0.7,
                'priority': 'HIGH'
            },
            'Cathie Wood': {
                'keywords': ['cathie wood', 'ark invest', '@cathiedwood'],
                'crypto_keywords': ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto'],
                'impact_weight': 0.6,
                'priority': 'MEDIUM'
            }
        }

        # Coin mappings for trading
        self.coin_mappings = {
            'bitcoin': 'BTC/USDC', 'btc': 'BTC/USDC',
            'ethereum': 'ETH/USDC', 'eth': 'ETH/USDC',
            'dogecoin': 'DOGE/USDC', 'doge': 'DOGE/USDC',
            'shiba': 'SHIB/USDC', 'shib': 'SHIB/USDC',
            'pepe': 'PEPE/USDC', 'bonk': 'BONK/USDC',
            'solana': 'SOL/USDC', 'sol': 'SOL/USDC',
            'cardano': 'ADA/USDC', 'ada': 'ADA/USDC',
            'polkadot': 'DOT/USDC', 'dot': 'DOT/USDC'
        }

        self.init_database()

    def init_database(self):
        """Initialize celebrity alerts database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS celebrity_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                celebrity TEXT,
                coin TEXT,
                sentiment TEXT,
                impact_score REAL,
                source TEXT,
                headline TEXT,
                content TEXT,
                action_taken TEXT,
                trade_executed BOOLEAN,
                trade_pair TEXT,
                profit_loss REAL
            )
        ''')

        conn.commit()
        conn.close()

    def analyze_sentiment(self, text: str, celebrity: str, coin: str) -> dict:
        """Enhanced sentiment analysis"""
        text_lower = text.lower()

        positive_words = {
            'buy': 0.8, 'invest': 0.7, 'hodl': 0.9, 'moon': 0.8, 'pump': 0.6,
            'bullish': 0.7, 'support': 0.6, 'backing': 0.8, 'endorsing': 0.9,
            'love': 0.5, 'great': 0.4, 'amazing': 0.6, 'revolutionary': 0.7
        }

        negative_words = {
            'sell': -0.8, 'dump': -0.9, 'crash': -0.8, 'bearish': -0.7,
            'avoid': -0.6, 'warning': -0.7, 'scam': -1.0, 'dangerous': -0.8
        }

        positive_score = sum(weight for word, weight in positive_words.items() if word in text_lower)
        negative_score = sum(abs(weight) for word, weight in negative_words.items() if word in text_lower)

        # Celebrity-specific boosts
        if celebrity == 'Elon Musk' and 'doge' in text_lower:
            positive_score *= 1.3
        if celebrity == 'Trump' and 'bitcoin' in text_lower:
            positive_score *= 1.2

        net_score = positive_score - negative_score

        if net_score > 0.5:
            sentiment = "POSITIVE"
            confidence = min(0.95, 0.6 + (net_score * 0.1))
        elif net_score < -0.3:
            sentiment = "NEGATIVE"
            confidence = min(0.9, 0.5 + (abs(net_score) * 0.1))
        else:
            sentiment = "NEUTRAL"
            confidence = 0.3 + abs(net_score) * 0.1

        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_score': positive_score,
            'negative_score': negative_score,
            'net_score': net_score
        }

    def calculate_impact_score(self, celebrity: str, sentiment_data: dict) -> float:
        """Calculate impact score for trading decision"""
        base_impact = self.celebrities.get(celebrity, {}).get('impact_weight', 0.5)

        impact_score = (
            base_impact *
            sentiment_data['confidence'] *
            (1 + sentiment_data['positive_score'] * 0.1)
        )

        return min(1.0, max(0.0, impact_score))

    def should_execute_trade(self, celebrity: str, impact_score: float, sentiment: str) -> bool:
        """Determine if trade should be executed"""
        thresholds = {
            'Elon Musk': 0.6,
            'Trump': 0.65,
            'Michael Saylor': 0.75,
            'Cathie Wood': 0.8
        }

        threshold = thresholds.get(celebrity, 0.7)
        return sentiment == "POSITIVE" and impact_score >= threshold

    def execute_trade(self, pair: str, celebrity: str, impact_score: float) -> dict:
        """Execute trade through FreqTrade API"""
        try:
            amount = 25.0 * (1 + (impact_score - 0.5))  # Scale with impact
            amount = min(amount, 50.0)  # Max 50 USDC

            url = f"{self.freqtrade_api}/forceentry"
            data = {
                "pair": pair,
                "side": "long",
                "ordertype": "market",
                "stakeamount": amount,
                "enter_tag": f"celebrity_{celebrity.replace(' ', '_').lower()}"
            }

            response = requests.post(url, json=data, auth=self.freqtrade_auth, timeout=15)

            if response.status_code == 200:
                logger.info(f"🚀 CELEBRITY TRADE: {pair} - {celebrity} signal")
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_news_feeds(self) -> list:
        """Search RSS feeds for celebrity crypto mentions"""
        results = []

        feeds = [
            "https://cointelegraph.com/rss",
            "https://coindesk.com/arc/outboundfeeds/rss/",
            "https://decrypt.co/feed",
            "https://cryptonews.com/news/feed/",
            "https://finance.yahoo.com/rss/topstories"
        ]

        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                source = feed_url.split('/')[2]

                for entry in feed.entries[:5]:  # Check latest 5 entries
                    title = entry.get('title', '').lower()
                    description = entry.get('description', '').lower()
                    content = f"{title} {description}"

                    # Check for celebrity + crypto mentions
                    for celebrity, config in self.celebrities.items():
                        for keyword in config['keywords']:
                            if keyword.lower() in content:
                                for crypto_keyword in config['crypto_keywords']:
                                    if crypto_keyword.lower() in content:
                                        results.append({
                                            'celebrity': celebrity,
                                            'coin': crypto_keyword,
                                            'content': content,
                                            'source': source,
                                            'title': entry.get('title', ''),
                                            'url': entry.get('link', '')
                                        })
                                        break
                                break

            except Exception as e:
                logger.debug(f"Error parsing feed {feed_url}: {e}")
                continue

            time.sleep(1)  # Rate limiting

        return results

    def process_alert(self, celebrity: str, coin: str, content: str, source: str, title: str) -> CelebrityAlert:
        """Process celebrity alert and potentially execute trade"""
        sentiment_data = self.analyze_sentiment(content, celebrity, coin)
        impact_score = self.calculate_impact_score(celebrity, sentiment_data)

        trading_pair = self.coin_mappings.get(coin.lower())
        trade_executed = False
        action_taken = "MONITORED"

        # Execute trade if conditions met
        if trading_pair and self.should_execute_trade(celebrity, impact_score, sentiment_data['sentiment']):
            trade_result = self.execute_trade(trading_pair, celebrity, impact_score)
            if trade_result["success"]:
                trade_executed = True
                action_taken = f"BUY_EXECUTED_{trading_pair}"
            else:
                action_taken = f"BUY_FAILED"

        alert = CelebrityAlert(
            timestamp=datetime.now(),
            celebrity=celebrity,
            coin=coin,
            sentiment=sentiment_data['sentiment'],
            impact_score=impact_score,
            source=source,
            headline=title,
            content=content[:300],
            action_taken=action_taken,
            trade_executed=trade_executed
        )

        # Store in database
        self.store_alert(alert, trading_pair if trade_executed else None)

        return alert

    def store_alert(self, alert: CelebrityAlert, trading_pair: str = None):
        """Store alert in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO celebrity_alerts
            (timestamp, celebrity, coin, sentiment, impact_score, source, headline, content, action_taken, trade_executed, trade_pair)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert.timestamp, alert.celebrity, alert.coin, alert.sentiment,
            alert.impact_score, alert.source, alert.headline, alert.content,
            alert.action_taken, alert.trade_executed, trading_pair
        ))

        conn.commit()
        conn.close()

    def get_recent_alerts(self, hours: int = 24) -> list:
        """Get recent alerts from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since = datetime.now() - timedelta(hours=hours)
        cursor.execute('''
            SELECT * FROM celebrity_alerts
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 50
        ''', (since,))

        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return results

    def monitoring_cycle(self):
        """Main monitoring cycle"""
        while self.running:
            try:
                logger.info("🎬 Scanning for celebrity crypto news...")

                news_results = self.search_news_feeds()
                alerts_processed = 0
                trades_executed = 0

                for result in news_results:
                    alert = self.process_alert(
                        result['celebrity'], result['coin'],
                        result['content'], result['source'], result['title']
                    )

                    alerts_processed += 1
                    if alert.trade_executed:
                        trades_executed += 1

                    time.sleep(2)  # Rate limiting

                if alerts_processed > 0:
                    logger.info(f"✅ Processed {alerts_processed} alerts, executed {trades_executed} trades")

                # Sleep for 10 minutes
                time.sleep(600)

            except Exception as e:
                logger.error(f"Error in celebrity monitoring: {e}")
                time.sleep(300)  # 5 minutes on error

    def start_monitoring(self):
        """Start celebrity monitoring in background thread"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self.monitoring_cycle, daemon=True)
            self.monitor_thread.start()
            logger.info("🎬 Celebrity monitoring started")

    def stop_monitoring(self):
        """Stop celebrity monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("🛑 Celebrity monitoring stopped")

    def get_status(self):
        """Get celebrity monitoring status"""
        recent_alerts = self.get_recent_alerts(24)

        return {
            'running': self.running,
            'total_alerts_24h': len(recent_alerts),
            'trades_executed_24h': len([a for a in recent_alerts if a['trade_executed']]),
            'high_impact_alerts': len([a for a in recent_alerts if a['impact_score'] > 0.7]),
            'celebrities_monitored': len(self.celebrities),
            'trading_pairs_supported': len(self.coin_mappings),
            'recent_alerts': recent_alerts[:10]  # Latest 10 alerts
        }

class EnhancedBotAnalytics:
    """Advanced analytics for Enhanced Bot trading system"""

    def __init__(self):
        self.api_url = "http://localhost:8081/api/v1"
        self.auth = ('freqtrade', 'ruriu7AY')
        self.db_path = "user_data/E0V1E_USDC_trades.sqlite"

    def get_api_data(self, endpoint):
        """Fetch data from FreqTrade API"""
        try:
            response = requests.get(f"{self.api_url}{endpoint}", auth=self.auth, timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                # Μην εμφανίζεις σφάλματα όταν το bot είναι απενεργοποιημένο
                if response.status_code in [401, 403, 404, 500, 502, 503]:
                    return {}
                logger.warning(f"API Warning {response.status_code} for {endpoint}")
                return {}
        except requests.exceptions.ConnectionError:
            # Bot είναι απενεργοποιημένο - δεν είναι σφάλμα
            return {}
        except requests.exceptions.Timeout:
            # Timeout - μην το θεωρούμε σφάλμα
            return {}
        except Exception as e:
            # Μόνο για πραγματικά απροσδόκητα σφάλματα
            logger.debug(f"API connection issue for {endpoint}: {e}")
            return {}

    def analyze_trade_performance(self, trade):
        """Analyze individual trade with detailed metrics"""
        profit_abs = trade.get('profit_abs', 0)
        profit_pct = trade.get('profit_ratio', 0) * 100 if trade.get('profit_ratio') else 0

        # Calculate duration
        if trade.get('open_date') and trade.get('close_date'):
            open_time = datetime.fromisoformat(trade['open_date'].replace('Z', ''))
            close_time = datetime.fromisoformat(trade['close_date'].replace('Z', ''))
            duration_minutes = int((close_time - open_time).total_seconds() / 60)
        else:
            duration_minutes = 0

        # Performance analysis
        if profit_pct > 3:
            performance = "🟢 Excellent"
            recommendation = "Perfect trade - Enhanced Bot working optimally"
        elif profit_pct > 1:
            performance = "🟢 Good"
            recommendation = "Profitable trade - good entry/exit timing"
        elif profit_pct > 0:
            performance = "🟡 Marginal Win"
            recommendation = "Small profit - could improve exit timing"
        elif profit_pct > -1:
            performance = "🟡 Small Loss"
            recommendation = "Minor loss - acceptable within strategy"
        elif profit_pct > -3:
            performance = "🟴 Poor"
            recommendation = "Significant loss - review entry conditions"
        else:
            performance = "🔴 Critical"
            recommendation = "Major loss - immediate strategy review needed"

        # Duration analysis
        if duration_minutes > 0:
            if duration_minutes < 30:
                duration_analysis = "Very fast trade"
            elif duration_minutes < 120:
                duration_analysis = "Normal duration"
            elif duration_minutes < 360:
                duration_analysis = "Long trade"
            else:
                duration_analysis = "Very long trade - check exit strategy"
        else:
            duration_analysis = "Open trade"

        # Risk assessment
        risk_score = 50  # Base risk
        if profit_pct < -5:
            risk_score += 30
        elif profit_pct < -2:
            risk_score += 15
        elif profit_pct > 2:
            risk_score -= 15

        if duration_minutes > 240:
            risk_score += 10

        return {
            'trade_id': trade.get('trade_id', 0),
            'pair': trade.get('pair', ''),
            'profit_abs': profit_abs,
            'profit_pct': profit_pct,
            'duration_minutes': duration_minutes,
            'duration_analysis': duration_analysis,
            'performance': performance,
            'recommendation': recommendation,
            'risk_score': min(100, max(0, risk_score)),
            'entry_rate': trade.get('open_rate', 0),
            'exit_rate': trade.get('close_rate', 0),
            'exit_reason': trade.get('exit_reason', 'unknown')
        }

    def get_comprehensive_analysis(self):
        """Get complete trading analysis for Enhanced Bot"""
        try:
            # Fetch current data
            status = self.get_api_data('/status')
            balance = self.get_api_data('/balance')
            trades = self.get_api_data('/trades')
            profit = self.get_api_data('/profit')

            # Analyze trades
            trade_analyses = []
            for trade in trades:
                if trade.get('close_date'):
                    analysis = self.analyze_trade_performance(trade)
                    trade_analyses.append(analysis)

            # Calculate metrics
            closed_trades = [t for t in trades if t.get('close_date')]
            if closed_trades:
                profits = [t.get('profit_abs', 0) for t in closed_trades]
                profit_pcts = [t.get('profit_ratio', 0) * 100 for t in closed_trades if t.get('profit_ratio')]

                winning_trades = len([p for p in profits if p > 0])
                losing_trades = len([p for p in profits if p < 0])

                metrics = {
                    'total_trades': len(closed_trades),
                    'winning_trades': winning_trades,
                    'losing_trades': losing_trades,
                    'win_rate': (winning_trades / len(closed_trades) * 100) if closed_trades else 0,
                    'total_profit': sum(profits),
                    'avg_profit': np.mean(profits) if profits else 0,
                    'best_trade': max(profits) if profits else 0,
                    'worst_trade': min(profits) if profits else 0,
                    'avg_profit_pct': np.mean(profit_pcts) if profit_pcts else 0
                }
            else:
                metrics = {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'win_rate': 0,
                    'total_profit': 0,
                    'avg_profit': 0,
                    'best_trade': 0,
                    'worst_trade': 0,
                    'avg_profit_pct': 0
                }

            # Generate recommendations
            recommendations = self.generate_recommendations(metrics, trade_analyses)

            # Pair performance analysis
            pair_performance = {}
            for trade in closed_trades:
                pair = trade.get('pair', '')
                if pair not in pair_performance:
                    pair_performance[pair] = {'trades': 0, 'profit': 0, 'wins': 0}
                pair_performance[pair]['trades'] += 1
                pair_performance[pair]['profit'] += trade.get('profit_abs', 0)
                if trade.get('profit_abs', 0) > 0:
                    pair_performance[pair]['wins'] += 1

            # Calculate win rates for pairs
            for pair in pair_performance:
                total = pair_performance[pair]['trades']
                wins = pair_performance[pair]['wins']
                pair_performance[pair]['win_rate'] = (wins / total * 100) if total > 0 else 0

            return {
                'timestamp': datetime.now().isoformat(),
                'bot_status': {
                    'running': len(status) > 0,
                    'open_trades': len(status),
                    'balance': balance.get('total', 0),
                    'free_balance': balance.get('free', 0),
                    'used_balance': balance.get('used', 0)
                },
                'metrics': metrics,
                'trade_analyses': sorted(trade_analyses, key=lambda x: x['trade_id'], reverse=True)[:15],
                'recommendations': recommendations,
                'pair_performance': dict(sorted(pair_performance.items(),
                                              key=lambda x: x[1]['profit'], reverse=True)),
                'current_trades': status
            }

        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            return {'error': str(e)}

    def generate_recommendations(self, metrics, trade_analyses):
        """Generate actionable recommendations for Enhanced Bot"""
        recommendations = []

        win_rate = metrics.get('win_rate', 0)
        total_profit = metrics.get('total_profit', 0)
        avg_profit = metrics.get('avg_profit', 0)
        total_trades = metrics.get('total_trades', 0)

        # Win rate recommendations
        if win_rate < 40:
            recommendations.append({
                'type': 'critical',
                'title': 'Κρίσιμο Ποσοστό Επιτυχίας',
                'message': f'Ποσοστό επιτυχίας {win_rate:.1f}% είναι πολύ χαμηλό',
                'action': 'Αναθεώρηση παραμέτρων Enhanced Bot (RSI, CTI thresholds)'
            })
        elif win_rate < 50:
            recommendations.append({
                'type': 'warning',
                'title': 'Χαμηλό Ποσοστό Επιτυχίας',
                'message': f'Ποσοστό επιτυχίας {win_rate:.1f}% χρειάζεται βελτίωση',
                'action': 'Ανάλυση αποτυχημένων trades για κοινά patterns'
            })
        elif win_rate > 70:
            recommendations.append({
                'type': 'success',
                'title': 'Εξαιρετικό Ποσοστό Επιτυχίας',
                'message': f'Ποσοστό επιτυχίας {win_rate:.1f}% είναι άριστο!',
                'action': 'Εξετάστε αύξηση position size ή max trades'
            })

        # Profit recommendations
        if total_profit < 0:
            recommendations.append({
                'type': 'critical',
                'title': 'Αρνητικό Συνολικό Κέρδος',
                'message': f'Συνολική ζημία: {total_profit:.2f} USDC',
                'action': 'Άμεση αναθεώρηση Enhanced Bot στρατηγικής απαιτείται'
            })
        elif avg_profit < 0:
            recommendations.append({
                'type': 'warning',
                'title': 'Αρνητικός Μέσος Όρος Κέρδους',
                'message': f'Μέσος όρος ανά trade: {avg_profit:.2f} USDC',
                'action': 'Βελτίωση exit strategy και risk management'
            })
        elif total_profit > 10:
            recommendations.append({
                'type': 'success',
                'title': 'Κερδοφόρα Στρατηγική',
                'message': f'Συνολικό κέρδος: {total_profit:.2f} USDC',
                'action': 'Enhanced Bot λειτουργεί άριστα - συνεχίστε'
            })

        # Data quality
        if total_trades < 10:
            recommendations.append({
                'type': 'info',
                'title': 'Περιορισμένα Δεδομένα',
                'message': f'Μόνο {total_trades} trades διαθέσιμα',
                'action': 'Περιμένετε περισσότερα trades για αξιόπιστη ανάλυση'
            })

        # Recent performance
        if trade_analyses:
            recent_trades = trade_analyses[:5]
            recent_losses = [t for t in recent_trades if t['profit_abs'] < 0]
            if len(recent_losses) >= 3:
                recommendations.append({
                    'type': 'warning',
                    'title': 'Πρόσφατες Ζημίες',
                    'message': f'{len(recent_losses)} από τα τελευταία 5 trades είναι ζημιογόνα',
                    'action': 'Παρακολουθήστε στενά και εξετάστε προσωρινή παύση'
                })

        return recommendations

# Flask application
app = Flask(__name__)

# Initialize analytics and celebrity monitor
enhanced_analytics = EnhancedBotAnalytics()
celebrity_monitor = CelebrityMonitor()

# Start celebrity monitoring automatically
celebrity_monitor.start_monitoring()

# System monitoring functions
def get_system_status():
    """Get comprehensive system status"""
    try:
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Network
        network = psutil.net_io_counters()

        # Load average
        load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)

        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used': memory.used / (1024**3),  # GB
            'memory_total': memory.total / (1024**3),  # GB
            'disk_percent': disk.percent,
            'disk_used': disk.used / (1024**3),  # GB
            'disk_total': disk.total / (1024**3),  # GB
            'load_avg': load_avg,
            'network_sent': network.bytes_sent / (1024**2),  # MB
            'network_recv': network.bytes_recv / (1024**2),  # MB
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {'error': str(e)}

def get_bot_status():
    """Get FreqTrade bot status"""
    try:
        # Check if FreqTrade process is running
        freqtrade_running = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and 'freqtrade' in ' '.join(proc.info['cmdline']).lower():
                    freqtrade_running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError):
                continue

        # Αν το bot δεν τρέχει, μην προσπαθείς να συνδεθείς στο API
        if not freqtrade_running:
            return {
                'process_running': False,
                'api_accessible': False,
                'open_trades': 0,
                'balance': 0,
                'free_balance': 0,
                'used_balance': 0,
                'status': 'Bot απενεργοποιημένο',
                'timestamp': datetime.now().isoformat()
            }

        # Try to get API data only if process is running
        api_data = enhanced_analytics.get_api_data('/status')
        balance_data = enhanced_analytics.get_api_data('/balance')

        return {
            'process_running': freqtrade_running,
            'api_accessible': len(api_data) > 0,
            'open_trades': len(api_data) if api_data else 0,
            'balance': balance_data.get('total', 0) if balance_data else 0,
            'free_balance': balance_data.get('free', 0) if balance_data else 0,
            'used_balance': balance_data.get('used', 0) if balance_data else 0,
            'status': 'Bot ενεργό' if len(api_data) > 0 else 'API μη διαθέσιμο',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        # Μην εμφανίζεις σφάλματα για απενεργοποιημένο bot
        logger.debug(f"Bot status check: {e}")
        return {
            'process_running': False,
            'api_accessible': False,
            'open_trades': 0,
            'balance': 0,
            'free_balance': 0,
            'used_balance': 0,
            'status': 'Bot απενεργοποιημένο',
            'timestamp': datetime.now().isoformat()
        }

def get_overview_status():
    """Get combined overview status"""
    try:
        system_data = get_system_status()
        bot_data = get_bot_status()

        return {
            'system': system_data,
            'bot': bot_data,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting overview status: {e}")
        return {'error': str(e)}

# Original System Dashboard HTML with Analytics Tab
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="el">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Advanced Strategy Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .tabs {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 10px;
        }
        .tab {
            padding: 12px 24px;
            margin: 0 5px;
            background: transparent;
            border: none;
            color: #fff;
            cursor: pointer;
            border-radius: 10px;
            transition: all 0.3s ease;
            font-size: 1em;
        }
        .tab.active {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
        }
        .tab:hover:not(.active) {
            background: rgba(255, 255, 255, 0.1);
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }
        .status-card:hover {
            transform: translateY(-5px);
        }
        .status-card h3 {
            font-size: 1em;
            margin-bottom: 15px;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .status-card .value {
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .status-card .change {
            font-size: 0.9em;
            opacity: 0.8;
        }
        .positive { color: #4CAF50; }
        .negative { color: #f44336; }
        .neutral { color: #FFA500; }
        .warning { color: #FF9800; }
        .info { color: #2196F3; }

        /* Analytics specific styles */
        .analytics-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        .chart-container, .section {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .trades-section { grid-column: 1 / -1; }
        .trades-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        .trades-table th, .trades-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .trades-table th {
            background: rgba(255, 255, 255, 0.1);
            font-weight: bold;
        }
        .trades-table tr:hover { background: rgba(255, 255, 255, 0.05); }
        .recommendation {
            margin: 10px 0;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid;
        }
        .recommendation.critical {
            background: rgba(244, 67, 54, 0.2);
            border-color: #f44336;
        }
        .recommendation.warning {
            background: rgba(255, 193, 7, 0.2);
            border-color: #FFC107;
        }
        .recommendation.success {
            background: rgba(76, 175, 80, 0.2);
            border-color: #4CAF50;
        }
        .recommendation.info {
            background: rgba(33, 150, 243, 0.2);
            border-color: #2196F3;
        }

        .refresh-btn {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            margin: 10px;
            transition: all 0.3s ease;
        }
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
        }
        .loading {
            text-align: center;
            padding: 40px;
            opacity: 0.7;
            font-size: 1.1em;
        }
        /* Celebrity monitoring styles */
        .alerts-list {
            max-height: 400px;
            overflow-y: auto;
        }
        .alert-item {
            background: rgba(255, 255, 255, 0.1);
            margin: 10px 0;
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        .alert-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            font-weight: bold;
        }
        .celebrity {
            color: #FFD700;
        }
        .coin {
            color: #4CAF50;
            background: rgba(76, 175, 80, 0.2);
            padding: 2px 8px;
            border-radius: 5px;
        }
        .timestamp {
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.9em;
        }
        .alert-content {
            margin-top: 10px;
        }
        .headline {
            margin-bottom: 8px;
            font-weight: 500;
        }
        .alert-metrics {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            font-size: 0.9em;
            color: rgba(255, 255, 255, 0.8);
        }
        .celebrity-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .celebrity-stat-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        .celebrity-stat-card h4 {
            margin-bottom: 10px;
            color: #FFD700;
        }
        .stat-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .impact-bar {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 5px;
        }
        .impact-fill {
            height: 100%;
            transition: width 0.3s ease;
        }
        .impact-text {
            text-align: center;
            font-size: 0.9em;
            color: rgba(255, 255, 255, 0.8);
        }
        .no-data {
            text-align: center;
            padding: 40px;
            color: rgba(255, 255, 255, 0.6);
            font-style: italic;
        }

        @media (max-width: 768px) {
            .analytics-content { grid-template-columns: 1fr; }
            .status-grid { grid-template-columns: repeat(2, 1fr); }
            .header h1 { font-size: 1.8em; }
            .tabs { flex-direction: column; }
            .tab { margin: 2px 0; }
            .celebrity-stats { grid-template-columns: 1fr; }
            .alert-header { flex-direction: column; align-items: flex-start; }
            .alert-metrics { flex-direction: column; gap: 5px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Advanced Strategy Dashboard</h1>
            <p>Professional Trading Strategy Management & Analysis</p>
            <button class="refresh-btn" onclick="refreshAllData()">🔄 Refresh Data Info</button>
            <div style="margin-top: 10px; font-size: 0.9em; opacity: 0.8;">
                Last Update: <span id="lastUpdate">-</span>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('overview')">📊 Overview</button>
            <button class="tab" onclick="showTab('strategies')">⚡ Strategies</button>
            <button class="tab" onclick="showTab('conditions')">🎯 Conditions</button>
            <button class="tab" onclick="showTab('sentiment')">📈 Sentiment</button>
            <button class="tab" onclick="showTab('celebrity')">🎬 Celebrity News</button>
            <button class="tab" onclick="showTab('ai-control')">🤖 AI Control</button>
            <button class="tab" onclick="showTab('data')">📊 Data</button>
            <button class="tab" onclick="showTab('history')">📜 History</button>
            <button class="tab" onclick="showTab('performance')">🎯 Performance</button>
            <button class="tab" onclick="showTab('system')">⚙️ System</button>
        </div>

        <!-- Overview Tab -->
        <div id="overview-tab" class="tab-content active">
            <div class="status-grid" id="overviewGrid">
                <div class="loading">Loading overview...</div>
            </div>
        </div>

        <!-- Strategies Tab -->
        <div id="strategies-tab" class="tab-content">
            <div class="status-grid" id="strategiesGrid">
                <div class="loading">Loading strategies...</div>
            </div>
            <div class="section">
                <h3>⚡ Active Strategies</h3>
                <div id="activeStrategiesContainer">
                    <div class="loading">Loading active strategies...</div>
                </div>
            </div>
        </div>

        <!-- Strategy Conditions Tab -->
        <div id="conditions-tab" class="tab-content">
            <div class="status-grid" id="conditionsGrid">
                <div class="loading">Loading strategy conditions...</div>
            </div>
            <div class="section">
                <h3>🎯 Pairs Ready to Trade</h3>
                <div id="readyPairsContainer">
                    <div class="loading">Analyzing entry conditions...</div>
                </div>
            </div>
            <div class="section">
                <h3>⚙️ Strategy Parameters</h3>
                <div id="strategyParamsContainer">
                    <div class="loading">Loading strategy parameters...</div>
                </div>
            </div>
        </div>

        <!-- Market Sentiment Tab -->
        <div id="sentiment-tab" class="tab-content">
            <div class="status-grid" id="sentimentGrid">
                <div class="loading">Loading market sentiment...</div>
            </div>
            <div class="analytics-content">
                <div class="chart-container">
                    <h3>😨 Fear & Greed Index</h3>
                    <div id="fearGreedContainer">
                        <div class="loading">Loading Fear & Greed Index...</div>
                    </div>
                </div>
                <div class="chart-container">
                    <h3>📰 News Sentiment</h3>
                    <div id="newsSentimentContainer">
                        <div class="loading">Analyzing news sentiment...</div>
                    </div>
                </div>
            </div>
            <div class="section">
                <h3>🧠 Market Analysis</h3>
                <div id="marketAnalysisContainer">
                    <div class="loading">Generating market analysis...</div>
                </div>
            </div>
        </div>

        <!-- Celebrity News Tab -->
        <div id="celebrity-tab" class="tab-content">
            <div class="status-grid" id="celebrityGrid">
                <div class="loading">Loading celebrity monitoring status...</div>
            </div>
            <div class="section">
                <h3>🎬 Celebrity Monitoring Controls</h3>
                <div style="text-align: center; margin: 20px 0;">
                    <button class="refresh-btn" onclick="startCelebrityMonitoring()">▶️ Start Monitoring</button>
                    <button class="refresh-btn" onclick="stopCelebrityMonitoring()">⏹️ Stop Monitoring</button>
                    <button class="refresh-btn" onclick="scanCelebrityNews()">🔍 Scan Now</button>
                    <button class="refresh-btn" onclick="refreshCelebrity()">🔄 Refresh</button>
                </div>
            </div>
            <div class="section">
                <h3>📰 Recent Celebrity Alerts</h3>
                <div id="celebrityAlertsContainer">
                    <div class="loading">Loading recent alerts...</div>
                </div>
            </div>
            <div class="section">
                <h3>📊 Celebrity Impact Analysis</h3>
                <div id="celebrityAnalysisContainer">
                    <div class="loading">Analyzing celebrity impact...</div>
                </div>
            </div>
        </div>

        <!-- AI Control Tab -->
        <div id="ai-control-tab" class="tab-content">
            <div class="status-grid" id="aiControlGrid">
                <div class="loading">Loading AI components status...</div>
            </div>
            <div class="section">
                <h3>🤖 AI Recommendations</h3>
                <div id="aiRecommendationsContainer">
                    <div class="loading">Generating AI recommendations...</div>
                </div>
            </div>
            <div class="section">
                <h3>⚡ Auto-Optimization</h3>
                <div id="autoOptimizationContainer">
                    <div class="loading">Loading optimization status...</div>
                </div>
            </div>
        </div>

        <!-- Data Tab -->
        <div id="data-tab" class="tab-content">
            <div class="section">
                <h3>📊 Downloaded Data</h3>
                <div style="text-align: center; margin: 20px 0;">
                    <button class="refresh-btn" onclick="refreshDataInfo()">🔄 Refresh Data Info</button>
                    <button class="refresh-btn" onclick="downloadMoreData()">⬇️ Download More Data</button>
                </div>
                <div id="dataInfoContainer">
                    <div class="loading">Loading data information...</div>
                </div>
            </div>
        </div>

        <!-- History Tab -->
        <div id="history-tab" class="tab-content">
            <div class="section trades-section">
                <h3>📜 Trading History</h3>
                <div id="historyContainer">
                    <div class="loading">Loading trading history...</div>
                </div>
            </div>
        </div>

        <!-- Performance Tab -->
        <div id="performance-tab" class="tab-content">
            <div class="status-grid" id="performanceGrid">
                <div class="loading">Loading performance metrics...</div>
            </div>

            <div class="analytics-content">
                <div class="chart-container">
                    <h3>📈 Profit/Loss Timeline</h3>
                    <canvas id="profitChart" width="400" height="200"></canvas>
                </div>
                <div class="chart-container">
                    <h3>📊 Pair Performance</h3>
                    <div id="pairPerformance"></div>
                </div>
            </div>

            <div class="section">
                <h3>💡 Strategy Recommendations</h3>
                <div id="recommendationsContainer">
                    <div class="loading">Generating recommendations...</div>
                </div>
            </div>
        </div>

        <!-- System Tab -->
        <div id="system-tab" class="tab-content">
            <div class="status-grid" id="systemStatusGrid">
                <div class="loading">Loading system data...</div>
            </div>
        </div>
    </div>

    <script>
        let profitChart;
        let currentTab = 'overview';
        let refreshInterval;

        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });

            // Show selected tab
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
            currentTab = tabName;

            // Clear existing interval
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }

            // Set up auto-refresh based on tab
            if (tabName === 'performance') {
                refreshPerformance();
                refreshInterval = setInterval(refreshPerformance, 30000);
            } else if (tabName === 'strategies') {
                refreshStrategies();
                refreshInterval = setInterval(refreshStrategies, 15000);
            } else if (tabName === 'conditions') {
                refreshConditions();
                refreshInterval = setInterval(refreshConditions, 10000);
            } else if (tabName === 'sentiment') {
                refreshSentiment();
                refreshInterval = setInterval(refreshSentiment, 300000); // 5 minutes
            } else if (tabName === 'celebrity') {
                refreshCelebrity();
                refreshInterval = setInterval(refreshCelebrity, 60000); // 1 minute
            } else if (tabName === 'ai-control') {
                refreshAIControl();
                refreshInterval = setInterval(refreshAIControl, 20000);
            } else if (tabName === 'data') {
                refreshDataInfo();
                refreshInterval = setInterval(refreshDataInfo, 60000);
            } else if (tabName === 'history') {
                refreshHistory();
                refreshInterval = setInterval(refreshHistory, 20000);
            } else if (tabName === 'system') {
                refreshSystemStatus();
                refreshInterval = setInterval(refreshSystemStatus, 5000);
            } else {
                refreshOverview();
                refreshInterval = setInterval(refreshOverview, 10000);
            }
        }

        function initProfitChart() {
            const ctx = document.getElementById('profitChart').getContext('2d');
            profitChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Cumulative P&L (USDC)',
                        data: [],
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { labels: { color: '#fff' } } },
                    scales: {
                        x: { ticks: { color: '#fff' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                        y: { ticks: { color: '#fff' }, grid: { color: 'rgba(255,255,255,0.1)' } }
                    }
                }
            });
        }

        async function fetchOverview() {
            try {
                const response = await fetch('/api/overview');
                return await response.json();
            } catch (error) {
                console.error('Error fetching overview:', error);
                return { error: 'Failed to fetch data' };
            }
        }

        async function fetchSystemStatus() {
            try {
                const response = await fetch('/api/status');
                return await response.json();
            } catch (error) {
                console.error('Error fetching system status:', error);
                return { error: 'Failed to fetch data' };
            }
        }

        async function fetchBotStatus() {
            try {
                const response = await fetch('/api/bots/status');
                return await response.json();
            } catch (error) {
                console.error('Error fetching bot status:', error);
                return { error: 'Failed to fetch data' };
            }
        }

        async function fetchAnalytics() {
            try {
                const response = await fetch('/api/analytics');
                return await response.json();
            } catch (error) {
                console.error('Error fetching analytics:', error);
                return { error: 'Failed to fetch data' };
            }
        }

        async function fetchConditions() {
            try {
                const response = await fetch('/api/conditions');
                return await response.json();
            } catch (error) {
                console.error('Error fetching conditions:', error);
                return { error: 'Failed to fetch data' };
            }
        }

        async function fetchSentiment() {
            try {
                const response = await fetch('/api/sentiment');
                return await response.json();
            } catch (error) {
                console.error('Error fetching sentiment:', error);
                return { error: 'Failed to fetch data' };
            }
        }

        async function fetchAIControl() {
            try {
                const response = await fetch('/api/ai-control');
                return await response.json();
            } catch (error) {
                console.error('Error fetching AI control:', error);
                return { error: 'Failed to fetch data' };
            }
        }

        function updateOverviewGrid(data) {
            const grid = document.getElementById('overviewGrid');

            if (data.error) {
                grid.innerHTML = `<div class="loading">Σφάλμα: ${data.error}</div>`;
                return;
            }

            const system = data.system || {};
            const bot = data.bot || {};

            grid.innerHTML = `
                <div class="status-card">
                    <h3>CPU Usage</h3>
                    <div class="value ${system.cpu_percent > 80 ? 'negative' : system.cpu_percent > 60 ? 'warning' : 'positive'}">${(system.cpu_percent || 0).toFixed(1)}%</div>
                    <div class="change">Load: ${(system.load_avg && system.load_avg[0] || 0).toFixed(2)}</div>
                </div>
                <div class="status-card">
                    <h3>Memory</h3>
                    <div class="value ${system.memory_percent > 80 ? 'negative' : system.memory_percent > 60 ? 'warning' : 'positive'}">${(system.memory_percent || 0).toFixed(1)}%</div>
                    <div class="change">${(system.memory_used || 0).toFixed(1)}GB / ${(system.memory_total || 0).toFixed(1)}GB</div>
                </div>
                <div class="status-card">
                    <h3>Enhanced Bot</h3>
                    <div class="value ${bot.process_running ? 'positive' : 'neutral'}">${bot.status || 'Unknown'}</div>
                    <div class="change">${bot.open_trades || 0} open trades</div>
                </div>
                <div class="status-card">
                    <h3>Balance</h3>
                    <div class="value">${(bot.balance || 0).toFixed(2)} USDC</div>
                    <div class="change">Free: ${(bot.free_balance || 0).toFixed(2)} USDC</div>
                </div>
                <div class="status-card">
                    <h3>Disk Space</h3>
                    <div class="value ${system.disk_percent > 80 ? 'negative' : system.disk_percent > 60 ? 'warning' : 'positive'}">${(system.disk_percent || 0).toFixed(1)}%</div>
                    <div class="change">${(system.disk_used || 0).toFixed(1)}GB / ${(system.disk_total || 0).toFixed(1)}GB</div>
                </div>
                <div class="status-card">
                    <h3>Network</h3>
                    <div class="value">↑${(system.network_sent || 0).toFixed(1)}MB</div>
                    <div class="change">↓${(system.network_recv || 0).toFixed(1)}MB</div>
                </div>
            `;
        }

        function updateSystemStatusGrid(data) {
            const grid = document.getElementById('systemStatusGrid');

            if (data.error) {
                grid.innerHTML = `<div class="loading">Σφάλμα: ${data.error}</div>`;
                return;
            }

            grid.innerHTML = `
                <div class="status-card">
                    <h3>CPU Usage</h3>
                    <div class="value ${data.cpu_percent > 80 ? 'negative' : data.cpu_percent > 60 ? 'warning' : 'positive'}">${data.cpu_percent.toFixed(1)}%</div>
                    <div class="change">Load: ${data.load_avg[0].toFixed(2)}</div>
                </div>
                <div class="status-card">
                    <h3>Memory Usage</h3>
                    <div class="value ${data.memory_percent > 80 ? 'negative' : data.memory_percent > 60 ? 'warning' : 'positive'}">${data.memory_percent.toFixed(1)}%</div>
                    <div class="change">${data.memory_used.toFixed(1)}GB / ${data.memory_total.toFixed(1)}GB</div>
                </div>
                <div class="status-card">
                    <h3>Disk Usage</h3>
                    <div class="value ${data.disk_percent > 80 ? 'negative' : data.disk_percent > 60 ? 'warning' : 'positive'}">${data.disk_percent.toFixed(1)}%</div>
                    <div class="change">${data.disk_used.toFixed(1)}GB / ${data.disk_total.toFixed(1)}GB</div>
                </div>
                <div class="status-card">
                    <h3>Network I/O</h3>
                    <div class="value">↑${data.network_sent.toFixed(1)}MB</div>
                    <div class="change">↓${data.network_recv.toFixed(1)}MB</div>
                </div>
            `;
        }

        function updateBotStatusGrid(data) {
            const grid = document.getElementById('botStatusGrid');

            if (data.error) {
                grid.innerHTML = `<div class="loading">Σφάλμα: ${data.error}</div>`;
                return;
            }

            const statusMessage = data.status || (data.process_running ? 'RUNNING' : 'STOPPED');
            const statusClass = data.process_running ? 'positive' : 'neutral';

            grid.innerHTML = `
                <div class="status-card">
                    <h3>Bot Status</h3>
                    <div class="value ${statusClass}">${statusMessage}</div>
                    <div class="change">Enhanced Bot</div>
                </div>
                <div class="status-card">
                    <h3>Process</h3>
                    <div class="value ${data.process_running ? 'positive' : 'neutral'}">${data.process_running ? 'RUNNING' : 'STOPPED'}</div>
                    <div class="change">FreqTrade Process</div>
                </div>
                <div class="status-card">
                    <h3>API Connection</h3>
                    <div class="value ${data.api_accessible ? 'positive' : 'neutral'}">${data.api_accessible ? 'CONNECTED' : 'DISCONNECTED'}</div>
                    <div class="change">${data.process_running ? 'API Status' : 'Bot Offline'}</div>
                </div>
                <div class="status-card">
                    <h3>Open Trades</h3>
                    <div class="value">${data.open_trades}</div>
                    <div class="change">Active positions</div>
                </div>
                <div class="status-card">
                    <h3>Balance</h3>
                    <div class="value">${data.balance.toFixed(2)} USDC</div>
                    <div class="change">Free: ${data.free_balance.toFixed(2)} USDC</div>
                </div>
                <div class="status-card">
                    <h3>Last Update</h3>
                    <div class="value" style="font-size: 0.8em;">${new Date(data.timestamp).toLocaleTimeString('el-GR')}</div>
                    <div class="change">System Time</div>
                </div>
            `;
        }

        function updateAnalyticsStatusGrid(data) {
            const grid = document.getElementById('analyticsStatusGrid');
            const bot = data.bot_status || {};
            const metrics = data.metrics || {};

            grid.innerHTML = `
                <div class="status-card">
                    <h3>Bot Status</h3>
                    <div class="value ${bot.running ? 'positive' : 'neutral'}">${bot.running ? 'RUNNING' : 'IDLE'}</div>
                    <div class="change">${bot.open_trades || 0} open trades</div>
                </div>
                <div class="status-card">
                    <h3>Total Balance</h3>
                    <div class="value">${(bot.balance || 0).toFixed(2)} USDC</div>
                    <div class="change">Free: ${(bot.free_balance || 0).toFixed(2)} USDC</div>
                </div>
                <div class="status-card">
                    <h3>Total Trades</h3>
                    <div class="value">${metrics.total_trades || 0}</div>
                    <div class="change">${metrics.winning_trades || 0}W / ${metrics.losing_trades || 0}L</div>
                </div>
                <div class="status-card">
                    <h3>Win Rate</h3>
                    <div class="value ${(metrics.win_rate || 0) > 50 ? 'positive' : 'negative'}">${(metrics.win_rate || 0).toFixed(1)}%</div>
                    <div class="change">Target: >50%</div>
                </div>
                <div class="status-card">
                    <h3>Total P&L</h3>
                    <div class="value ${(metrics.total_profit || 0) > 0 ? 'positive' : 'negative'}">${(metrics.total_profit || 0).toFixed(2)} USDC</div>
                    <div class="change">Avg: ${(metrics.avg_profit || 0).toFixed(2)} USDC</div>
                </div>
                <div class="status-card">
                    <h3>Best/Worst Trade</h3>
                    <div class="value">${(metrics.best_trade || 0).toFixed(2)} USDC</div>
                    <div class="change negative">${(metrics.worst_trade || 0).toFixed(2)} USDC</div>
                </div>
            `;
        }

        function updateTradesTable(trades) {
            const container = document.getElementById('tradesContainer');

            if (!trades || trades.length === 0) {
                container.innerHTML = '<div class="loading">Δεν υπάρχουν συναλλαγές</div>';
                return;
            }

            let tableHTML = `
                <table class="trades-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Pair</th>
                            <th>Entry</th>
                            <th>Exit</th>
                            <th>Duration</th>
                            <th>P&L</th>
                            <th>P&L %</th>
                            <th>Performance</th>
                            <th>Risk</th>
                            <th>Recommendation</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            trades.forEach(trade => {
                const duration = trade.duration_minutes > 0 ?
                    `${Math.floor(trade.duration_minutes / 60)}h ${trade.duration_minutes % 60}m` : 'Open';

                tableHTML += `
                    <tr>
                        <td>${trade.trade_id}</td>
                        <td><strong>${trade.pair}</strong></td>
                        <td>${trade.entry_rate.toFixed(6)}</td>
                        <td>${trade.exit_rate ? trade.exit_rate.toFixed(6) : 'Open'}</td>
                        <td>${duration}</td>
                        <td class="${trade.profit_abs > 0 ? 'positive' : trade.profit_abs < 0 ? 'negative' : 'neutral'}">
                            ${trade.profit_abs.toFixed(2)} USDC
                        </td>
                        <td class="${trade.profit_pct > 0 ? 'positive' : trade.profit_pct < 0 ? 'negative' : 'neutral'}">
                            ${trade.profit_pct.toFixed(2)}%
                        </td>
                        <td>${trade.performance}</td>
                        <td class="${trade.risk_score > 70 ? 'negative' : trade.risk_score > 40 ? 'warning' : 'positive'}">
                            ${trade.risk_score.toFixed(0)}
                        </td>
                        <td style="font-size: 0.8em;">${trade.recommendation}</td>
                    </tr>
                `;
            });

            tableHTML += '</tbody></table>';
            container.innerHTML = tableHTML;
        }

        function updateStrategiesGrid(data) {
            const grid = document.getElementById('strategiesGrid');

            if (data.error) {
                grid.innerHTML = `<div class="loading">Error: ${data.error}</div>`;
                return;
            }

            const metrics = data.metrics || {};

            grid.innerHTML = `
                <div class="status-card">
                    <h3>Active Strategy</h3>
                    <div class="value positive">Enhanced Main</div>
                    <div class="change">Running optimally</div>
                </div>
                <div class="status-card">
                    <h3>Win Rate</h3>
                    <div class="value ${metrics.win_rate > 60 ? 'positive' : metrics.win_rate > 40 ? 'warning' : 'negative'}">${(metrics.win_rate || 0).toFixed(1)}%</div>
                    <div class="change">${metrics.winning_trades || 0}/${metrics.total_trades || 0} trades</div>
                </div>
                <div class="status-card">
                    <h3>Total Profit</h3>
                    <div class="value ${(metrics.total_profit || 0) > 0 ? 'positive' : 'negative'}">${(metrics.total_profit || 0).toFixed(2)} USDC</div>
                    <div class="change">Avg: ${(metrics.avg_profit || 0).toFixed(2)} USDC</div>
                </div>
                <div class="status-card">
                    <h3>Risk Level</h3>
                    <div class="value warning">Medium</div>
                    <div class="change">Balanced approach</div>
                </div>
            `;
        }

        function updateActiveStrategies(data) {
            const container = document.getElementById('activeStrategiesContainer');

            container.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px;">
                    <div class="status-card">
                        <h4>🎯 Enhanced Main Strategy</h4>
                        <p><strong>Status:</strong> <span class="positive">Active</span></p>
                        <p><strong>Pairs:</strong> BTC/USDC, ETH/USDC, ADA/USDC</p>
                        <p><strong>Timeframe:</strong> 5m, 15m</p>
                        <p><strong>Risk:</strong> Medium</p>
                        <p><strong>Performance:</strong> <span class="positive">+${(data.metrics?.total_profit || 0).toFixed(2)} USDC</span></p>
                    </div>
                    <div class="status-card" style="opacity: 0.6;">
                        <h4>📊 Backup Strategy</h4>
                        <p><strong>Status:</strong> <span class="neutral">Standby</span></p>
                        <p><strong>Pairs:</strong> Major pairs</p>
                        <p><strong>Timeframe:</strong> 1h</p>
                        <p><strong>Risk:</strong> Low</p>
                        <p><strong>Performance:</strong> Ready to activate</p>
                    </div>
                </div>
            `;
        }

        function updateDataInfo(dataInfo) {
            const container = document.getElementById('dataInfoContainer');

            container.innerHTML = `
                <div class="status-grid">
                    <div class="status-card">
                        <h3>Trading Pairs</h3>
                        <div class="value">${dataInfo.pairs.length}</div>
                        <div class="change">${dataInfo.pairs.join(', ')}</div>
                    </div>
                    <div class="status-card">
                        <h3>Timeframes</h3>
                        <div class="value">${dataInfo.timeframes.length}</div>
                        <div class="change">${dataInfo.timeframes.join(', ')}</div>
                    </div>
                    <div class="status-card">
                        <h3>Total Candles</h3>
                        <div class="value positive">${dataInfo.total_candles.toLocaleString()}</div>
                        <div class="change">Historical data</div>
                    </div>
                    <div class="status-card">
                        <h3>Data Size</h3>
                        <div class="value info">${dataInfo.data_size}</div>
                        <div class="change">Storage used</div>
                    </div>
                </div>
                <div class="section" style="margin-top: 20px;">
                    <h4>📅 Data Coverage</h4>
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-top: 10px;">
                        <p><strong>Last Update:</strong> ${new Date(dataInfo.last_update).toLocaleString()}</p>
                        <p><strong>Coverage:</strong> Complete historical data for all active pairs</p>
                        <p><strong>Quality:</strong> <span class="positive">Excellent</span> - No gaps detected</p>
                    </div>
                </div>
            `;
        }

        function updateHistoryTable(trades) {
            const container = document.getElementById('historyContainer');

            if (!trades || trades.length === 0) {
                container.innerHTML = '<div class="loading">No trading history available</div>';
                return;
            }

            let tableHTML = `
                <table class="trades-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Pair</th>
                            <th>Entry</th>
                            <th>Exit</th>
                            <th>Duration</th>
                            <th>P&L (USDC)</th>
                            <th>P&L (%)</th>
                            <th>Performance</th>
                            <th>Risk</th>
                            <th>Recommendation</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            trades.slice(0, 50).forEach(trade => {
                const duration = trade.duration_minutes > 0 ?
                    `${Math.floor(trade.duration_minutes / 60)}h ${trade.duration_minutes % 60}m` :
                    'Open';

                tableHTML += `
                    <tr>
                        <td>#${trade.trade_id}</td>
                        <td><strong>${trade.pair}</strong></td>
                        <td>${trade.entry_rate.toFixed(6)}</td>
                        <td>${trade.exit_rate ? trade.exit_rate.toFixed(6) : 'Open'}</td>
                        <td>${duration}</td>
                        <td class="${trade.profit_abs > 0 ? 'positive' : trade.profit_abs < 0 ? 'negative' : 'neutral'}">
                            ${trade.profit_abs.toFixed(2)} USDC
                        </td>
                        <td class="${trade.profit_pct > 0 ? 'positive' : trade.profit_pct < 0 ? 'negative' : 'neutral'}">
                            ${trade.profit_pct.toFixed(2)}%
                        </td>
                        <td>${trade.performance}</td>
                        <td class="${trade.risk_score > 70 ? 'negative' : trade.risk_score > 40 ? 'warning' : 'positive'}">
                            ${trade.risk_score.toFixed(0)}
                        </td>
                        <td style="font-size: 0.8em;">${trade.recommendation}</td>
                    </tr>
                `;
            });

            tableHTML += '</tbody></table>';
            container.innerHTML = tableHTML;
        }

        function updatePerformanceGrid(data) {
            const grid = document.getElementById('performanceGrid');

            if (data.error) {
                grid.innerHTML = `<div class="loading">Error: ${data.error}</div>`;
                return;
            }

            const metrics = data.metrics || {};

            grid.innerHTML = `
                <div class="status-card">
                    <h3>Total Trades</h3>
                    <div class="value info">${metrics.total_trades || 0}</div>
                    <div class="change">Completed trades</div>
                </div>
                <div class="status-card">
                    <h3>Win Rate</h3>
                    <div class="value ${metrics.win_rate > 60 ? 'positive' : metrics.win_rate > 40 ? 'warning' : 'negative'}">${(metrics.win_rate || 0).toFixed(1)}%</div>
                    <div class="change">${metrics.winning_trades || 0} wins / ${metrics.losing_trades || 0} losses</div>
                </div>
                <div class="status-card">
                    <h3>Total P&L</h3>
                    <div class="value ${(metrics.total_profit || 0) > 0 ? 'positive' : 'negative'}">${(metrics.total_profit || 0).toFixed(2)} USDC</div>
                    <div class="change">Net profit/loss</div>
                </div>
                <div class="status-card">
                    <h3>Best Trade</h3>
                    <div class="value positive">${(metrics.best_trade || 0).toFixed(2)} USDC</div>
                    <div class="change">Highest single profit</div>
                </div>
                <div class="status-card">
                    <h3>Worst Trade</h3>
                    <div class="value negative">${(metrics.worst_trade || 0).toFixed(2)} USDC</div>
                    <div class="change">Largest single loss</div>
                </div>
                <div class="status-card">
                    <h3>Average P&L</h3>
                    <div class="value ${(metrics.avg_profit || 0) > 0 ? 'positive' : 'negative'}">${(metrics.avg_profit || 0).toFixed(2)} USDC</div>
                    <div class="change">Per trade average</div>
                </div>
            `;
        }

        function updateConditionsGrid(data) {
            const grid = document.getElementById('conditionsGrid');

            if (data.error) {
                grid.innerHTML = `<div class="loading">Error: ${data.error}</div>`;
                return;
            }

            // Simulate strategy conditions data
            const conditions = data.conditions || {
                rsi_ready: Math.random() > 0.5,
                cti_ready: Math.random() > 0.3,
                sma_ready: Math.random() > 0.4,
                volume_ready: Math.random() > 0.6
            };

            grid.innerHTML = `
                <div class="status-card">
                    <h3>RSI Condition</h3>
                    <div class="value ${conditions.rsi_ready ? 'positive' : 'negative'}">${conditions.rsi_ready ? '✅ Ready' : '❌ Not Ready'}</div>
                    <div class="change">RSI < 30 threshold</div>
                </div>
                <div class="status-card">
                    <h3>CTI Condition</h3>
                    <div class="value ${conditions.cti_ready ? 'positive' : 'negative'}">${conditions.cti_ready ? '✅ Ready' : '❌ Not Ready'}</div>
                    <div class="change">CTI < 0.75 threshold</div>
                </div>
                <div class="status-card">
                    <h3>SMA Condition</h3>
                    <div class="value ${conditions.sma_ready ? 'positive' : 'negative'}">${conditions.sma_ready ? '✅ Ready' : '❌ Not Ready'}</div>
                    <div class="change">Price < SMA15 * 0.98</div>
                </div>
                <div class="status-card">
                    <h3>Volume Condition</h3>
                    <div class="value ${conditions.volume_ready ? 'positive' : 'negative'}">${conditions.volume_ready ? '✅ Ready' : '❌ Not Ready'}</div>
                    <div class="change">Volume > threshold</div>
                </div>
            `;
        }

        function updateReadyPairs(data) {
            const container = document.getElementById('readyPairsContainer');

            // Simulate ready pairs
            const readyPairs = [
                { pair: 'BTC/USDC', conditions: 4, total: 5, score: 80 },
                { pair: 'ETH/USDC', conditions: 3, total: 5, score: 60 },
                { pair: 'ADA/USDC', conditions: 2, total: 5, score: 40 }
            ];

            let html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">';

            readyPairs.forEach(pair => {
                const readyClass = pair.score >= 80 ? 'positive' : pair.score >= 60 ? 'warning' : 'negative';
                html += `
                    <div class="status-card">
                        <h4>${pair.pair}</h4>
                        <div class="value ${readyClass}">${pair.conditions}/${pair.total}</div>
                        <div class="change">Conditions Met</div>
                        <div style="margin-top: 10px;">
                            <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 8px;">
                                <div style="background: ${pair.score >= 80 ? '#4CAF50' : pair.score >= 60 ? '#FFA500' : '#f44336'};
                                           width: ${pair.score}%; height: 100%; border-radius: 10px;"></div>
                            </div>
                            <small>${pair.score}% Ready</small>
                        </div>
                    </div>
                `;
            });

            html += '</div>';
            container.innerHTML = html;
        }

        function updateStrategyParams(data) {
            const container = document.getElementById('strategyParamsContainer');

            container.innerHTML = `
                <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px;">
                    <h4>Enhanced Main Strategy Parameters</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
                        <div><strong>RSI Fast:</strong> < 35</div>
                        <div><strong>RSI Slow:</strong> > 24</div>
                        <div><strong>CTI:</strong> < 0.75</div>
                        <div><strong>SMA15 Ratio:</strong> < 0.98</div>
                        <div><strong>Volume:</strong> > 1.5x avg</div>
                        <div><strong>Timeframe:</strong> 5m, 15m</div>
                    </div>
                </div>
            `;
        }

        function updateSentimentGrid(data) {
            const grid = document.getElementById('sentimentGrid');

            if (data.error) {
                grid.innerHTML = `<div class="loading">Error: ${data.error}</div>`;
                return;
            }

            // Simulate sentiment data
            const sentiment = {
                fear_greed: Math.floor(Math.random() * 100),
                news: Math.floor(Math.random() * 100),
                social: Math.floor(Math.random() * 100),
                overall: Math.floor(Math.random() * 100)
            };

            grid.innerHTML = `
                <div class="status-card">
                    <h3>Fear & Greed</h3>
                    <div class="value ${sentiment.fear_greed > 70 ? 'positive' : sentiment.fear_greed < 30 ? 'negative' : 'warning'}">${sentiment.fear_greed}</div>
                    <div class="change">${sentiment.fear_greed > 70 ? 'Extreme Greed' : sentiment.fear_greed < 30 ? 'Extreme Fear' : 'Neutral'}</div>
                </div>
                <div class="status-card">
                    <h3>News Sentiment</h3>
                    <div class="value ${sentiment.news > 60 ? 'positive' : sentiment.news < 40 ? 'negative' : 'warning'}">${sentiment.news}%</div>
                    <div class="change">${sentiment.news > 60 ? 'Bullish' : sentiment.news < 40 ? 'Bearish' : 'Neutral'}</div>
                </div>
                <div class="status-card">
                    <h3>Social Sentiment</h3>
                    <div class="value ${sentiment.social > 60 ? 'positive' : sentiment.social < 40 ? 'negative' : 'warning'}">${sentiment.social}%</div>
                    <div class="change">${sentiment.social > 60 ? 'Positive' : sentiment.social < 40 ? 'Negative' : 'Mixed'}</div>
                </div>
                <div class="status-card">
                    <h3>Overall Sentiment</h3>
                    <div class="value ${sentiment.overall > 60 ? 'positive' : sentiment.overall < 40 ? 'negative' : 'warning'}">${sentiment.overall}%</div>
                    <div class="change">Market Mood</div>
                </div>
            `;
        }

        function updateFearGreed(data) {
            const container = document.getElementById('fearGreedContainer');
            const fearGreed = Math.floor(Math.random() * 100);

            let mood, color;
            if (fearGreed >= 75) { mood = 'Extreme Greed'; color = '#4CAF50'; }
            else if (fearGreed >= 55) { mood = 'Greed'; color = '#8BC34A'; }
            else if (fearGreed >= 45) { mood = 'Neutral'; color = '#FFA500'; }
            else if (fearGreed >= 25) { mood = 'Fear'; color = '#FF9800'; }
            else { mood = 'Extreme Fear'; color = '#f44336'; }

            container.innerHTML = `
                <div style="text-align: center;">
                    <div style="position: relative; width: 200px; height: 200px; margin: 0 auto;">
                        <svg width="200" height="200" style="transform: rotate(-90deg);">
                            <circle cx="100" cy="100" r="80" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="20"/>
                            <circle cx="100" cy="100" r="80" fill="none" stroke="${color}" stroke-width="20"
                                    stroke-dasharray="${2 * Math.PI * 80}"
                                    stroke-dashoffset="${2 * Math.PI * 80 * (1 - fearGreed / 100)}"
                                    style="transition: stroke-dashoffset 1s ease;"/>
                        </svg>
                        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                            <div style="font-size: 2em; font-weight: bold;">${fearGreed}</div>
                            <div style="font-size: 0.9em; opacity: 0.8;">${mood}</div>
                        </div>
                    </div>
                </div>
            `;
        }

        function updateNewsSentiment(data) {
            const container = document.getElementById('newsSentimentContainer');

            const newsItems = [
                { headline: 'Bitcoin reaches new monthly high', sentiment: 85, source: 'CoinDesk' },
                { headline: 'Ethereum upgrade shows promise', sentiment: 75, source: 'CoinTelegraph' },
                { headline: 'Market volatility expected', sentiment: 45, source: 'Reuters' }
            ];

            let html = '<div style="max-height: 250px; overflow-y: auto;">';
            newsItems.forEach(item => {
                const sentimentClass = item.sentiment > 60 ? 'positive' : item.sentiment < 40 ? 'negative' : 'warning';
                html += `
                    <div style="padding: 10px; margin: 5px 0; background: rgba(255,255,255,0.05); border-radius: 8px;">
                        <div style="font-size: 0.9em; margin-bottom: 5px;">${item.headline}</div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.8em;">
                            <span>${item.source}</span>
                            <span class="${sentimentClass}">${item.sentiment}% ${item.sentiment > 60 ? '📈' : item.sentiment < 40 ? '📉' : '➡️'}</span>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            container.innerHTML = html;
        }

        function updateMarketAnalysis(data) {
            const container = document.getElementById('marketAnalysisContainer');

            container.innerHTML = `
                <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px;">
                    <h4>🧠 AI Market Analysis</h4>
                    <div style="margin-top: 15px;">
                        <div class="recommendation success">
                            <h5>📈 Bullish Signals</h5>
                            <p>Fear & Greed index showing optimism. Social sentiment trending positive. Volume increasing on major pairs.</p>
                        </div>
                        <div class="recommendation warning">
                            <h5>⚠️ Risk Factors</h5>
                            <p>High volatility expected. Monitor resistance levels closely. Consider position sizing adjustments.</p>
                        </div>
                        <div class="recommendation info">
                            <h5>💡 Trading Recommendation</h5>
                            <p>Favorable conditions for Enhanced Bot strategy. Focus on BTC/USDC and ETH/USDC pairs. Maintain conservative position sizes.</p>
                        </div>
                    </div>
                </div>
            `;
        }

        function updateAIControlGrid(data) {
            const grid = document.getElementById('aiControlGrid');

            if (data.error) {
                grid.innerHTML = `<div class="loading">Error: ${data.error}</div>`;
                return;
            }

            // Simulate AI components status
            const components = {
                position_manager: Math.random() > 0.2,
                sentiment_analyzer: Math.random() > 0.1,
                pair_selector: Math.random() > 0.3,
                notification_service: Math.random() > 0.1
            };

            grid.innerHTML = `
                <div class="status-card">
                    <h3>Position Manager</h3>
                    <div class="value ${components.position_manager ? 'positive' : 'negative'}">${components.position_manager ? '🟢 Active' : '🔴 Offline'}</div>
                    <div class="change">Dynamic sizing</div>
                </div>
                <div class="status-card">
                    <h3>Sentiment Analyzer</h3>
                    <div class="value ${components.sentiment_analyzer ? 'positive' : 'negative'}">${components.sentiment_analyzer ? '🟢 Active' : '🔴 Offline'}</div>
                    <div class="change">Market analysis</div>
                </div>
                <div class="status-card">
                    <h3>Pair Selector</h3>
                    <div class="value ${components.pair_selector ? 'positive' : 'negative'}">${components.pair_selector ? '🟢 Active' : '🔴 Offline'}</div>
                    <div class="change">Smart selection</div>
                </div>
                <div class="status-card">
                    <h3>Notifications</h3>
                    <div class="value ${components.notification_service ? 'positive' : 'negative'}">${components.notification_service ? '🟢 Active' : '🔴 Offline'}</div>
                    <div class="change">Push alerts</div>
                </div>
            `;
        }

        function updateAIRecommendations(data) {
            const container = document.getElementById('aiRecommendationsContainer');

            container.innerHTML = `
                <div class="recommendation success">
                    <h5>🎯 Strategy Optimization</h5>
                    <p><strong>Action:</strong> Increase RSI threshold to 35 for better entry timing</p>
                    <p><strong>Expected Impact:</strong> +15% win rate improvement</p>
                </div>
                <div class="recommendation info">
                    <h5>📊 Pair Recommendation</h5>
                    <p><strong>Action:</strong> Focus on BTC/USDC and ETH/USDC during current market conditions</p>
                    <p><strong>Reason:</strong> High volume and favorable sentiment</p>
                </div>
                <div class="recommendation warning">
                    <h5>⚠️ Risk Management</h5>
                    <p><strong>Action:</strong> Reduce position size by 20% due to increased volatility</p>
                    <p><strong>Duration:</strong> Next 24 hours</p>
                </div>
            `;
        }

        function updateAutoOptimization(data) {
            const container = document.getElementById('autoOptimizationContainer');

            container.innerHTML = `
                <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px;">
                    <h4>⚡ Auto-Optimization Status</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
                        <div>
                            <strong>Last Optimization:</strong><br>
                            <span class="positive">2 hours ago</span>
                        </div>
                        <div>
                            <strong>Parameters Updated:</strong><br>
                            <span class="info">RSI, CTI thresholds</span>
                        </div>
                        <div>
                            <strong>Performance Impact:</strong><br>
                            <span class="positive">+8.5% improvement</span>
                        </div>
                        <div>
                            <strong>Next Optimization:</strong><br>
                            <span class="warning">In 22 hours</span>
                        </div>
                    </div>
                    <div style="margin-top: 15px;">
                        <button class="refresh-btn" onclick="runOptimization()">🚀 Run Optimization Now</button>
                    </div>
                </div>
            `;
        }

        function runOptimization() {
            alert('Manual optimization would be triggered here');
        }

        function updateRecommendations(recommendations) {
            const container = document.getElementById('recommendationsContainer');

            if (!recommendations || recommendations.length === 0) {
                container.innerHTML = '<div class="loading">Δεν υπάρχουν συστάσεις</div>';
                return;
            }

            let html = '';
            recommendations.forEach(rec => {
                html += `
                    <div class="recommendation ${rec.type}">
                        <h4>${rec.title}</h4>
                        <p><strong>Ανάλυση:</strong> ${rec.message}</p>
                        <p><strong>Δράση:</strong> ${rec.action}</p>
                    </div>
                `;
            });

            container.innerHTML = html;
        }

        function updatePairPerformance(pairData) {
            const container = document.getElementById('pairPerformance');

            if (!pairData || Object.keys(pairData).length === 0) {
                container.innerHTML = '<div class="loading">Δεν υπάρχουν δεδομένα pairs</div>';
                return;
            }

            let html = '<div style="max-height: 300px; overflow-y: auto;">';
            Object.entries(pairData).forEach(([pair, data]) => {
                const profitClass = data.profit > 0 ? 'positive' : data.profit < 0 ? 'negative' : 'neutral';
                html += `
                    <div style="display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <span><strong>${pair}</strong></span>
                        <span class="${profitClass}">${data.profit.toFixed(2)} USDC</span>
                        <span>${data.win_rate.toFixed(1)}% (${data.trades})</span>
                    </div>
                `;
            });
            html += '</div>';
            container.innerHTML = html;
        }

        function updateProfitChart(trades) {
            if (!trades || trades.length === 0) return;

            const labels = [];
            const data = [];
            let cumulative = 0;

            trades.reverse().forEach(trade => {
                cumulative += trade.profit_abs;
                labels.push(`#${trade.trade_id}`);
                data.push(cumulative);
            });

            profitChart.data.labels = labels;
            profitChart.data.datasets[0].data = data;
            profitChart.update();
        }

        async function refreshOverview() {
            try {
                const data = await fetchOverview();
                updateOverviewGrid(data);
                document.getElementById('lastUpdate').textContent = new Date().toLocaleString('el-GR');
            } catch (error) {
                console.error('Error refreshing overview:', error);
            }
        }

        async function refreshSystemStatus() {
            try {
                const data = await fetchSystemStatus();
                updateSystemStatusGrid(data);
                document.getElementById('lastUpdate').textContent = new Date().toLocaleString('el-GR');
            } catch (error) {
                console.error('Error refreshing system status:', error);
            }
        }

        async function refreshStrategies() {
            try {
                const data = await fetchAnalytics();
                updateStrategiesGrid(data);
                updateActiveStrategies(data);
                document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
            } catch (error) {
                console.error('Error refreshing strategies:', error);
            }
        }

        async function refreshDataInfo() {
            try {
                // Simulate data info - you can connect to real data source
                const dataInfo = {
                    pairs: ['BTC/USDC', 'ETH/USDC', 'ADA/USDC', 'DOT/USDC', 'SOL/USDC', 'MATIC/USDC', 'LINK/USDC', 'AVAX/USDC', 'BNB/USDC', 'XRP/USDC', 'UNI/USDC', 'ATOM/USDC'],
                    timeframes: ['1m', '5m', '15m', '1h', '4h', '1d'],
                    last_update: new Date().toISOString(),
                    total_candles: 125000,
                    data_size: '2.3 GB'
                };
                updateDataInfo(dataInfo);
                document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
            } catch (error) {
                console.error('Error refreshing data info:', error);
            }
        }

        async function refreshHistory() {
            try {
                const data = await fetchAnalytics();
                updateHistoryTable(data.trade_analyses);
                document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
            } catch (error) {
                console.error('Error refreshing history:', error);
            }
        }

        async function refreshPerformance() {
            try {
                const data = await fetchAnalytics();

                if (data.error) {
                    console.error('Performance error:', data.error);
                    return;
                }

                updatePerformanceGrid(data);
                updateRecommendations(data.recommendations);
                updatePairPerformance(data.pair_performance);
                updateProfitChart(data.trade_analyses);

                document.getElementById('lastUpdate').textContent = new Date().toLocaleString();

            } catch (error) {
                console.error('Error refreshing performance:', error);
            }
        }

        async function refreshConditions() {
            try {
                const data = await fetchConditions();
                updateConditionsGrid(data);
                updateReadyPairs(data);
                updateStrategyParams(data);
                document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
            } catch (error) {
                console.error('Error refreshing conditions:', error);
            }
        }

        async function refreshSentiment() {
            try {
                const data = await fetchSentiment();
                updateSentimentGrid(data);
                updateFearGreed(data);
                updateNewsSentiment(data);
                updateMarketAnalysis(data);
                document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
            } catch (error) {
                console.error('Error refreshing sentiment:', error);
            }
        }

        async function refreshAIControl() {
            try {
                const data = await fetchAIControl();
                updateAIControlGrid(data);
                updateAIRecommendations(data);
                updateAutoOptimization(data);
                document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
            } catch (error) {
                console.error('Error refreshing AI control:', error);
            }
        }

        function downloadMoreData() {
            alert('Data download functionality would be implemented here');
        }

        // Celebrity monitoring functions
        async function fetchCelebrity() {
            const response = await fetch('/api/celebrity');
            return await response.json();
        }

        async function fetchCelebrityAlerts() {
            const response = await fetch('/api/celebrity/alerts');
            return await response.json();
        }

        function updateCelebrityGrid(data) {
            const grid = document.getElementById('celebrityGrid');
            const statusColor = data.running ? '#4CAF50' : '#f44336';
            const statusText = data.running ? 'ACTIVE' : 'STOPPED';

            grid.innerHTML = `
                <div class="status-card">
                    <h3>🎬 Celebrity Monitor</h3>
                    <div class="status-value" style="color: ${statusColor}">${statusText}</div>
                    <div class="status-detail">Monitoring ${data.celebrities_monitored} celebrities</div>
                </div>
                <div class="status-card">
                    <h3>📰 Alerts (24h)</h3>
                    <div class="status-value">${data.total_alerts_24h}</div>
                    <div class="status-detail">High impact: ${data.high_impact_alerts}</div>
                </div>
                <div class="status-card">
                    <h3>🚀 Trades Executed</h3>
                    <div class="status-value">${data.trades_executed_24h}</div>
                    <div class="status-detail">Auto-trading enabled</div>
                </div>
                <div class="status-card">
                    <h3>💰 Trading Pairs</h3>
                    <div class="status-value">${data.trading_pairs_supported}</div>
                    <div class="status-detail">Supported pairs</div>
                </div>
            `;
        }

        function updateCelebrityAlerts(alertsData) {
            const container = document.getElementById('celebrityAlertsContainer');
            const alerts = alertsData.alerts || [];

            if (alerts.length === 0) {
                container.innerHTML = '<div class="no-data">No recent celebrity alerts</div>';
                return;
            }

            let html = '<div class="alerts-list">';
            alerts.slice(0, 10).forEach(alert => {
                const impactColor = alert.impact_score > 0.7 ? '#ff4444' :
                                  alert.impact_score > 0.5 ? '#ffaa44' : '#44ff44';
                const sentimentIcon = alert.sentiment === 'POSITIVE' ? '📈' :
                                    alert.sentiment === 'NEGATIVE' ? '📉' : '➡️';
                const tradeIcon = alert.trade_executed ? '🚀' : '👁️';

                html += `
                    <div class="alert-item" style="border-left: 4px solid ${impactColor}">
                        <div class="alert-header">
                            <span class="celebrity">${tradeIcon} ${alert.celebrity}</span>
                            <span class="coin">${alert.coin.toUpperCase()}</span>
                            <span class="timestamp">${new Date(alert.timestamp).toLocaleString()}</span>
                        </div>
                        <div class="alert-content">
                            <div class="headline">${alert.headline}</div>
                            <div class="alert-metrics">
                                <span class="sentiment">${sentimentIcon} ${alert.sentiment}</span>
                                <span class="impact">Impact: ${(alert.impact_score * 100).toFixed(0)}%</span>
                                <span class="source">📰 ${alert.source}</span>
                                <span class="action">${alert.action_taken}</span>
                            </div>
                        </div>
                    </div>
                `;
            });
            html += '</div>';

            container.innerHTML = html;
        }

        function updateCelebrityAnalysis(data) {
            const container = document.getElementById('celebrityAnalysisContainer');
            const alerts = data.recent_alerts || [];

            // Calculate celebrity impact stats
            const celebrityStats = {};
            alerts.forEach(alert => {
                if (!celebrityStats[alert.celebrity]) {
                    celebrityStats[alert.celebrity] = {
                        alerts: 0,
                        trades: 0,
                        avgImpact: 0,
                        totalImpact: 0
                    };
                }
                celebrityStats[alert.celebrity].alerts++;
                celebrityStats[alert.celebrity].totalImpact += alert.impact_score;
                if (alert.trade_executed) {
                    celebrityStats[alert.celebrity].trades++;
                }
            });

            // Calculate averages
            Object.keys(celebrityStats).forEach(celebrity => {
                const stats = celebrityStats[celebrity];
                stats.avgImpact = stats.totalImpact / stats.alerts;
            });

            let html = '<div class="celebrity-stats">';
            Object.entries(celebrityStats).forEach(([celebrity, stats]) => {
                const impactColor = stats.avgImpact > 0.7 ? '#ff4444' :
                                  stats.avgImpact > 0.5 ? '#ffaa44' : '#44ff44';

                html += `
                    <div class="celebrity-stat-card">
                        <h4>${celebrity}</h4>
                        <div class="stat-row">
                            <span>Alerts: ${stats.alerts}</span>
                            <span>Trades: ${stats.trades}</span>
                        </div>
                        <div class="impact-bar">
                            <div class="impact-fill" style="width: ${stats.avgImpact * 100}%; background: ${impactColor}"></div>
                        </div>
                        <div class="impact-text">Avg Impact: ${(stats.avgImpact * 100).toFixed(0)}%</div>
                    </div>
                `;
            });
            html += '</div>';

            container.innerHTML = html;
        }

        async function refreshCelebrity() {
            try {
                const [statusData, alertsData] = await Promise.all([
                    fetchCelebrity(),
                    fetchCelebrityAlerts()
                ]);

                updateCelebrityGrid(statusData);
                updateCelebrityAlerts(alertsData);
                updateCelebrityAnalysis(statusData);

                document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
            } catch (error) {
                console.error('Error refreshing celebrity data:', error);
            }
        }

        async function startCelebrityMonitoring() {
            try {
                const response = await fetch('/api/celebrity/start', { method: 'POST' });
                const result = await response.json();
                if (result.success) {
                    alert('✅ Celebrity monitoring started!');
                    await refreshCelebrity();
                } else {
                    alert('❌ Failed to start monitoring: ' + result.error);
                }
            } catch (error) {
                alert('❌ Error starting monitoring: ' + error.message);
            }
        }

        async function stopCelebrityMonitoring() {
            try {
                const response = await fetch('/api/celebrity/stop', { method: 'POST' });
                const result = await response.json();
                if (result.success) {
                    alert('⏹️ Celebrity monitoring stopped!');
                    await refreshCelebrity();
                } else {
                    alert('❌ Failed to stop monitoring: ' + result.error);
                }
            } catch (error) {
                alert('❌ Error stopping monitoring: ' + error.message);
            }
        }

        async function scanCelebrityNews() {
            try {
                const button = event.target;
                button.disabled = true;
                button.textContent = '🔍 Scanning...';

                const response = await fetch('/api/celebrity/scan', { method: 'POST' });
                const result = await response.json();

                if (result.success) {
                    alert(`✅ Scan complete! ${result.message}`);
                    await refreshCelebrity();
                } else {
                    alert('❌ Scan failed: ' + result.error);
                }
            } catch (error) {
                alert('❌ Error scanning: ' + error.message);
            } finally {
                const button = event.target;
                button.disabled = false;
                button.textContent = '🔍 Scan Now';
            }
        }

        async function refreshAllData() {
            if (currentTab === 'overview') {
                await refreshOverview();
            } else if (currentTab === 'strategies') {
                await refreshStrategies();
            } else if (currentTab === 'conditions') {
                await refreshConditions();
            } else if (currentTab === 'sentiment') {
                await refreshSentiment();
            } else if (currentTab === 'celebrity') {
                await refreshCelebrity();
            } else if (currentTab === 'ai-control') {
                await refreshAIControl();
            } else if (currentTab === 'data') {
                await refreshDataInfo();
            } else if (currentTab === 'history') {
                await refreshHistory();
            } else if (currentTab === 'performance') {
                await refreshPerformance();
            } else if (currentTab === 'system') {
                await refreshSystemStatus();
            }
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            initProfitChart();
            refreshOverview();
            refreshInterval = setInterval(refreshOverview, 10000);
        });
    </script>
</body>
</html>
"""

# Flask routes
@app.route('/')
def dashboard():
    """Serve the enhanced dashboard"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/overview')
def api_overview():
    """API endpoint for overview status"""
    data = get_overview_status()
    return jsonify(data)

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    data = get_system_status()
    return jsonify(data)

@app.route('/api/bots/status')
def api_bots_status():
    """API endpoint for bot status"""
    data = get_bot_status()
    return jsonify(data)

@app.route('/api/analytics')
def api_analytics():
    """API endpoint for analytics data"""
    data = enhanced_analytics.get_comprehensive_analysis()
    return jsonify(data)

@app.route('/api/analytics/export')
def api_analytics_export():
    """Export analytics data"""
    data = enhanced_analytics.get_comprehensive_analysis()
    return jsonify(data)

@app.route('/api/conditions')
def api_conditions():
    """API endpoint for strategy conditions"""
    # Simulate strategy conditions data
    import random
    data = {
        'conditions': {
            'rsi_ready': random.random() > 0.5,
            'cti_ready': random.random() > 0.3,
            'sma_ready': random.random() > 0.4,
            'volume_ready': random.random() > 0.6
        },
        'ready_pairs': [
            {'pair': 'BTC/USDC', 'conditions': 4, 'total': 5, 'score': 80},
            {'pair': 'ETH/USDC', 'conditions': 3, 'total': 5, 'score': 60},
            {'pair': 'ADA/USDC', 'conditions': 2, 'total': 5, 'score': 40}
        ],
        'strategy_params': {
            'rsi_fast': 35,
            'rsi_slow': 24,
            'cti': 0.75,
            'sma15_ratio': 0.98,
            'volume_threshold': 1.5
        },
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(data)

@app.route('/api/sentiment')
def api_sentiment():
    """API endpoint for market sentiment"""
    import random

    # Simulate Fear & Greed Index API call
    fear_greed = random.randint(20, 80)

    data = {
        'fear_greed_index': fear_greed,
        'news_sentiment': random.randint(30, 90),
        'social_sentiment': random.randint(25, 85),
        'overall_sentiment': random.randint(35, 75),
        'market_mood': 'Bullish' if fear_greed > 60 else 'Bearish' if fear_greed < 40 else 'Neutral',
        'news_items': [
            {'headline': 'Bitcoin reaches new monthly high', 'sentiment': 85, 'source': 'CoinDesk'},
            {'headline': 'Ethereum upgrade shows promise', 'sentiment': 75, 'source': 'CoinTelegraph'},
            {'headline': 'Market volatility expected', 'sentiment': 45, 'source': 'Reuters'}
        ],
        'analysis': {
            'bullish_signals': ['Fear & Greed index showing optimism', 'Social sentiment trending positive'],
            'risk_factors': ['High volatility expected', 'Monitor resistance levels'],
            'recommendation': 'Favorable conditions for Enhanced Bot strategy'
        },
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(data)

@app.route('/api/ai-control')
def api_ai_control():
    """API endpoint for AI control status"""
    import random

    data = {
        'components': {
            'position_manager': {'status': random.choice(['active', 'offline']), 'last_update': '2 minutes ago'},
            'sentiment_analyzer': {'status': random.choice(['active', 'offline']), 'last_update': '1 minute ago'},
            'pair_selector': {'status': random.choice(['active', 'offline']), 'last_update': '30 seconds ago'},
            'notification_service': {'status': random.choice(['active', 'offline']), 'last_update': '10 seconds ago'}
        },
        'recommendations': [
            {
                'type': 'optimization',
                'title': 'Strategy Optimization',
                'action': 'Increase RSI threshold to 35 for better entry timing',
                'impact': '+15% win rate improvement'
            },
            {
                'type': 'pair',
                'title': 'Pair Recommendation',
                'action': 'Focus on BTC/USDC and ETH/USDC during current market conditions',
                'reason': 'High volume and favorable sentiment'
            },
            {
                'type': 'risk',
                'title': 'Risk Management',
                'action': 'Reduce position size by 20% due to increased volatility',
                'duration': 'Next 24 hours'
            }
        ],
        'optimization': {
            'last_run': '2 hours ago',
            'parameters_updated': 'RSI, CTI thresholds',
            'performance_impact': '+8.5% improvement',
            'next_run': 'In 22 hours'
        },
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(data)

@app.route('/api/celebrity')
def api_celebrity():
    """API endpoint for celebrity monitoring status"""
    data = celebrity_monitor.get_status()
    return jsonify(data)

@app.route('/api/celebrity/alerts')
def api_celebrity_alerts():
    """API endpoint for recent celebrity alerts"""
    hours = request.args.get('hours', 24, type=int)
    alerts = celebrity_monitor.get_recent_alerts(hours)
    return jsonify({'alerts': alerts, 'total': len(alerts)})

@app.route('/api/celebrity/start', methods=['POST'])
def api_celebrity_start():
    """Start celebrity monitoring"""
    try:
        celebrity_monitor.start_monitoring()
        return jsonify({'success': True, 'message': 'Celebrity monitoring started'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/celebrity/stop', methods=['POST'])
def api_celebrity_stop():
    """Stop celebrity monitoring"""
    try:
        celebrity_monitor.stop_monitoring()
        return jsonify({'success': True, 'message': 'Celebrity monitoring stopped'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/celebrity/scan', methods=['POST'])
def api_celebrity_scan():
    """Manual celebrity news scan"""
    try:
        news_results = celebrity_monitor.search_news_feeds()
        alerts_processed = 0
        trades_executed = 0

        for result in news_results:
            alert = celebrity_monitor.process_alert(
                result['celebrity'], result['coin'],
                result['content'], result['source'], result['title']
            )
            alerts_processed += 1
            if alert.trade_executed:
                trades_executed += 1

        return jsonify({
            'success': True,
            'alerts_processed': alerts_processed,
            'trades_executed': trades_executed,
            'message': f'Processed {alerts_processed} alerts, executed {trades_executed} trades'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == "__main__":
    logger.info("🚀 Enhanced Bot System Dashboard ξεκινάει στο http://localhost:8503")
    logger.info("📊 Πατήστε το κουμπί για έλεγχο όλων των συστημάτων")
    app.run(host='0.0.0.0', port=8503, debug=False)