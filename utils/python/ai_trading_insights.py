"""
AI-Powered Trading Insights Module
Παρέχει προηγμένες αναλύσεις και προβλέψεις για το trading system
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import ta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketSentiment(Enum):
    EXTREMELY_BULLISH = "extremely_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    EXTREMELY_BEARISH = "extremely_bearish"

class TrendStrength(Enum):
    VERY_STRONG = "very_strong"
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    VERY_WEAK = "very_weak"

@dataclass
class AIInsight:
    """AI-generated trading insight"""
    symbol: str
    timestamp: datetime
    sentiment: MarketSentiment
    trend_strength: TrendStrength
    price_prediction_1h: float
    price_prediction_4h: float
    price_prediction_24h: float
    confidence_score: float
    key_factors: List[str]
    risk_assessment: str
    recommended_action: str
    support_levels: List[float]
    resistance_levels: List[float]
    volatility_forecast: float
    market_regime: str

@dataclass
class MarketRegimeAnalysis:
    """Market regime classification"""
    regime: str  # trending_up, trending_down, sideways, volatile
    confidence: float
    duration_estimate: str
    characteristics: List[str]
    trading_recommendations: List[str]

class AITradingInsights:
    """AI-powered trading insights generator"""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.market_data_cache = {}
        self.news_sentiment_cache = {}

    async def initialize_models(self):
        """Initialize ML models for predictions"""
        try:
            # Initialize models for each symbol
            symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'BNBUSDT', 'DOTUSDT']

            for symbol in symbols:
                # Random Forest for price prediction
                self.models[symbol] = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                self.scalers[symbol] = StandardScaler()

            logger.info("AI models initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing AI models: {e}")

    async def get_market_data(self, symbol: str, interval: str = '1h', limit: int = 200) -> pd.DataFrame:
        """Fetch market data for analysis"""
        try:
            # Simulate market data (in production, use real API)
            dates = pd.date_range(end=datetime.now(), periods=limit, freq='H')

            # Generate realistic OHLCV data
            np.random.seed(42)
            base_price = {'BTCUSDT': 45000, 'ETHUSDT': 2800, 'SOLUSDT': 120,
                         'ADAUSDT': 0.5, 'BNBUSDT': 350, 'DOTUSDT': 8}[symbol]

            prices = []
            current_price = base_price

            for i in range(limit):
                # Add trend and volatility
                trend = 0.001 * np.sin(i * 0.1)  # Long-term trend
                volatility = 0.02 * np.random.randn()  # Random volatility

                current_price *= (1 + trend + volatility)
                prices.append(current_price)

            # Create OHLCV data
            df = pd.DataFrame({
                'timestamp': dates,
                'open': prices,
                'high': [p * (1 + abs(np.random.randn() * 0.01)) for p in prices],
                'low': [p * (1 - abs(np.random.randn() * 0.01)) for p in prices],
                'close': prices,
                'volume': [1000 + np.random.randint(0, 5000) for _ in range(limit)]
            })

            return df

        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            return pd.DataFrame()

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive technical indicators"""
        try:
            # Trend indicators
            df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
            df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
            df['ema_12'] = ta.trend.ema_indicator(df['close'], window=12)
            df['ema_26'] = ta.trend.ema_indicator(df['close'], window=26)

            # MACD
            df['macd'] = ta.trend.macd_diff(df['close'])
            df['macd_signal'] = ta.trend.macd_signal(df['close'])

            # RSI
            df['rsi'] = ta.momentum.rsi(df['close'])

            # Bollinger Bands
            bb = ta.volatility.BollingerBands(df['close'])
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_lower'] = bb.bollinger_lband()

            # Stochastic
            df['stoch_k'] = ta.momentum.stoch(df['high'], df['low'], df['close'])
            df['stoch_d'] = ta.momentum.stoch_signal(df['high'], df['low'], df['close'])

            # Volume indicators
            df['volume_sma'] = ta.volume.volume_sma(df['close'], df['volume'])
            df['mfi'] = ta.volume.money_flow_index(df['high'], df['low'], df['close'], df['volume'])

            # Volatility indicators
            df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'])

            return df

        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return df

    def analyze_market_regime(self, df: pd.DataFrame) -> MarketRegimeAnalysis:
        """Analyze current market regime"""
        try:
            if len(df) < 50:
                return MarketRegimeAnalysis("unknown", 0.0, "insufficient_data", [], [])

            # Calculate regime indicators
            recent_data = df.tail(50)

            # Trend analysis
            price_change = (recent_data['close'].iloc[-1] - recent_data['close'].iloc[0]) / recent_data['close'].iloc[0]
            volatility = recent_data['close'].pct_change().std()

            # Volume analysis
            avg_volume = recent_data['volume'].mean()
            recent_volume = recent_data['volume'].tail(10).mean()
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1

            # Determine regime
            if abs(price_change) > 0.1 and volatility > 0.03:
                if price_change > 0:
                    regime = "strong_uptrend"
                    characteristics = ["High volatility", "Strong upward momentum", "Increased volume"]
                    recommendations = ["Trend following strategies", "Momentum trading", "Breakout strategies"]
                else:
                    regime = "strong_downtrend"
                    characteristics = ["High volatility", "Strong downward momentum", "Panic selling"]
                    recommendations = ["Short selling", "Defensive strategies", "Wait for reversal signals"]
            elif abs(price_change) > 0.05:
                if price_change > 0:
                    regime = "moderate_uptrend"
                    characteristics = ["Moderate upward movement", "Steady buying pressure"]
                    recommendations = ["Buy on dips", "Trend following", "Gradual position building"]
                else:
                    regime = "moderate_downtrend"
                    characteristics = ["Moderate downward movement", "Selling pressure"]
                    recommendations = ["Cautious selling", "Wait for support", "Defensive positioning"]
            elif volatility > 0.025:
                regime = "high_volatility_sideways"
                characteristics = ["High volatility", "No clear direction", "Range-bound trading"]
                recommendations = ["Range trading", "Volatility strategies", "Quick scalping"]
            else:
                regime = "low_volatility_sideways"
                characteristics = ["Low volatility", "Consolidation phase", "Tight range"]
                recommendations = ["Wait for breakout", "Accumulation strategies", "Patience required"]

            confidence = min(0.95, 0.5 + abs(price_change) * 2 + volatility * 10)

            return MarketRegimeAnalysis(
                regime=regime,
                confidence=confidence,
                duration_estimate="2-8 hours",
                characteristics=characteristics,
                trading_recommendations=recommendations
            )

        except Exception as e:
            logger.error(f"Error analyzing market regime: {e}")
            return MarketRegimeAnalysis("unknown", 0.0, "error", [], [])

    def calculate_support_resistance(self, df: pd.DataFrame) -> Tuple[List[float], List[float]]:
        """Calculate dynamic support and resistance levels"""
        try:
            if len(df) < 20:
                return [], []

            recent_data = df.tail(100)
            highs = recent_data['high'].values
            lows = recent_data['low'].values
            closes = recent_data['close'].values

            # Find local maxima and minima
            from scipy.signal import argrelextrema

            # Resistance levels (local maxima)
            max_indices = argrelextrema(highs, np.greater, order=5)[0]
            resistance_levels = [highs[i] for i in max_indices if i >= len(highs) - 50]

            # Support levels (local minima)
            min_indices = argrelextrema(lows, np.less, order=5)[0]
            support_levels = [lows[i] for i in min_indices if i >= len(lows) - 50]

            # Add psychological levels
            current_price = closes[-1]
            psychological_levels = []

            # Round numbers
            for multiplier in [0.9, 0.95, 1.05, 1.1]:
                level = round(current_price * multiplier, -2)  # Round to nearest 100
                psychological_levels.append(level)

            # Combine and sort
            all_resistance = sorted(set(resistance_levels + [l for l in psychological_levels if l > current_price]))
            all_support = sorted(set(support_levels + [l for l in psychological_levels if l < current_price]), reverse=True)

            return all_support[:3], all_resistance[:3]

        except Exception as e:
            logger.error(f"Error calculating support/resistance: {e}")
            return [], []

    def predict_price_movements(self, df: pd.DataFrame, symbol: str) -> Dict[str, float]:
        """Predict future price movements using ML"""
        try:
            if len(df) < 50:
                return {'1h': 0, '4h': 0, '24h': 0}

            # Prepare features
            features = []
            for i in range(10, len(df)):
                row_features = [
                    df['close'].iloc[i-1],
                    df['rsi'].iloc[i-1] if not pd.isna(df['rsi'].iloc[i-1]) else 50,
                    df['macd'].iloc[i-1] if not pd.isna(df['macd'].iloc[i-1]) else 0,
                    df['volume'].iloc[i-1],
                    df['atr'].iloc[i-1] if not pd.isna(df['atr'].iloc[i-1]) else 0,
                ]
                features.append(row_features)

            if len(features) < 20:
                return {'1h': 0, '4h': 0, '24h': 0}

            X = np.array(features[:-1])
            y = np.array([df['close'].iloc[i] for i in range(11, len(df))])

            # Train simple model
            if symbol not in self.models:
                self.models[symbol] = RandomForestRegressor(n_estimators=50, random_state=42)
                self.scalers[symbol] = StandardScaler()

            # Fit scaler and model
            X_scaled = self.scalers[symbol].fit_transform(X)
            self.models[symbol].fit(X_scaled, y)

            # Make predictions
            last_features = np.array([features[-1]])
            last_features_scaled = self.scalers[symbol].transform(last_features)

            current_price = df['close'].iloc[-1]
            predicted_price = self.models[symbol].predict(last_features_scaled)[0]

            # Calculate percentage changes
            change_1h = (predicted_price - current_price) / current_price
            change_4h = change_1h * 1.5  # Amplify for longer timeframes
            change_24h = change_1h * 2.0

            return {
                '1h': change_1h,
                '4h': change_4h,
                '24h': change_24h
            }

        except Exception as e:
            logger.error(f"Error predicting price movements: {e}")
            return {'1h': 0, '4h': 0, '24h': 0}

    def analyze_sentiment(self, symbol: str) -> MarketSentiment:
        """Analyze market sentiment (simulated)"""
        try:
            # Simulate sentiment analysis based on technical indicators
            # In production, this would use news API, social media, etc.

            sentiment_score = np.random.uniform(-1, 1)  # Simulate sentiment

            if sentiment_score > 0.6:
                return MarketSentiment.EXTREMELY_BULLISH
            elif sentiment_score > 0.2:
                return MarketSentiment.BULLISH
            elif sentiment_score > -0.2:
                return MarketSentiment.NEUTRAL
            elif sentiment_score > -0.6:
                return MarketSentiment.BEARISH
            else:
                return MarketSentiment.EXTREMELY_BEARISH

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return MarketSentiment.NEUTRAL

    async def generate_ai_insight(self, symbol: str) -> AIInsight:
        """Generate comprehensive AI insight for a symbol"""
        try:
            # Get market data
            df = await self.get_market_data(symbol)
            if df.empty:
                raise ValueError(f"No market data available for {symbol}")

            # Calculate technical indicators
            df = self.calculate_technical_indicators(df)

            # Analyze market regime
            regime_analysis = self.analyze_market_regime(df)

            # Calculate support/resistance
            support_levels, resistance_levels = self.calculate_support_resistance(df)

            # Predict price movements
            predictions = self.predict_price_movements(df, symbol)
            current_price = df['close'].iloc[-1]

            # Analyze sentiment
            sentiment = self.analyze_sentiment(symbol)

            # Determine trend strength
            price_change_20 = (df['close'].iloc[-1] - df['close'].iloc[-20]) / df['close'].iloc[-20]
            if abs(price_change_20) > 0.1:
                trend_strength = TrendStrength.VERY_STRONG
            elif abs(price_change_20) > 0.05:
                trend_strength = TrendStrength.STRONG
            elif abs(price_change_20) > 0.02:
                trend_strength = TrendStrength.MODERATE
            elif abs(price_change_20) > 0.01:
                trend_strength = TrendStrength.WEAK
            else:
                trend_strength = TrendStrength.VERY_WEAK

            # Generate key factors
            key_factors = []

            rsi = df['rsi'].iloc[-1] if not pd.isna(df['rsi'].iloc[-1]) else 50
            if rsi > 70:
                key_factors.append(f"RSI overbought ({rsi:.1f})")
            elif rsi < 30:
                key_factors.append(f"RSI oversold ({rsi:.1f})")

            macd = df['macd'].iloc[-1] if not pd.isna(df['macd'].iloc[-1]) else 0
            if macd > 0:
                key_factors.append("MACD bullish crossover")
            else:
                key_factors.append("MACD bearish crossover")

            if df['close'].iloc[-1] > df['sma_20'].iloc[-1]:
                key_factors.append("Price above SMA20")
            else:
                key_factors.append("Price below SMA20")

            key_factors.extend(regime_analysis.characteristics[:2])

            # Calculate confidence score
            confidence_factors = [
                abs(predictions['1h']) * 100,  # Prediction strength
                regime_analysis.confidence * 100,  # Regime confidence
                min(100, len(support_levels + resistance_levels) * 20)  # S/R levels
            ]
            confidence_score = min(95, np.mean(confidence_factors))

            # Generate recommendations
            if predictions['1h'] > 0.02:
                recommended_action = "STRONG BUY - High upside potential"
            elif predictions['1h'] > 0.005:
                recommended_action = "BUY - Moderate upside expected"
            elif predictions['1h'] > -0.005:
                recommended_action = "HOLD - Sideways movement expected"
            elif predictions['1h'] > -0.02:
                recommended_action = "SELL - Moderate downside risk"
            else:
                recommended_action = "STRONG SELL - High downside risk"

            # Risk assessment
            volatility = df['close'].pct_change().tail(20).std()
            if volatility > 0.05:
                risk_assessment = "HIGH RISK - Extreme volatility"
            elif volatility > 0.03:
                risk_assessment = "MEDIUM-HIGH RISK - High volatility"
            elif volatility > 0.02:
                risk_assessment = "MEDIUM RISK - Moderate volatility"
            else:
                risk_assessment = "LOW-MEDIUM RISK - Low volatility"

            return AIInsight(
                symbol=symbol,
                timestamp=datetime.now(),
                sentiment=sentiment,
                trend_strength=trend_strength,
                price_prediction_1h=current_price * (1 + predictions['1h']),
                price_prediction_4h=current_price * (1 + predictions['4h']),
                price_prediction_24h=current_price * (1 + predictions['24h']),
                confidence_score=confidence_score,
                key_factors=key_factors,
                risk_assessment=risk_assessment,
                recommended_action=recommended_action,
                support_levels=support_levels,
                resistance_levels=resistance_levels,
                volatility_forecast=volatility * 100,
                market_regime=regime_analysis.regime
            )

        except Exception as e:
            logger.error(f"Error generating AI insight for {symbol}: {e}")
            # Return default insight
            return AIInsight(
                symbol=symbol,
                timestamp=datetime.now(),
                sentiment=MarketSentiment.NEUTRAL,
                trend_strength=TrendStrength.MODERATE,
                price_prediction_1h=0,
                price_prediction_4h=0,
                price_prediction_24h=0,
                confidence_score=0,
                key_factors=["Analysis unavailable"],
                risk_assessment="UNKNOWN RISK",
                recommended_action="HOLD - Insufficient data",
                support_levels=[],
                resistance_levels=[],
                volatility_forecast=0,
                market_regime="unknown"
            )

# Global instance
ai_insights = AITradingInsights()

async def get_ai_insights_for_symbols(symbols: List[str]) -> Dict[str, AIInsight]:
    """Get AI insights for multiple symbols"""
    try:
        await ai_insights.initialize_models()

        tasks = [ai_insights.generate_ai_insight(symbol) for symbol in symbols]
        insights = await asyncio.gather(*tasks, return_exceptions=True)

        result = {}
        for symbol, insight in zip(symbols, insights):
            if isinstance(insight, Exception):
                logger.error(f"Error getting insight for {symbol}: {insight}")
                continue
            result[symbol] = insight

        return result

    except Exception as e:
        logger.error(f"Error getting AI insights: {e}")
        return {}

if __name__ == "__main__":
    # Test the AI insights
    async def test_ai_insights():
        symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
        insights = await get_ai_insights_for_symbols(symbols)

        for symbol, insight in insights.items():
            print(f"\n=== AI Insight for {symbol} ===")
            print(f"Sentiment: {insight.sentiment.value}")
            print(f"Trend Strength: {insight.trend_strength.value}")
            print(f"Confidence: {insight.confidence_score:.1f}%")
            print(f"Recommendation: {insight.recommended_action}")
            print(f"Key Factors: {', '.join(insight.key_factors)}")
            print(f"Risk: {insight.risk_assessment}")

    asyncio.run(test_ai_insights())
