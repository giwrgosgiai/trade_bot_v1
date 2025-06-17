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
        response = requests.get(f"{API_BASE}/{endpoint}", auth=AUTH, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error {response.status_code}: {endpoint}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def main():
    st.title("🎯 NFI5MOHO Portfolio Monitor")
    st.markdown("---")

    # Auto refresh
    if st.button("🔄 Refresh Data"):
        st.rerun()

    # Get bot status
    status_data = get_api_data("status")
    if not status_data:
        st.error("❌ Cannot connect to Freqtrade API")
        return

    # Display main metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🤖 Bot Status",
            value="RUNNING" if status_data.get("state") == "RUNNING" else "STOPPED"
        )

    with col2:
        st.metric(
            label="📊 Strategy",
            value=status_data.get("strategy", "N/A")
        )

    with col3:
        st.metric(
            label="⏰ Timeframe",
            value=status_data.get("timeframe", "N/A")
        )

    with col4:
        st.metric(
            label="🔄 Max Trades",
            value=status_data.get("max_open_trades", "N/A")
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
    if trades_data and trades_data.get('open_trades'):
        st.subheader("🔄 Open Trades")

        trades_df = pd.DataFrame(trades_data['open_trades'])
        if not trades_df.empty:
            # Select relevant columns
            display_cols = ['pair', 'side', 'amount', 'open_rate', 'current_rate', 'profit_pct', 'open_date']
            available_cols = [col for col in display_cols if col in trades_df.columns]

            if available_cols:
                st.dataframe(trades_df[available_cols], use_container_width=True)
            else:
                st.write("Open trades data available but columns not recognized")
                st.json(trades_data['open_trades'])
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

    # Auto refresh every 30 seconds
    st.markdown("---")
    st.info("🔄 Dashboard auto-refreshes every 30 seconds")
    time.sleep(30)
    st.rerun()

if __name__ == "__main__":
    main()