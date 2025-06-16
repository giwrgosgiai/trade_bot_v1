#!/usr/bin/env python3
"""
NFI5MOHO_WIP Bot Starter
Ξεκινάει το freqtrade bot με τη στρατηγική NFI5MOHO_WIP
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_bot_status():
    """Ελέγχει αν το bot τρέχει"""
    try:
        response = requests.get("http://localhost:8080/api/v1/status",
                              auth=("freqtrade", "ruriu7AY"),
                              timeout=5)
        return response.status_code == 200
    except:
        return False

def start_freqtrade_bot():
    """Ξεκινάει το freqtrade bot"""
    print("🚀 Starting NFI5MOHO_WIP FreqTrade Bot...")

    # Change to freqtrade directory
    freqtrade_dir = Path.cwd() / "freqtrade"
    os.chdir(freqtrade_dir)

    # Start freqtrade with NFI5MOHO_WIP strategy
    cmd = [
        "python3", "-m", "freqtrade", "trade",
        "--config", "user_data/config.json",
        "--strategy", "NFI5MOHO_WIP",
        "--dry-run",
        "--logfile", "logs/nfi5moho_bot.log"
    ]

    print(f"📝 Command: {' '.join(cmd)}")
    print(f"📁 Working directory: {freqtrade_dir}")

    # Start the process
    process = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             text=True)

    print(f"🔄 Bot started with PID: {process.pid}")

    # Wait a bit and check if it's running
    time.sleep(10)

    if check_bot_status():
        print("✅ Bot is running successfully!")
        print("📊 API available at: http://localhost:8080")
        print("🎯 Strategy: NFI5MOHO_WIP")
        print("💧 Mode: Dry Run")
        return True
    else:
        print("❌ Bot failed to start properly")
        # Print any error output
        stdout, stderr = process.communicate(timeout=5)
        if stderr:
            print(f"Error: {stderr}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("🤖 NFI5MOHO_WIP FreqTrade Bot Starter")
    print("=" * 60)

    # Check if already running
    if check_bot_status():
        print("ℹ️  Bot is already running!")
        print("📊 Dashboard: http://localhost:8504")
        return

    # Start the bot
    if start_freqtrade_bot():
        print("\n🎉 Bot started successfully!")
        print("📊 Strategy Monitor: http://localhost:8504")
        print("🔧 FreqTrade UI: http://localhost:8080")
        print("\n💡 To stop the bot, use Ctrl+C or kill the process")
    else:
        print("\n❌ Failed to start bot. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()