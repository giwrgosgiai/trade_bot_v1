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
        self.config_file = "/Users/georgegiailoglou/Documents/GitHub/trade_bot_v1/configs/hyperopt_config.json"
        self.strategy = "NFI5MOHO_WIP"
        self.max_epochs = 1000
        self.early_stop_patience = 20
        self.db_file = "user_data/hyperopt_nfi5moho.sqlite"
        self.log_file = "logs/hyperopt_nfi5moho.log"
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

    def run_hyperopt_batch(self, batch_size=50):
        """Run hyperopt in batches to check for early stopping"""
        # Get absolute paths
        project_root = Path.cwd()
        config_path = project_root / "configs" / "hyperopt_config.json"
        strategy_path = project_root / "user_data" / "strategies"
        data_path = project_root / "user_data" / "data"

        cmd = [
            "python3", "-m", "freqtrade", "hyperopt",
            "--config", str(config_path),
            "--strategy", self.strategy,
            "--strategy-path", str(strategy_path),
            "--hyperopt-loss", "SharpeHyperOptLoss",
            "--spaces", "buy", "sell",
            "--epochs", str(batch_size),
            "--timerange", "20240101-20240301",
            "--enable-protections",
            "--print-all",
            "--print-json",
            "--datadir", str(data_path),
            "--jobs", "1"  # Use single thread to avoid pickle issues
        ]

        print(f"🚀 Running hyperopt batch of {batch_size} epochs...")
        print(f"Command: {' '.join(cmd)}")

        try:
            # Change to freqtrade directory
            os.chdir("freqtrade")

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout per batch
            )

            # Change back to original directory
            os.chdir("..")

            if process.returncode != 0:
                print(f"❌ Hyperopt batch failed with return code {process.returncode}")
                print(f"STDERR: {process.stderr}")
                return False

            print(f"✅ Hyperopt batch completed successfully")
            return True

        except subprocess.TimeoutExpired:
            print("⏰ Hyperopt batch timed out")
            os.chdir("..")
            return False
        except Exception as e:
            print(f"❌ Error running hyperopt batch: {e}")
            os.chdir("..")
            return False

    def run(self):
        """Main hyperopt runner with early stopping"""
        print("🎯 Starting Hyperopt for NFI5MOHO_WIP Strategy")
        print(f"📊 Max epochs: {self.max_epochs}")
        print(f"⏹️ Early stopping patience: {self.early_stop_patience}")
        print(f"📁 Config file: {self.config_file}")
        print(f"🗄️ Database: {self.db_file}")
        print("=" * 60)

        self.setup_directories()

        batch_size = 10  # Run in batches of 10 epochs for testing
        total_epochs_run = 0

        while total_epochs_run < self.max_epochs:
            remaining_epochs = min(batch_size, self.max_epochs - total_epochs_run)

            print(f"\n📈 Epoch {total_epochs_run + 1}-{total_epochs_run + remaining_epochs} of {self.max_epochs}")

            # Run hyperopt batch
            if not self.run_hyperopt_batch(remaining_epochs):
                print("❌ Hyperopt batch failed, stopping...")
                break

            total_epochs_run += remaining_epochs

            # Check for early stopping
            if self.check_early_stopping():
                break

            # Small delay between batches
            time.sleep(2)

        # Final results
        final_result = self.get_best_result_from_db()
        if final_result:
            print("\n" + "=" * 60)
            print("🏆 HYPEROPT COMPLETED")
            print(f"📊 Total epochs run: {final_result['total_epochs']}")
            print(f"🎯 Best profit: {final_result['best_profit']:.6f}")
            print(f"🗄️ Results saved in: {self.db_file}")
            print("=" * 60)
        else:
            print("\n❌ No results found in database")

def main():
    """Main function"""
    runner = HyperoptRunner()
    runner.run()

if __name__ == "__main__":
    main()