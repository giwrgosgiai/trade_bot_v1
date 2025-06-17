#!/usr/bin/env python3
"""
Hyperopt script for NFI5MOHO_WIP strategy
Runs hyperopt with 1000 epochs and early stopping after 20 consecutive epochs without improvement
"""

import os
import sys
import subprocess
import time
import json
import sqlite3
from datetime import datetime
from pathlib import Path

# Add freqtrade to path
sys.path.append(str(Path("/Users/georgegiailoglou/Documents/GitHub/trade_bot_v1/freqtrade")))

class HyperoptRunner:
    def __init__(self):
        self.project_root = Path.cwd()
        self.config_file = str(self.project_root / "configs" / "hyperopt_config.json")
        self.strategy = "NFI5MOHO_WIP"
        self.max_epochs = 50  # Reduced for testing
        self.early_stop_patience = 20
        self.db_file = str(self.project_root / "user_data" / "hyperopt_nfi5moho.sqlite")
        self.log_file = str(self.project_root / "logs" / "hyperopt_nfi5moho.log")
        self.best_result = None
        self.epochs_without_improvement = 0
        self.current_epoch = 0

    def setup_directories(self):
        """Create necessary directories"""
        os.makedirs("logs", exist_ok=True)
        os.makedirs("user_data", exist_ok=True)

    def get_best_result_from_db(self):
        """Get the best result from hyperopt database"""
        try:
            if not os.path.exists(self.db_file):
                return None

            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # Get the best result (highest profit)
            cursor.execute("""
                SELECT MAX(results_metrics) as best_profit, COUNT(*) as total_epochs
                FROM trials
                WHERE results_metrics IS NOT NULL
            """)

            result = cursor.fetchone()
            conn.close()

            if result and result[0] is not None:
                return {
                    'best_profit': float(result[0]),
                    'total_epochs': int(result[1])
                }
            return None

        except Exception as e:
            print(f"Error reading database: {e}")
            return None

    def check_early_stopping(self):
        """Check if we should stop early due to no improvement"""
        current_best = self.get_best_result_from_db()

        if current_best is None:
            return False

        self.current_epoch = current_best['total_epochs']

        if self.best_result is None:
            self.best_result = current_best['best_profit']
            self.epochs_without_improvement = 0
            return False

        if current_best['best_profit'] > self.best_result:
            print(f"✅ New best result found: {current_best['best_profit']:.6f} (previous: {self.best_result:.6f})")
            self.best_result = current_best['best_profit']
            self.epochs_without_improvement = 0
            return False
        else:
            self.epochs_without_improvement += 1
            print(f"⏳ No improvement for {self.epochs_without_improvement} epochs (best: {self.best_result:.6f})")

            if self.epochs_without_improvement >= self.early_stop_patience:
                print(f"🛑 Early stopping triggered after {self.epochs_without_improvement} epochs without improvement")
                return True

        return False

    def run_backtest(self):
        """Run backtest with current strategy parameters"""
        # Get absolute paths
        project_root = Path.cwd()
        config_path = project_root / "user_data" / "config.json"
        strategy_path = project_root / "user_data" / "strategies"
        data_path = project_root / "user_data" / "data"

        cmd = [
            "python3", "-m", "freqtrade", "backtesting",
            "--config", str(config_path),
            "--strategy", self.strategy,
            "--strategy-path", str(strategy_path),
            "--timerange", "20241201-20241217",
            "--export", "trades",
            "--export-filename", "../backtest/backtest_current_params.json",
            "--datadir", str(data_path)
        ]

        print(f"🚀 Running backtest...")
        print(f"Command: {' '.join(cmd)}")

        try:
            # Change to freqtrade directory
            os.chdir("freqtrade")

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            # Change back to original directory
            os.chdir("..")

            print(f"STDOUT: {process.stdout}")
            if process.stderr:
                print(f"STDERR: {process.stderr}")

            if process.returncode != 0:
                print(f"❌ Backtest failed with return code {process.returncode}")
                return False

            print(f"✅ Backtest completed successfully")
            return True

        except subprocess.TimeoutExpired:
            print("⏰ Backtest timed out")
            os.chdir("..")
            return False
        except Exception as e:
            print(f"❌ Error running backtest: {e}")
            os.chdir("..")
            return False

    def run(self):
        """Main backtest runner"""
        print("🎯 Starting Backtest for NFI5MOHO_WIP Strategy")
        print(f"📁 Config file: {self.config_file}")
        print("=" * 60)

        self.setup_directories()

        # Run backtest
        if self.run_backtest():
            print("\n" + "=" * 60)
            print("🏆 BACKTEST COMPLETED SUCCESSFULLY")
            print("📊 Check the results in the output above")
            print("=" * 60)
        else:
            print("\n❌ Backtest failed")

def main():
    """Main function"""
    runner = HyperoptRunner()
    runner.run()

if __name__ == "__main__":
    main()