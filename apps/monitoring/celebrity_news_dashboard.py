#!/usr/bin/env python3
"""
Celebrity News Trading Dashboard
Real-time monitoring and automatic trading based on celebrity crypto endorsements
Port: 8503
"""

import streamlit as st
import pandas as pd
import requests
import json
import time
from datetime import datetime, timedelta
import sqlite3
import threading
import logging
from typing import Dict, List, Optional
import re
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass
import asyncio
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NewsAlert:
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

class CelebrityNewsTrader:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "databases", "celebrity_news.db")
        self.freqtrade_api = "http://localhost:8082/api/v1"
        self.freqtrade_auth = ("freqtrade", "ruriu7AY")

        # Celebrity configurations with impact weights
        self.celebrities = {
            'Trump': {
                'keywords': ['trump', 'donald trump', 'president trump', '@realdonaldtrump'],
                'crypto_keywords': ['bitcoin', 'btc', 'crypto', 'cryptocurrency', 'coin', 'token', 'blockchain'],
                'impact_weight': 0.9,  # Very high impact
                'priority': 'CRITICAL'
            },
            'Elon Musk': {
                'keywords': ['elon musk', 'musk', '@elonmusk', 'tesla', 'spacex'],
                'crypto_keywords': ['dogecoin', 'doge', 'bitcoin', 'btc', 'crypto', 'cryptocurrency'],
                'impact_weight': 0.95,  # Highest impact
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
            },
            'Jack Dorsey': {
                'keywords': ['jack dorsey', 'dorsey', '@jack'],
                'crypto_keywords': ['bitcoin', 'btc', 'cryptocurrency'],
                'impact_weight': 0.65,
                'priority': 'MEDIUM'
            }
        }

        # Coin mappings for trading
        self.coin_mappings = {
            'bitcoin': 'BTC/USDC',
            'btc': 'BTC/USDC',
            'ethereum': 'ETH/USDC',
            'eth': 'ETH/USDC',
            'dogecoin': 'DOGE/USDC',
            'doge': 'DOGE/USDC',
            'shiba': 'SHIB/USDC',
            'shib': 'SHIB/USDC',
            'pepe': 'PEPE/USDC',
            'bonk': 'BONK/USDC',
            'solana': 'SOL/USDC',
            'sol': 'SOL/USDC',
            'cardano': 'ADA/USDC',
            'ada': 'ADA/USDC',
            'polkadot': 'DOT/USDC',
            'dot': 'DOT/USDC',
            'chainlink': 'LINK/USDC',
            'link': 'LINK/USDC',
            'avalanche': 'AVAX/USDC',
            'avax': 'AVAX/USDC'
        }

        self.init_database()

    def init_database(self):
        """Initialize SQLite database for storing news and trades"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS celebrity_news (
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
                trade_amount REAL,
                trade_price REAL,
                profit_loss REAL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                total_alerts INTEGER,
                trades_executed INTEGER,
                total_profit REAL,
                active_monitoring BOOLEAN
            )
        ''')

        conn.commit()
        conn.close()

    def calculate_impact_score(self, celebrity: str, content: str, sentiment: str) -> float:
        """Calculate impact score based on celebrity, content, and sentiment"""
        base_score = self.celebrities.get(celebrity, {}).get('impact_weight', 0.5)

        # Sentiment multiplier
        sentiment_multiplier = {
            'POSITIVE': 1.0,
            'NEGATIVE': 0.3,
            'NEUTRAL': 0.6
        }.get(sentiment, 0.5)

        # Content analysis for power words
        power_words = ['buy', 'invest', 'hodl', 'moon', 'pump', 'bullish', 'support', 'backing', 'endorsing']
        negative_words = ['sell', 'dump', 'crash', 'bearish', 'avoid', 'warning']

        content_lower = content.lower()
        power_count = sum(1 for word in power_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)

        content_multiplier = 1.0 + (power_count * 0.1) - (negative_count * 0.15)
        content_multiplier = max(0.1, min(2.0, content_multiplier))

        final_score = base_score * sentiment_multiplier * content_multiplier
        return min(1.0, max(0.0, final_score))

    def analyze_sentiment(self, text: str) -> str:
        """Enhanced sentiment analysis"""
        positive_words = ['buy', 'bullish', 'moon', 'pump', 'invest', 'hodl', 'support', 'backing', 'endorsing', 'love', 'great', 'amazing', 'revolutionary']
        negative_words = ['sell', 'bearish', 'dump', 'crash', 'avoid', 'warning', 'scam', 'dangerous', 'risky', 'bubble']

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count and positive_count > 0:
            return "POSITIVE"
        elif negative_count > positive_count and negative_count > 0:
            return "NEGATIVE"
        else:
            return "NEUTRAL"

    def search_crypto_news(self, query: str) -> List[Dict]:
        """Search crypto news from multiple sources"""
        results = []

        # RSS feeds to monitor
        feeds = [
            "https://cointelegraph.com/rss",
            "https://coindesk.com/arc/outboundfeeds/rss/",
            "https://decrypt.co/feed",
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "https://cryptonews.com/news/feed/",
        ]

        for feed_url in feeds:
            try:
                response = requests.get(feed_url, timeout=10)
                if response.status_code == 200:
                    content = response.text.lower()
                    query_lower = query.lower()

                    if query_lower in content:
                        # Extract more detailed information
                        results.append({
                            'source': feed_url.split('/')[2],
                            'url': feed_url,
                            'query': query,
                            'timestamp': datetime.now(),
                            'content': self.extract_relevant_content(content, query_lower),
                            'raw_content': content[:1000]  # First 1000 chars for analysis
                        })
            except Exception as e:
                logger.debug(f"Error fetching {feed_url}: {e}")

        return results

    def extract_relevant_content(self, content: str, query: str, context_length: int = 300) -> str:
        """Extract relevant content around the query"""
        try:
            index = content.lower().find(query.lower())
            if index != -1:
                start = max(0, index - context_length // 2)
                end = min(len(content), index + len(query) + context_length // 2)
                return content[start:end].strip()
            return content[:context_length]
        except:
            return content[:context_length]

    def should_execute_trade(self, impact_score: float, sentiment: str, celebrity: str) -> bool:
        """Determine if a trade should be executed based on impact score and other factors"""
        # Minimum impact score threshold
        min_threshold = 0.7

        # Celebrity-specific thresholds
        celebrity_thresholds = {
            'Elon Musk': 0.6,
            'Trump': 0.65,
            'Michael Saylor': 0.75,
            'Cathie Wood': 0.8
        }

        threshold = celebrity_thresholds.get(celebrity, min_threshold)

        # Only trade on positive sentiment with high impact
        return sentiment == "POSITIVE" and impact_score >= threshold

    def execute_freqtrade_order(self, pair: str, action: str = "buy", amount: float = 25.0) -> Dict:
        """Execute trade through FreqTrade API"""
        try:
            if action == "buy":
                url = f"{self.freqtrade_api}/forceentry"
                data = {
                    "pair": pair,
                    "side": "long",
                    "ordertype": "market",
                    "stakeamount": amount
                }
            else:
                url = f"{self.freqtrade_api}/forceexit"
                data = {"tradeid": "all", "pair": pair}

            response = requests.post(url, json=data, auth=self.freqtrade_auth, timeout=10)

            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def process_news_alert(self, celebrity: str, coin: str, content: str, source: str) -> NewsAlert:
        """Process a news alert and potentially execute trade"""
        sentiment = self.analyze_sentiment(content)
        impact_score = self.calculate_impact_score(celebrity, content, sentiment)

        # Determine trading pair
        trading_pair = self.coin_mappings.get(coin.lower(), None)
        trade_executed = False
        action_taken = "MONITORED"

        # Check if we should execute a trade
        if trading_pair and self.should_execute_trade(impact_score, sentiment, celebrity):
            trade_result = self.execute_freqtrade_order(trading_pair, "buy")
            if trade_result["success"]:
                trade_executed = True
                action_taken = f"BUY_EXECUTED_{trading_pair}"
                logger.info(f"🚀 TRADE EXECUTED: {trading_pair} due to {celebrity} {sentiment} news")
            else:
                action_taken = f"BUY_FAILED_{trade_result.get('error', 'Unknown')}"

        # Create news alert object
        alert = NewsAlert(
            timestamp=datetime.now(),
            celebrity=celebrity,
            coin=coin,
            sentiment=sentiment,
            impact_score=impact_score,
            source=source,
            headline=f"{celebrity} mentions {coin}",
            content=content[:500],
            action_taken=action_taken,
            trade_executed=trade_executed
        )

        # Store in database
        self.store_news_alert(alert, trading_pair if trade_executed else None)

        return alert

    def store_news_alert(self, alert: NewsAlert, trading_pair: str = None):
        """Store news alert in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO celebrity_news
            (timestamp, celebrity, coin, sentiment, impact_score, source, headline, content, action_taken, trade_executed, trade_pair)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert.timestamp, alert.celebrity, alert.coin, alert.sentiment,
            alert.impact_score, alert.source, alert.headline, alert.content,
            alert.action_taken, alert.trade_executed, trading_pair
        ))

        conn.commit()
        conn.close()

    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Get recent alerts from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since = datetime.now() - timedelta(hours=hours)
        cursor.execute('''
            SELECT * FROM celebrity_news
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        ''', (since,))

        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return results

    def monitor_celebrities(self) -> List[NewsAlert]:
        """Main monitoring function - returns new alerts"""
        alerts = []

        for celebrity, config in self.celebrities.items():
            for celeb_keyword in config['keywords']:
                for crypto_keyword in config['crypto_keywords']:
                    query = f"{celeb_keyword} {crypto_keyword}"

                    # Search for news
                    news_results = self.search_crypto_news(query)

                    for result in news_results:
                        # Process each news item
                        alert = self.process_news_alert(
                            celebrity=celebrity,
                            coin=crypto_keyword,
                            content=result['content'],
                            source=result['source']
                        )
                        alerts.append(alert)

                    # Rate limiting
                    time.sleep(1)

        return alerts

# Streamlit Dashboard
def main():
    st.set_page_config(
        page_title="Celebrity Crypto News Trader",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🎬 Celebrity Crypto News Trading Dashboard")
    st.markdown("**Real-time monitoring and automatic trading based on celebrity endorsements**")

    # Initialize trader
    if 'trader' not in st.session_state:
        st.session_state.trader = CelebrityNewsTrader()

    trader = st.session_state.trader

    # Sidebar controls
    st.sidebar.header("🎯 Monitoring Controls")

    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh (10 min)", value=True)

    # Manual scan button
    if st.sidebar.button("🔍 Scan Now", type="primary"):
        with st.spinner("Scanning for celebrity crypto news..."):
            new_alerts = trader.monitor_celebrities()
            if new_alerts:
                st.sidebar.success(f"Found {len(new_alerts)} new alerts!")
            else:
                st.sidebar.info("No new alerts found")

    # Trading settings
    st.sidebar.header("⚙️ Trading Settings")
    min_impact_score = st.sidebar.slider("Min Impact Score for Trading", 0.0, 1.0, 0.7, 0.05)
    max_trades_per_hour = st.sidebar.number_input("Max Trades per Hour", 1, 10, 3)

    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)

    # Get recent data
    recent_alerts = trader.get_recent_alerts(24)

    with col1:
        st.metric("📊 Total Alerts (24h)", len(recent_alerts))

    with col2:
        trades_executed = len([a for a in recent_alerts if a['trade_executed']])
        st.metric("🚀 Trades Executed", trades_executed)

    with col3:
        high_impact = len([a for a in recent_alerts if a['impact_score'] > 0.7])
        st.metric("🔥 High Impact Alerts", high_impact)

    with col4:
        avg_impact = sum(a['impact_score'] for a in recent_alerts) / len(recent_alerts) if recent_alerts else 0
        st.metric("📈 Avg Impact Score", f"{avg_impact:.2f}")

    # Recent alerts table
    st.header("📰 Recent Celebrity News Alerts")

    if recent_alerts:
        df = pd.DataFrame(recent_alerts)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=False)

        # Color code by impact score
        def color_impact(val):
            if val >= 0.8:
                return 'background-color: #ff4444; color: white'
            elif val >= 0.6:
                return 'background-color: #ffaa44; color: white'
            else:
                return 'background-color: #44ff44; color: black'

        # Display styled dataframe
        styled_df = df[['timestamp', 'celebrity', 'coin', 'sentiment', 'impact_score', 'action_taken', 'trade_executed']].style.applymap(color_impact, subset=['impact_score'])

        st.dataframe(styled_df, use_container_width=True)

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Alerts by Celebrity")
            celebrity_counts = df['celebrity'].value_counts()
            fig = px.bar(x=celebrity_counts.index, y=celebrity_counts.values)
            fig.update_layout(xaxis_title="Celebrity", yaxis_title="Alert Count")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("💰 Impact Score Distribution")
            fig = px.histogram(df, x='impact_score', bins=20)
            fig.update_layout(xaxis_title="Impact Score", yaxis_title="Frequency")
            st.plotly_chart(fig, use_container_width=True)

        # Timeline chart
        st.subheader("⏰ Alert Timeline")
        df_timeline = df.groupby([df['timestamp'].dt.floor('H'), 'celebrity']).size().reset_index(name='count')
        fig = px.line(df_timeline, x='timestamp', y='count', color='celebrity')
        fig.update_layout(xaxis_title="Time", yaxis_title="Alert Count")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No recent alerts found. The system is monitoring...")

    # Live monitoring status
    st.header("🔴 Live Monitoring Status")

    status_col1, status_col2, status_col3 = st.columns(3)

    with status_col1:
        st.success("✅ Celebrity Monitor: ACTIVE")
        st.info(f"👥 Monitoring: {len(trader.celebrities)} celebrities")

    with status_col2:
        st.success("✅ Auto Trading: ENABLED")
        st.info(f"💰 Pairs: {len(trader.coin_mappings)} supported")

    with status_col3:
        st.success("✅ Database: CONNECTED")
        st.info(f"📊 Records: {len(recent_alerts)} (24h)")

    # Auto-refresh mechanism
    if auto_refresh:
        time.sleep(600)  # 10 minutes
        st.rerun()

if __name__ == "__main__":
    main()