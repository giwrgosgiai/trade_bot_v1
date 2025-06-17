#!/usr/bin/env python3
"""
🚀 Enhanced Telegram Bot Starter για NFI5MOHO_WIP
Ξεκινάει το enhanced telegram bot με όλες τις λειτουργίες
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    """Ξεκίνημα του Enhanced Telegram Bot"""
    print("🚀 Starting Enhanced Telegram Bot για NFI5MOHO_WIP...")

    # Έλεγχος αν υπάρχει το logs directory
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True, exist_ok=True)
        print("📁 Created logs directory")

    # Έλεγχος αν το bot τρέχει ήδη
    try:
        result = subprocess.run(
            ["pgrep", "-f", "enhanced_telegram_bot.py"],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            print("⚠️  Enhanced Telegram Bot is already running!")
            print(f"PID: {result.stdout.strip()}")
            return
    except:
        pass

    # Ξεκίνημα του bot
    try:
        print("🤖 Starting Enhanced Telegram Bot...")
        print("📊 Strategy: NFI5MOHO_WIP")
        print("🔧 Features: Hyperopt, Live Tracking, System Monitoring")
        print("🇬🇷 Interface: Greek + English")
        print()

        # Εκτέλεση του bot
        subprocess.run([
            sys.executable,
            "apps/telegram/enhanced_telegram_bot.py"
        ])

    except KeyboardInterrupt:
        print("\n🛑 Enhanced Telegram Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting Enhanced Telegram Bot: {e}")

if __name__ == "__main__":
    main()