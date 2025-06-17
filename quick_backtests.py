#!/usr/bin/env python3
"""
Quick Backtests Script
Γρήγορα backtests με διαφορετικά timeframes και περιόδους
"""

import subprocess
import json
import os
from datetime import datetime

def run_quick_backtest(timeframe, timerange, description):
    """Τρέχει ένα γρήγορο backtest"""
    print(f"\n🚀 {description}")
    print(f"   Timeframe: {timeframe}")
    print(f"   Timerange: {timerange}")

    cmd = [
        "freqtrade", "backtesting",
        "--config", "user_data/config.json",
        "--strategy", "NFI5MOHO_WIP",
        "--timeframe", timeframe,
        "--timerange", timerange,
        "--breakdown", "day"
    ]

    try:
        result = subprocess.run(cmd, text=True, timeout=120)
        if result.returncode == 0:
            print(f"   ✅ Επιτυχές!")
        else:
            print(f"   ❌ Αποτυχία")
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout")
    except Exception as e:
        print(f"   💥 Σφάλμα: {str(e)}")

def main():
    """Main function για γρήγορα backtests"""
    print("⚡ Quick Backtests")
    print("=" * 20)

    # Διαφορετικά scenarios
    scenarios = [
        ("5m", "20241210-20241217", "Τελευταία εβδομάδα - 5m"),
        ("15m", "20241210-20241217", "Τελευταία εβδομάδα - 15m"),
        ("1h", "20241210-20241217", "Τελευταία εβδομάδα - 1h"),

        ("5m", "20241201-20241217", "Τελευταίες 2+ εβδομάδες - 5m"),
        ("15m", "20241201-20241217", "Τελευταίες 2+ εβδομάδες - 15m"),
        ("1h", "20241201-20241217", "Τελευταίες 2+ εβδομάδες - 1h"),

        ("5m", "20241115-20241217", "Τελευταίος μήνας - 5m"),
        ("1h", "20241115-20241217", "Τελευταίος μήνας - 1h"),
    ]

    for timeframe, timerange, description in scenarios:
        run_quick_backtest(timeframe, timerange, description)

    print("\n🎉 Όλα τα γρήγορα backtests ολοκληρώθηκαν!")

if __name__ == "__main__":
    main()