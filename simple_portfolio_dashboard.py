#!/usr/bin/env python3
"""
🎯 Simple Portfolio Dashboard για NFI5MOHO_WIP
Εμφανίζει real-time δεδομένα από το Freqtrade API
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import time
import plotly.graph_objects as go
import plotly.express as px

# Configuration
API_BASE = "http://localhost:8080/api/v1"
AUTH = ("freqtrade", "ruriu7AY")

st.set_page_config(
    page_title="NFI5MOHO Portfolio Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_api_data(endpoint):
    """Παίρνει δεδομένα από το Freqtrade API"""
    try:
        response = requests.get(f"{API_BASE}/{endpoint}", auth=AUTH, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

def main():
    st.title("🎯 NFI5MOHO Portfolio Dashboard")
    st.markdown("---")

    # Auto-refresh
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()

    # Auto-refresh every 30 seconds
    auto_refresh = st.sidebar.checkbox("Auto Refresh (30s)", value=True)
    if auto_refresh:
        time.sleep(30)
        st.rerun()

    # Get data
    balance_data = get_api_data("balance")
    status_data = get_api_data("status")
    profit_data = get_api_data("profit")

    if not balance_data:
        st.error("❌ Cannot connect to Freqtrade API")
        st.info("Make sure the bot is running on port 8080")
        return

    # Main metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "💰 Current Balance",
            f"{balance_data['total']:.2f} USDC",
            f"{balance_data['starting_capital_pct']:.2f}%"
        )

    with col2:
        st.metric(
            "🎯 Starting Capital",
            f"{balance_data['starting_capital']:.2f} USDC"
        )

    with col3:
        if profit_data:
            st.metric(
                "📊 Total Trades",
                profit_data.get('trade_count', 0),
                f"Win Rate: {profit_data.get('winrate', 0)*100:.1f}%"
            )

    with col4:
        if profit_data:
            st.metric(
                "💎 Profit/Loss",
                f"{profit_data.get('profit_all_coin', 0):.2f} USDC",
                f"{profit_data.get('profit_all_percent', 0):.2f}%"
            )

    st.markdown("---")

    # Current positions
    st.subheader("📈 Current Positions")
    if status_data and len(status_data) > 0:
        df = pd.DataFrame(status_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No open positions currently")

    # Balance breakdown
    st.subheader("💰 Balance Breakdown")
    if balance_data and 'currencies' in balance_data:
        for currency in balance_data['currencies']:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**{currency['currency']}**")
            with col2:
                st.write(f"Free: {currency['free']:.4f}")
            with col3:
                st.write(f"Used: {currency['used']:.4f}")

    # Performance metrics
    if profit_data:
        st.subheader("📊 Performance Metrics")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Trading Statistics:**")
            st.write(f"• Total Trades: {profit_data.get('trade_count', 0)}")
            st.write(f"• Winning Trades: {profit_data.get('winning_trades', 0)}")
            st.write(f"• Losing Trades: {profit_data.get('losing_trades', 0)}")
            st.write(f"• Win Rate: {profit_data.get('winrate', 0)*100:.1f}%")
            st.write(f"• Average Duration: {profit_data.get('avg_duration', 'N/A')}")

        with col2:
            st.write("**Profit Metrics:**")
            st.write(f"• Total P&L: {profit_data.get('profit_all_coin', 0):.4f} USDC")
            st.write(f"• Total P&L %: {profit_data.get('profit_all_percent', 0):.2f}%")
            st.write(f"• Best Pair: {profit_data.get('best_pair', 'N/A')}")
            st.write(f"• Best Rate: {profit_data.get('best_rate', 0):.2f}%")
            st.write(f"• Expectancy: {profit_data.get('expectancy', 0):.4f}")

    # Strategy info
    st.subheader("🎯 Strategy Information")
    st.info("**NFI5MOHO_WIP Strategy** - Optimized with Hyperopt for 15m timeframe")
    st.write("• Timeframe: 15 minutes")
    st.write("• Max Open Trades: 3")
    st.write("• Stoploss: -20%")
    st.write("• Trailing Stop: Enabled")

    # Footer
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()