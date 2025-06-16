#!/usr/bin/env python3
"""
Market Sentiment Analyzer
Analyzes market sentiment from multiple sources:
- News sentiment (NewsAPI, CoinDesk, etc.)
- Social media sentiment (Twitter, Reddit)
- Fear & Greed Index
- Technical sentiment (price action, volume)
- On-chain metrics (when available)
"""

import asyncio
import aiohttp
import json
import logging
import requests
import sqlite3
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import re
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/market_sentiment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MarketSentimentAnalyzer:
    """Comprehensive market sentiment analysis"""

    def __init__(self, config_path: str = "user_data/config_enhanced.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.api_url = f"http://localhost:{self.config['api_server']['listen_port']}/api/v1"
        self.auth = (self.config['api_server']['username'], self.config['api_server']['password'])

        # API Keys (configure these for full functionality)
        self.news_api_key = None  # Get from newsapi.org
        self.twitter_bearer_token = None  # Twitter API v2
        self.reddit_client_id = None  # Reddit API
        self.reddit_client_secret = None

        # Sentiment weights
        self.sentiment_weights = {
            'fear_greed': 0.25,      # Fear & Greed Index
            'news': 0.25,            # News sentiment
            'social': 0.20,          # Social media sentiment
            'technical': 0.20,       # Technical sentiment
            'volume': 0.10           # Volume sentiment
        }

        # Initialize database
        self.db_path = "data/databases/market_sentiment.db"
        self._init_database()

        # Cache for sentiment data
        self.sentiment_cache = {}
        self.cache_duration = 300  # 5 minutes

        logger.info("Market Sentiment Analyzer initialized")

    def _load_config(self) -> dict:
        """Load freqtrade configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def _init_database(self):
        """Initialize database for sentiment data"""
        Path("data/databases").mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pair TEXT NOT NULL,
                fear_greed_score REAL DEFAULT 50,
                news_score REAL DEFAULT 50,
                social_score REAL DEFAULT 50,
                technical_score REAL DEFAULT 50,
                volume_score REAL DEFAULT 50,
                overall_score REAL NOT NULL,
                confidence REAL NOT NULL,
                data_sources TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_sentiment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                currency TEXT NOT NULL,
                headline TEXT NOT NULL,
                source TEXT NOT NULL,
                sentiment_score REAL NOT NULL,
                url TEXT,
                published_at DATETIME,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_sentiment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                currency TEXT NOT NULL,
                platform TEXT NOT NULL,
                content TEXT NOT NULL,
                sentiment_score REAL NOT NULL,
                engagement_score REAL DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    async def get_freqtrade_data(self, endpoint: str) -> Optional[dict]:
        """Get data from Freqtrade API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/{endpoint}",
                    auth=aiohttp.BasicAuth(self.auth[0], self.auth[1]),
                    timeout=10
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"API request failed: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching {endpoint}: {e}")
            return None

    async def get_fear_greed_index(self) -> float:
        """Get Fear & Greed Index from API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.alternative.me/fng/",
                    timeout=10
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        value = float(data['data'][0]['value'])
                        logger.info(f"Fear & Greed Index: {value}")
                        return value
        except Exception as e:
            logger.error(f"Error fetching Fear & Greed Index: {e}")

        return 50.0  # Neutral default

    async def analyze_news_sentiment(self, currency: str) -> float:
        """Analyze news sentiment for a currency"""
        if not self.news_api_key:
            logger.warning("NewsAPI key not configured, using neutral sentiment")
            return 50.0

        try:
            # Search for recent news about the currency
            query = f"{currency} cryptocurrency OR {currency} crypto"
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'language': 'en',
                'sortBy': 'publishedAt',
                'from': (datetime.now() - timedelta(days=1)).isoformat(),
                'apiKey': self.news_api_key,
                'pageSize': 20
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get('articles', [])

                        if not articles:
                            return 50.0  # Neutral if no news

                        sentiment_scores = []
                        for article in articles:
                            title = article.get('title', '')
                            description = article.get('description', '')
                            content = f"{title} {description}"

                            # Simple sentiment analysis
                            sentiment = self._analyze_text_sentiment(content)
                            sentiment_scores.append(sentiment)

                            # Store in database
                            self._store_news_sentiment(
                                currency, title, article.get('source', {}).get('name', 'Unknown'),
                                sentiment, article.get('url'), article.get('publishedAt')
                            )

                        # Calculate average sentiment
                        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                        logger.info(f"News sentiment for {currency}: {avg_sentiment:.1f}")
                        return avg_sentiment

        except Exception as e:
            logger.error(f"Error analyzing news sentiment for {currency}: {e}")

        return 50.0  # Neutral default

    def _analyze_text_sentiment(self, text: str) -> float:
        """Simple text sentiment analysis using keyword matching"""
        # Positive keywords
        positive_words = [
            'bullish', 'bull', 'rise', 'rising', 'up', 'gain', 'gains', 'profit',
            'profits', 'surge', 'surging', 'rally', 'rallying', 'boom', 'booming',
            'positive', 'optimistic', 'strong', 'strength', 'breakthrough',
            'adoption', 'partnership', 'upgrade', 'improvement', 'success',
            'milestone', 'achievement', 'growth', 'growing', 'increase', 'increasing'
        ]

        # Negative keywords
        negative_words = [
            'bearish', 'bear', 'fall', 'falling', 'down', 'loss', 'losses',
            'crash', 'crashing', 'dump', 'dumping', 'decline', 'declining',
            'negative', 'pessimistic', 'weak', 'weakness', 'concern', 'concerns',
            'risk', 'risks', 'problem', 'problems', 'issue', 'issues',
            'regulation', 'ban', 'banned', 'hack', 'hacked', 'scam', 'fraud'
        ]

        text_lower = text.lower()

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        total_words = len(text.split())
        if total_words == 0:
            return 50.0

        # Calculate sentiment score (0-100)
        sentiment_score = 50 + ((positive_count - negative_count) / max(1, total_words * 0.1)) * 25
        return max(0, min(100, sentiment_score))

    def _store_news_sentiment(self, currency: str, headline: str, source: str,
                             sentiment: float, url: str, published_at: str):
        """Store news sentiment in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO news_sentiment
            (currency, headline, source, sentiment_score, url, published_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (currency, headline, source, sentiment, url, published_at))

        conn.commit()
        conn.close()

    async def analyze_social_sentiment(self, currency: str) -> float:
        """Analyze social media sentiment (placeholder implementation)"""
        # This would integrate with Twitter API, Reddit API, etc.
        # For now, return a simulated sentiment based on recent price action

        try:
            # Get recent price data as a proxy for social sentiment
            pair = f"{currency}/USDC"
            candles_data = await self.get_freqtrade_data(f"pair_candles?pair={pair}&timeframe=1h&limit=24")

            if candles_data and 'data' in candles_data:
                candles = candles_data['data']
                if len(candles) >= 12:
                    prices = [float(c[4]) for c in candles]

                    # Calculate price momentum as social sentiment proxy
                    recent_change = (prices[-1] - prices[-6]) / prices[-6]  # 6h change
                    daily_change = (prices[-1] - prices[-24]) / prices[-24]  # 24h change

                    # Convert to sentiment score (0-100)
                    momentum_sentiment = 50 + (recent_change * 0.3 + daily_change * 0.7) * 100
                    sentiment = max(0, min(100, momentum_sentiment))

                    logger.info(f"Social sentiment (proxy) for {currency}: {sentiment:.1f}")
                    return sentiment

        except Exception as e:
            logger.error(f"Error analyzing social sentiment for {currency}: {e}")

        return 50.0  # Neutral default

    async def analyze_technical_sentiment(self, pair: str) -> float:
        """Analyze technical sentiment based on price action and indicators"""
        try:
            # Get strategy conditions
            response = requests.get("http://localhost:8503/api/conditions", timeout=5)
            if response.status_code == 200:
                conditions = response.json()
                if pair in conditions:
                    met_count = conditions[pair]['conditions']['met_count']
                    total_count = conditions[pair]['conditions']['total_count']

                    # Base technical score
                    base_score = (met_count / total_count) * 100

                    # Get additional technical data
                    candles_data = await self.get_freqtrade_data(f"pair_candles?pair={pair}&timeframe=1h&limit=50")
                    if candles_data and 'data' in candles_data:
                        candles = candles_data['data']
                        if len(candles) >= 20:
                            prices = [float(c[4]) for c in candles]
                            volumes = [float(c[5]) for c in candles]

                            # Price momentum
                            short_momentum = (prices[-1] - prices[-6]) / prices[-6]
                            medium_momentum = (prices[-1] - prices[-12]) / prices[-12]
                            long_momentum = (prices[-1] - prices[-24]) / prices[-24]

                            # Volume trend
                            recent_volume = sum(volumes[-6:]) / 6
                            historical_volume = sum(volumes[-24:-6]) / 18
                            volume_trend = (recent_volume - historical_volume) / historical_volume if historical_volume > 0 else 0

                            # Combine factors
                            momentum_score = 50 + (short_momentum * 0.5 + medium_momentum * 0.3 + long_momentum * 0.2) * 100
                            volume_score = 50 + volume_trend * 50

                            # Weighted technical sentiment
                            technical_sentiment = (
                                base_score * 0.4 +
                                momentum_score * 0.4 +
                                volume_score * 0.2
                            )

                            technical_sentiment = max(0, min(100, technical_sentiment))
                            logger.info(f"Technical sentiment for {pair}: {technical_sentiment:.1f}")
                            return technical_sentiment

                    return base_score

        except Exception as e:
            logger.error(f"Error analyzing technical sentiment for {pair}: {e}")

        return 50.0  # Neutral default

    async def analyze_volume_sentiment(self, pair: str) -> float:
        """Analyze volume-based sentiment"""
        try:
            candles_data = await self.get_freqtrade_data(f"pair_candles?pair={pair}&timeframe=1h&limit=48")
            if candles_data and 'data' in candles_data:
                candles = candles_data['data']
                if len(candles) >= 24:
                    volumes = [float(c[5]) for c in candles]
                    prices = [float(c[4]) for c in candles]

                    # Volume trend analysis
                    recent_volume = sum(volumes[-12:]) / 12  # Last 12 hours
                    historical_volume = sum(volumes[-24:-12]) / 12  # Previous 12 hours

                    volume_change = (recent_volume - historical_volume) / historical_volume if historical_volume > 0 else 0

                    # Price-volume correlation
                    price_changes = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
                    volume_changes = [(volumes[i] - volumes[i-1]) / volumes[i-1] for i in range(1, len(volumes)) if volumes[i-1] > 0]

                    if len(price_changes) == len(volume_changes) and len(price_changes) > 0:
                        correlation = np.corrcoef(price_changes, volume_changes)[0, 1]
                        if np.isnan(correlation):
                            correlation = 0
                    else:
                        correlation = 0

                    # Volume sentiment score
                    volume_sentiment = 50 + (volume_change * 25) + (correlation * 25)
                    volume_sentiment = max(0, min(100, volume_sentiment))

                    logger.info(f"Volume sentiment for {pair}: {volume_sentiment:.1f}")
                    return volume_sentiment

        except Exception as e:
            logger.error(f"Error analyzing volume sentiment for {pair}: {e}")

        return 50.0  # Neutral default

    async def get_comprehensive_sentiment(self, pair: str) -> Dict[str, float]:
        """Get comprehensive sentiment analysis for a trading pair"""
        currency = pair.split('/')[0]

        # Check cache first
        cache_key = f"{pair}_{int(time.time() // self.cache_duration)}"
        if cache_key in self.sentiment_cache:
            return self.sentiment_cache[cache_key]

        try:
            # Gather sentiment from all sources
            fear_greed_score = await self.get_fear_greed_index()
            news_score = await self.analyze_news_sentiment(currency)
            social_score = await self.analyze_social_sentiment(currency)
            technical_score = await self.analyze_technical_sentiment(pair)
            volume_score = await self.analyze_volume_sentiment(pair)

            # Calculate weighted overall sentiment
            overall_sentiment = (
                fear_greed_score * self.sentiment_weights['fear_greed'] +
                news_score * self.sentiment_weights['news'] +
                social_score * self.sentiment_weights['social'] +
                technical_score * self.sentiment_weights['technical'] +
                volume_score * self.sentiment_weights['volume']
            )

            # Calculate confidence based on data availability
            data_sources = []
            if fear_greed_score != 50.0:
                data_sources.append('fear_greed')
            if news_score != 50.0:
                data_sources.append('news')
            if social_score != 50.0:
                data_sources.append('social')
            if technical_score != 50.0:
                data_sources.append('technical')
            if volume_score != 50.0:
                data_sources.append('volume')

            confidence = len(data_sources) / len(self.sentiment_weights)

            sentiment_data = {
                'pair': pair,
                'fear_greed_score': fear_greed_score,
                'news_score': news_score,
                'social_score': social_score,
                'technical_score': technical_score,
                'volume_score': volume_score,
                'overall_score': overall_sentiment,
                'confidence': confidence,
                'data_sources': ','.join(data_sources),
                'timestamp': datetime.now().isoformat()
            }

            # Store in database
            self._store_sentiment_analysis(sentiment_data)

            # Cache the result
            self.sentiment_cache[cache_key] = sentiment_data

            logger.info(f"Comprehensive sentiment for {pair}: {overall_sentiment:.1f} (confidence: {confidence:.2f})")

            return sentiment_data

        except Exception as e:
            logger.error(f"Error getting comprehensive sentiment for {pair}: {e}")
            return {
                'pair': pair,
                'overall_score': 50.0,
                'confidence': 0.0,
                'error': str(e)
            }

    def _store_sentiment_analysis(self, data: Dict[str, float]):
        """Store sentiment analysis in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO sentiment_analysis
            (pair, fear_greed_score, news_score, social_score, technical_score,
             volume_score, overall_score, confidence, data_sources)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['pair'], data['fear_greed_score'], data['news_score'],
            data['social_score'], data['technical_score'], data['volume_score'],
            data['overall_score'], data['confidence'], data['data_sources']
        ))

        conn.commit()
        conn.close()

    async def get_market_overview(self) -> Dict[str, any]:
        """Get overall market sentiment overview"""
        try:
            # Get whitelist
            whitelist_data = await self.get_freqtrade_data("whitelist")
            if not whitelist_data:
                return {}

            pairs = whitelist_data.get('whitelist', [])

            # Analyze sentiment for all pairs
            sentiment_scores = []
            pair_sentiments = {}

            for pair in pairs[:10]:  # Limit to first 10 pairs to avoid rate limits
                sentiment = await self.get_comprehensive_sentiment(pair)
                sentiment_scores.append(sentiment['overall_score'])
                pair_sentiments[pair] = sentiment

            # Calculate market overview
            if sentiment_scores:
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                bullish_pairs = len([s for s in sentiment_scores if s > 60])
                bearish_pairs = len([s for s in sentiment_scores if s < 40])
                neutral_pairs = len(sentiment_scores) - bullish_pairs - bearish_pairs

                market_overview = {
                    'average_sentiment': avg_sentiment,
                    'total_pairs': len(sentiment_scores),
                    'bullish_pairs': bullish_pairs,
                    'bearish_pairs': bearish_pairs,
                    'neutral_pairs': neutral_pairs,
                    'market_mood': 'Bullish' if avg_sentiment > 60 else 'Bearish' if avg_sentiment < 40 else 'Neutral',
                    'pair_sentiments': pair_sentiments,
                    'timestamp': datetime.now().isoformat()
                }

                logger.info(f"Market Overview: {market_overview['market_mood']} ({avg_sentiment:.1f})")
                return market_overview

        except Exception as e:
            logger.error(f"Error getting market overview: {e}")

        return {}

async def main():
    """Main function for testing"""
    analyzer = MarketSentimentAnalyzer()

    # Test sentiment analysis
    test_pairs = ["BTC/USDC", "ETH/USDC", "XRP/USDC"]

    for pair in test_pairs:
        sentiment = await analyzer.get_comprehensive_sentiment(pair)
        print(f"\n{pair} Sentiment Analysis:")
        print(f"  Overall Score: {sentiment.get('overall_score', 0):.1f}/100")
        print(f"  Fear & Greed: {sentiment.get('fear_greed_score', 0):.1f}")
        print(f"  Technical: {sentiment.get('technical_score', 0):.1f}")
        print(f"  Volume: {sentiment.get('volume_score', 0):.1f}")
        print(f"  Confidence: {sentiment.get('confidence', 0):.2f}")

    # Test market overview
    overview = await analyzer.get_market_overview()
    if overview:
        print(f"\nMarket Overview:")
        print(f"  Market Mood: {overview.get('market_mood', 'Unknown')}")
        print(f"  Average Sentiment: {overview.get('average_sentiment', 0):.1f}")
        print(f"  Bullish Pairs: {overview.get('bullish_pairs', 0)}")
        print(f"  Bearish Pairs: {overview.get('bearish_pairs', 0)}")

if __name__ == "__main__":
    asyncio.run(main())