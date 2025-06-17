#!/usr/bin/env python3
"""
🎯 Portfolio Monitor Dashboard για NFI5MOHO_WIP
Απλό dashboard που εμφανίζει real-time δεδομένα από το Freqtrade API
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import time

# Configuration
API_BASE = "http://localhost:8080/api/v1"
AUTH = ("freqtrade", "ruriu7AY")

st.set_page_config(
    page_title="🎯 NFI5MOHO Portfolio Monitor",
    page_icon="🎯",
    layout="wide"
)

def get_api_data(endpoint):
    """Παίρνει δεδομένα από το Freqtrade API"""
    try:
        response = requests.get(f"{API_BASE}/{endpoint}", auth=AUTH, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("❌ Authentication failed - Check API credentials")
            return None
        else:
            st.error(f"❌ API Error {response.status_code}: {endpoint}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to Freqtrade API - Make sure the bot is running")
        return None
    except requests.exceptions.Timeout:
        st.error("❌ API request timeout - Bot may be busy")
        return None
    except Exception as e:
        st.error(f"❌ Connection Error: {str(e)}")
        return None

def main():
    st.title("🎯 NFI5MOHO Portfolio Monitor")
    st.markdown("---")

    # Connection info
    st.info(f"🔗 Connecting to: {API_BASE}")

    # Auto refresh
    if st.button("🔄 Refresh Data"):
        st.rerun()

    # Test API connection
    ping_data = get_api_data("ping")
    if ping_data:
        st.success("✅ API Connection: OK")
    else:
        st.error("❌ API Connection: Failed")
        return

    # Get bot status - handle both cases (empty list or dict)
    status_data = get_api_data("status")
    if status_data is None:
        st.error("❌ Cannot connect to Freqtrade API")
        return

    # Get additional bot info
    show_config = get_api_data("show_config")

    # Display main metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Bot is running if API responds
        st.metric(
            label="🤖 Bot Status",
            value="RUNNING"
        )

    with col2:
        strategy = "NFI5MOHO_WIP"
        if show_config and show_config.get("strategy"):
            strategy = show_config["strategy"]
        st.metric(
            label="📊 Strategy",
            value=strategy
        )

    with col3:
        timeframe = "15m"
        if show_config and show_config.get("timeframe"):
            timeframe = show_config["timeframe"]
        st.metric(
            label="⏰ Timeframe",
            value=timeframe
        )

    with col4:
        max_trades = 3
        if show_config and show_config.get("max_open_trades"):
            max_trades = show_config["max_open_trades"]
        st.metric(
            label="🔄 Max Trades",
            value=max_trades
        )

    st.markdown("---")

    # Get balance data
    balance_data = get_api_data("balance")
    if balance_data:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="💰 Total Balance",
                value=f"{balance_data.get('total', 0):.2f} USDC"
            )

        with col2:
            st.metric(
                label="💵 Starting Capital",
                value=f"{balance_data.get('starting_capital', 0):.2f} USDC"
            )

        with col3:
            pnl_pct = balance_data.get('starting_capital_pct', 0)
            st.metric(
                label="📈 P&L %",
                value=f"{pnl_pct:.2f}%",
                delta=f"{pnl_pct:.2f}%"
            )

        with col4:
            pnl_abs = balance_data.get('total', 0) - balance_data.get('starting_capital', 0)
            st.metric(
                label="💲 P&L Absolute",
                value=f"{pnl_abs:.2f} USDC",
                delta=f"{pnl_abs:.2f} USDC"
            )

    st.markdown("---")

    # Get profit data
    profit_data = get_api_data("profit")
    if profit_data:
        st.subheader("📊 Profit Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="🏆 Total Profit",
                value=f"{profit_data.get('profit_total_abs', 0):.2f} USDC"
            )

        with col2:
            st.metric(
                label="📈 Profit %",
                value=f"{profit_data.get('profit_total', 0):.2f}%"
            )

        with col3:
            st.metric(
                label="🔢 Total Trades",
                value=profit_data.get('trade_count', 0)
            )

    st.markdown("---")

    # Get open trades
    trades_data = get_api_data("status")
    st.subheader("🔄 Open Trades")

    if trades_data and isinstance(trades_data, list) and len(trades_data) > 0:
        # We have open trades
        trades_df = pd.DataFrame(trades_data)
        if not trades_df.empty:
            # Select relevant columns
            display_cols = ['pair', 'side', 'amount', 'open_rate', 'current_rate', 'profit_pct', 'open_date']
            available_cols = [col for col in display_cols if col in trades_df.columns]

            if available_cols:
                st.dataframe(trades_df[available_cols], use_container_width=True)
            else:
                st.write("Open trades data available but columns not recognized")
                st.json(trades_data)
        else:
            st.info("✅ No open trades")
    else:
        st.info("✅ No open trades")

    # Performance metrics
    performance_data = get_api_data("performance")
    if performance_data:
        st.subheader("🎯 Pair Performance")
        perf_df = pd.DataFrame(performance_data)
        if not perf_df.empty:
            st.dataframe(perf_df, use_container_width=True)

    # Debug info (expandable)
    st.markdown("---")
    with st.expander("🔧 Debug Info"):
        st.write("**API Responses:**")

        if balance_data:
            st.write("Balance Data:")
            st.json(balance_data)

        if profit_data:
            st.write("Profit Data:")
            st.json(profit_data)

        if show_config:
            st.write("Bot Config:")
            st.json(show_config)

    # Auto refresh info
    st.info("🔄 Click 'Refresh Data' button to update or refresh the page manually")

if __name__ == "__main__":
    main()