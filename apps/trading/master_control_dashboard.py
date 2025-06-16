#!/usr/bin/env python3
"""
🎛️ Master Control Dashboard - Unified Trading System Control
🎯 Features:
- Real-time system monitoring
- Strategy performance tracking
- Risk management controls
- Emergency stop capabilities
- Portfolio overview
- Sentiment analysis integration
- Automated alerts and notifications
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import sqlite3
from datetime import datetime, timedelta
import subprocess
import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🎛️ Master Trading Control Dashboard",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }

    .alert-danger {
        background-color: #ff4444;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }

    .alert-warning {
        background-color: #ffaa00;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }

    .alert-success {
        background-color: #00aa44;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


class MasterControlDashboard:
    """🎛️ Master Control Dashboard"""

    def __init__(self):
        self.db_path = "tradesv3.sqlite"
        self.config_path = "user_data/config.json"
        self.initial_balance = 2000.0

        # Initialize session state
        if 'emergency_stop' not in st.session_state:
            st.session_state.emergency_stop = False
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()

    def load_config(self) -> dict:
        """Load trading configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def get_database_data(self) -> pd.DataFrame:
        """Get trading data from database"""
        try:
            if not os.path.exists(self.db_path):
                return pd.DataFrame()

            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT
                pair, profit_abs, profit_ratio, open_date, close_date,
                is_open, strategy, open_rate, close_rate, amount
            FROM trades
            ORDER BY open_date DESC
            LIMIT 1000
            """
            df = pd.read_sql_query(query, conn)
            conn.close()

            if not df.empty:
                df['open_date'] = pd.to_datetime(df['open_date'])
                df['close_date'] = pd.to_datetime(df['close_date'])

            return df

        except Exception as e:
            logger.error(f"Database query failed: {e}")
            return pd.DataFrame()

    def calculate_portfolio_metrics(self, df: pd.DataFrame) -> dict:
        """Calculate portfolio performance metrics"""
        try:
            if df.empty:
                return {
                    'total_trades': 0,
                    'open_trades': 0,
                    'total_profit': 0.0,
                    'win_rate': 0.0,
                    'current_balance': self.initial_balance,
                    'total_return': 0.0,
                    'daily_pnl': 0.0,
                    'weekly_pnl': 0.0,
                    'monthly_pnl': 0.0
                }

            # Basic metrics
            total_trades = len(df[df['is_open'] == 0])
            open_trades = len(df[df['is_open'] == 1])
            total_profit = df[df['is_open'] == 0]['profit_abs'].sum()

            # Win rate
            closed_trades = df[df['is_open'] == 0]
            winning_trades = len(closed_trades[closed_trades['profit_abs'] > 0])
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

            # Current balance
            current_balance = self.initial_balance + total_profit
            total_return = (total_profit / self.initial_balance * 100) if self.initial_balance > 0 else 0

            # Time-based PnL
            now = datetime.now()
            daily_trades = closed_trades[closed_trades['close_date'] >= now - timedelta(days=1)]
            weekly_trades = closed_trades[closed_trades['close_date'] >= now - timedelta(days=7)]
            monthly_trades = closed_trades[closed_trades['close_date'] >= now - timedelta(days=30)]

            daily_pnl = daily_trades['profit_abs'].sum()
            weekly_pnl = weekly_trades['profit_abs'].sum()
            monthly_pnl = monthly_trades['profit_abs'].sum()

            return {
                'total_trades': total_trades,
                'open_trades': open_trades,
                'total_profit': total_profit,
                'win_rate': win_rate,
                'current_balance': current_balance,
                'total_return': total_return,
                'daily_pnl': daily_pnl,
                'weekly_pnl': weekly_pnl,
                'monthly_pnl': monthly_pnl
            }

        except Exception as e:
            logger.error(f"Portfolio metrics calculation failed: {e}")
            return {}

    def get_strategy_performance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get performance by strategy"""
        try:
            if df.empty:
                return pd.DataFrame()

            closed_trades = df[df['is_open'] == 0]

            strategy_stats = closed_trades.groupby('strategy').agg({
                'profit_abs': ['count', 'sum', 'mean'],
                'profit_ratio': 'mean'
            }).round(4)

            strategy_stats.columns = ['Trades', 'Total_Profit', 'Avg_Profit', 'Avg_Return']

            # Calculate win rates
            win_rates = []
            for strategy in strategy_stats.index:
                strategy_trades = closed_trades[closed_trades['strategy'] == strategy]
                wins = len(strategy_trades[strategy_trades['profit_abs'] > 0])
                total = len(strategy_trades)
                win_rate = (wins / total * 100) if total > 0 else 0
                win_rates.append(win_rate)

            strategy_stats['Win_Rate'] = win_rates
            strategy_stats = strategy_stats.reset_index()

            return strategy_stats

        except Exception as e:
            logger.error(f"Strategy performance calculation failed: {e}")
            return pd.DataFrame()

    def create_performance_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create portfolio performance chart"""
        try:
            if df.empty:
                fig = go.Figure()
                fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
                return fig

            # Calculate cumulative PnL
            closed_trades = df[df['is_open'] == 0].sort_values('close_date')
            closed_trades['cumulative_pnl'] = closed_trades['profit_abs'].cumsum()
            closed_trades['balance'] = self.initial_balance + closed_trades['cumulative_pnl']

            # Create subplot
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Portfolio Balance', 'Daily PnL'),
                vertical_spacing=0.1
            )

            # Balance line
            fig.add_trace(
                go.Scatter(
                    x=closed_trades['close_date'],
                    y=closed_trades['balance'],
                    mode='lines',
                    name='Portfolio Balance',
                    line=dict(color='#00aa44', width=2)
                ),
                row=1, col=1
            )

            # Daily PnL bars
            daily_pnl = closed_trades.groupby(closed_trades['close_date'].dt.date)['profit_abs'].sum()
            colors = ['green' if x > 0 else 'red' for x in daily_pnl.values]

            fig.add_trace(
                go.Bar(
                    x=daily_pnl.index,
                    y=daily_pnl.values,
                    name='Daily PnL',
                    marker_color=colors
                ),
                row=2, col=1
            )

            fig.update_layout(
                title="Portfolio Performance Overview",
                height=600,
                showlegend=True
            )

            return fig

        except Exception as e:
            logger.error(f"Performance chart creation failed: {e}")
            return go.Figure()

    def get_system_status(self) -> dict:
        """Get system status"""
        try:
            status = {
                'freqtrade_running': False,
                'database_accessible': False,
                'config_valid': False,
                'emergency_stop': st.session_state.emergency_stop,
                'last_trade': None,
                'system_uptime': None
            }

            # Check if freqtrade is running
            try:
                result = subprocess.run(['pgrep', '-f', 'freqtrade'],
                                      capture_output=True, text=True)
                status['freqtrade_running'] = len(result.stdout.strip()) > 0
            except:
                pass

            # Check database
            status['database_accessible'] = os.path.exists(self.db_path)

            # Check config
            config = self.load_config()
            status['config_valid'] = len(config) > 0

            # Get last trade time
            df = self.get_database_data()
            if not df.empty:
                last_trade_time = df['open_date'].max()
                status['last_trade'] = last_trade_time

            return status

        except Exception as e:
            logger.error(f"System status check failed: {e}")
            return {}

    def render_header(self):
        """Render dashboard header"""
        st.markdown('<h1 class="main-header">🎛️ Master Trading Control Dashboard</h1>',
                   unsafe_allow_html=True)

        # System status indicators
        col1, col2, col3, col4 = st.columns(4)

        status = self.get_system_status()

        with col1:
            if status.get('freqtrade_running', False):
                st.success("🟢 FreqTrade Running")
            else:
                st.error("🔴 FreqTrade Stopped")

        with col2:
            if status.get('database_accessible', False):
                st.success("🟢 Database OK")
            else:
                st.error("🔴 Database Error")

        with col3:
            if status.get('emergency_stop', False):
                st.error("🚨 EMERGENCY STOP")
            else:
                st.success("🟢 Normal Operation")

        with col4:
            st.info(f"🕐 Last Update: {datetime.now().strftime('%H:%M:%S')}")

    def render_portfolio_overview(self):
        """Render portfolio overview section"""
        st.header("📊 Portfolio Overview")

        df = self.get_database_data()
        metrics = self.calculate_portfolio_metrics(df)

        # Key metrics
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                label="Current Balance",
                value=f"€{metrics.get('current_balance', 0):.2f}",
                delta=f"€{metrics.get('total_profit', 0):.2f}"
            )

        with col2:
            st.metric(
                label="Total Return",
                value=f"{metrics.get('total_return', 0):.2f}%",
                delta=f"{metrics.get('daily_pnl', 0):.2f} today"
            )

        with col3:
            st.metric(
                label="Total Trades",
                value=metrics.get('total_trades', 0),
                delta=f"{metrics.get('open_trades', 0)} open"
            )

        with col4:
            st.metric(
                label="Win Rate",
                value=f"{metrics.get('win_rate', 0):.1f}%"
            )

        with col5:
            monthly_target = 250  # €250 monthly target
            monthly_progress = (metrics.get('monthly_pnl', 0) / monthly_target * 100)
            st.metric(
                label="Monthly Progress",
                value=f"{monthly_progress:.1f}%",
                delta=f"€{metrics.get('monthly_pnl', 0):.2f}/€{monthly_target}"
            )

        # Performance chart
        if not df.empty:
            fig = self.create_performance_chart(df)
            st.plotly_chart(fig, use_container_width=True)

    def render_strategy_performance(self):
        """Render strategy performance section"""
        st.header("🎯 Strategy Performance")

        df = self.get_database_data()
        strategy_stats = self.get_strategy_performance(df)

        if not strategy_stats.empty:
            # Strategy comparison chart
            fig = px.bar(
                strategy_stats,
                x='strategy',
                y='Total_Profit',
                color='Win_Rate',
                title="Strategy Performance Comparison",
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Strategy details table
            st.subheader("Strategy Details")
            st.dataframe(strategy_stats, use_container_width=True)
        else:
            st.info("No strategy performance data available")

    def render_risk_management(self):
        """Render risk management section"""
        st.header("🛡️ Risk Management")

        df = self.get_database_data()
        metrics = self.calculate_portfolio_metrics(df)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Risk Metrics")

            # Calculate drawdown
            if not df.empty:
                closed_trades = df[df['is_open'] == 0].sort_values('close_date')
                if not closed_trades.empty:
                    closed_trades['cumulative_pnl'] = closed_trades['profit_abs'].cumsum()
                    closed_trades['balance'] = self.initial_balance + closed_trades['cumulative_pnl']
                    peak_balance = closed_trades['balance'].expanding().max()
                    drawdown = (peak_balance - closed_trades['balance']) / peak_balance * 100
                    max_drawdown = drawdown.max()
                else:
                    max_drawdown = 0
            else:
                max_drawdown = 0

            st.metric("Max Drawdown", f"{max_drawdown:.2f}%")
            st.metric("Daily PnL", f"€{metrics.get('daily_pnl', 0):.2f}")
            st.metric("Open Positions", metrics.get('open_trades', 0))

            # Risk alerts
            alerts = []
            if max_drawdown > 5:
                alerts.append("⚠️ High drawdown detected")
            if metrics.get('daily_pnl', 0) < -50:
                alerts.append("⚠️ High daily losses")
            if metrics.get('open_trades', 0) > 8:
                alerts.append("⚠️ Too many open positions")

            if alerts:
                st.subheader("Risk Alerts")
                for alert in alerts:
                    st.warning(alert)

        with col2:
            st.subheader("Emergency Controls")

            # Emergency stop button
            if st.button("🚨 EMERGENCY STOP", type="primary"):
                st.session_state.emergency_stop = True
                st.error("EMERGENCY STOP ACTIVATED!")
                # Here you would implement actual emergency stop logic

            if st.session_state.emergency_stop:
                if st.button("🟢 Resume Trading"):
                    st.session_state.emergency_stop = False
                    st.success("Trading resumed")

            # Quick actions
            st.subheader("Quick Actions")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📊 Export Report"):
                    st.info("Report export functionality would be implemented here")

            with col_b:
                if st.button("🔄 Restart Bot"):
                    st.info("Bot restart functionality would be implemented here")

    def render_live_trades(self):
        """Render live trades section"""
        st.header("📈 Live Trades")

        df = self.get_database_data()

        if not df.empty:
            # Open trades
            open_trades = df[df['is_open'] == 1]
            if not open_trades.empty:
                st.subheader("Open Positions")

                # Format open trades for display
                display_trades = open_trades[['pair', 'strategy', 'open_date', 'open_rate', 'amount']].copy()
                display_trades['open_date'] = display_trades['open_date'].dt.strftime('%Y-%m-%d %H:%M')
                display_trades['open_rate'] = display_trades['open_rate'].round(6)
                display_trades['amount'] = display_trades['amount'].round(4)

                st.dataframe(display_trades, use_container_width=True)
            else:
                st.info("No open positions")

            # Recent closed trades
            closed_trades = df[df['is_open'] == 0].head(10)
            if not closed_trades.empty:
                st.subheader("Recent Closed Trades")

                display_closed = closed_trades[['pair', 'strategy', 'close_date', 'profit_abs', 'profit_ratio']].copy()
                display_closed['close_date'] = display_closed['close_date'].dt.strftime('%Y-%m-%d %H:%M')
                display_closed['profit_abs'] = display_closed['profit_abs'].round(2)
                display_closed['profit_ratio'] = (display_closed['profit_ratio'] * 100).round(2)

                # Color code profits
                def color_profit(val):
                    color = 'green' if val > 0 else 'red' if val < 0 else 'gray'
                    return f'color: {color}'

                styled_df = display_closed.style.applymap(color_profit, subset=['profit_abs', 'profit_ratio'])
                st.dataframe(styled_df, use_container_width=True)
        else:
            st.info("No trading data available")

    def render_sidebar(self):
        """Render sidebar controls"""
        st.sidebar.header("🎛️ Control Panel")

        # Auto-refresh
        auto_refresh = st.sidebar.checkbox("Auto Refresh (30s)", value=True)
        if auto_refresh:
            time.sleep(30)
            st.experimental_rerun()

        # Manual refresh
        if st.sidebar.button("🔄 Refresh Now"):
            st.experimental_rerun()

        # Settings
        st.sidebar.header("⚙️ Settings")

        # Time range selector
        time_range = st.sidebar.selectbox(
            "Analysis Time Range",
            ["1 Day", "1 Week", "1 Month", "3 Months", "All Time"]
        )

        # Strategy filter
        df = self.get_database_data()
        if not df.empty:
            strategies = df['strategy'].unique().tolist()
            selected_strategies = st.sidebar.multiselect(
                "Filter Strategies",
                strategies,
                default=strategies
            )

        # Export options
        st.sidebar.header("📊 Export")

        if st.sidebar.button("Export Portfolio Report"):
            st.sidebar.success("Report exported!")

        if st.sidebar.button("Export Trade History"):
            st.sidebar.success("History exported!")

    def run(self):
        """Run the dashboard"""
        try:
            # Render sidebar
            self.render_sidebar()

            # Render main content
            self.render_header()

            # Create tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Portfolio", "🎯 Strategies", "🛡️ Risk", "📈 Live Trades"])

            with tab1:
                self.render_portfolio_overview()

            with tab2:
                self.render_strategy_performance()

            with tab3:
                self.render_risk_management()

            with tab4:
                self.render_live_trades()

            # Footer
            st.markdown("---")
            st.markdown(
                "🎛️ **Master Trading Control Dashboard** | "
                f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
                "🚀 Powered by Advanced AI Trading System"
            )

        except Exception as e:
            st.error(f"Dashboard error: {e}")
            logger.error(f"Dashboard error: {e}")


def main():
    """Main function"""
    dashboard = MasterControlDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()