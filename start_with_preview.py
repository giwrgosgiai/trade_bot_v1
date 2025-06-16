#!/usr/bin/env python3
"""
Freqtrade Preview System Launcher
Ξεκινάει το Freqtrade με epochs=600 και EarlyStopping(patience=10)
Δείχνει preview των ελέγχων και του profit σε πραγματικό χρόνο
"""

import subprocess
import sys
import time
import logging
from datetime import datetime
import threading
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('preview_logs.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def print_banner():
    """Print startup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    FREQTRADE PREVIEW SYSTEM                  ║
    ║                                                              ║
    ║  🚀 Epochs: 600                                              ║
    ║  ⏹️  Early Stopping: patience=10                             ║
    ║  📊 Real-time Preview: Enabled                               ║
    ║  💰 Profit Tracking: Active                                  ║
    ║  🎯 Condition Monitoring: Live                               ║
    ║                                                              ║
    ║  Strategy: NFI5MOHO_WIP                                      ║
    ║  Timeframe: 5m                                               ║
    ║  Dry Run: 500 USDC                                           ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def monitor_logs():
    """Monitor and display logs in real-time"""
    try:
        # Monitor the freqtrade logs
        cmd = ["tail", "-f", "user_data/logs/freqtrade.log"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        for line in iter(process.stdout.readline, ''):
            if line:
                # Filter and highlight important messages
                if "PREVIEW" in line or "CONDITIONS MET" in line or "Buy signal" in line or "Sell signal" in line:
                    print(f"🔥 {line.strip()}")
                elif "ERROR" in line:
                    print(f"❌ {line.strip()}")
                elif "WARNING" in line:
                    print(f"⚠️  {line.strip()}")
                else:
                    print(line.strip())

    except Exception as e:
        logging.error(f"Error monitoring logs: {e}")

def start_freqtrade():
    """Start Freqtrade with the preview system"""
    try:
        print_banner()

        # Start log monitoring in background
        log_thread = threading.Thread(target=monitor_logs, daemon=True)
        log_thread.start()

        # Start Freqtrade
        cmd = [
            "freqtrade", "trade",
            "--config", "configs/custom_config.json",
            "--dry-run",
            "--strategy", "NFI5MOHO_WIP",
            "--db-url", "sqlite:///preview_trades.db",
            "--logfile", "user_data/logs/freqtrade.log"
        ]

        logging.info("🚀 Starting Freqtrade with Preview System...")
        logging.info(f"Command: {' '.join(cmd)}")

        # Run Freqtrade
        process = subprocess.run(cmd, check=False)

        if process.returncode != 0:
            logging.error(f"Freqtrade exited with code {process.returncode}")
        else:
            logging.info("Freqtrade completed successfully")

    except KeyboardInterrupt:
        logging.info("🛑 Stopping Freqtrade Preview System...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Error starting Freqtrade: {e}")
        sys.exit(1)

def show_preview_status():
    """Show current preview status"""
    status = f"""
    📊 PREVIEW STATUS - {datetime.now().strftime('%H:%M:%S')}
    ═══════════════════════════════════════════════════════════
    🔧 Training Parameters:
       • Epochs: 600
       • Early Stopping Patience: 10

    📈 Strategy Configuration:
       • Name: NFI5MOHO_WIP
       • Timeframe: 5m
       • Max Open Trades: 3
       • Dry Run Wallet: 500 USDC

    🎯 Monitoring:
       • Buy/Sell Conditions: 21 Buy + 8 Sell
       • Real-time Logging: Active
       • Profit Tracking: Enabled

    💡 Features:
       • Live condition checking
       • Signal preview
       • Performance monitoring
       • Early stopping mechanism
    ═══════════════════════════════════════════════════════════
    """
    print(status)

if __name__ == "__main__":
    try:
        # Show initial status
        show_preview_status()

        # Wait a moment for user to read
        time.sleep(3)

        # Start the system
        start_freqtrade()

    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)