#!/usr/bin/env python3
"""
Download historical data for hyperopt
Downloads 5m and 1h data for the pairs specified in the config
"""

import os
import sys
import subprocess
from pathlib import Path

def download_data():
    """Download historical data for hyperopt"""

    # Pairs to download (matching the config)
    pairs = [
        "BTC/USDC",
        "ETH/USDC",
        "ADA/USDC",
        "DOT/USDC",
        "SOL/USDC",
        "MATIC/USDC",
        "LINK/USDC",
        "AVAX/USDC",
        "UNI/USDC"
    ]

    # Timeframes needed
    timeframes = ["5m", "1h"]

    # Time range for data
    timerange = "20240101-20240301"

    print("📥 Downloading historical data for hyperopt...")
    print(f"Pairs: {', '.join(pairs)}")
    print(f"Timeframes: {', '.join(timeframes)}")
    print(f"Time range: {timerange}")
    print("=" * 60)

    # Change to freqtrade directory
    os.chdir("freqtrade")

    for timeframe in timeframes:
        print(f"\n📊 Downloading {timeframe} data...")

        cmd = [
            "python3", "-m", "freqtrade", "download-data",
            "--config", "../configs/hyperopt_config.json",
            "--exchange", "binance",
            "--pairs"] + pairs + [
            "--timeframes", timeframe,
            "--timerange", timerange,
            "--datadir", "user_data/data"
        ]

        print(f"Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

            if result.returncode == 0:
                print(f"✅ Successfully downloaded {timeframe} data")
            else:
                print(f"❌ Failed to download {timeframe} data")
                print(f"Error: {result.stderr}")

        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout downloading {timeframe} data")
        except Exception as e:
            print(f"❌ Error downloading {timeframe} data: {e}")

    # Change back to original directory
    os.chdir("..")

    print("\n🏁 Data download completed!")
    print("You can now run the hyperopt with: ./run_hyperopt_nfi5moho.sh")

if __name__ == "__main__":
    download_data()