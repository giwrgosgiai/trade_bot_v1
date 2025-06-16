#!/usr/bin/env python3
"""
Comprehensive Hyperopt Script για NFI5MOHO_WIP
Βελτιστοποίηση στρατηγικής με dynamic stakes και φίλτρα pairlists
"""

import os
import sys
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path

class NFIHyperoptOptimizer:
    def __init__(self, freqtrade_path="freqtrade"):
        self.freqtrade_path = Path(freqtrade_path)
        self.config_path = Path.cwd() / self.freqtrade_path / "user_data" / "config_altcoins.json"
        self.strategy = "NFI5MOHO_WIP"

    def create_optimized_config(self):
        """Δημιουργεί βελτιστοποιημένο config με dynamic stakes και φίλτρα"""
        config = {
            "max_open_trades": 12,  # Αυξημένο από 8
            "stake_currency": "USDC",
            "stake_amount": "unlimited",  # Dynamic staking
            "tradable_balance_ratio": 0.99,
            "fiat_display_currency": "USD",
            "timeframe": "5m",  # Επιβεβαίωση 5m timeframe
            "dry_run": True,
            "dry_run_wallet": 3000,  # Αυξημένο budget για καλύτερα αποτελέσματα
            "cancel_open_orders_on_exit": False,

            # Dynamic Position Sizing
            "position_adjustment_enable": True,
            "max_entry_position_adjustment": 3,

            # Βελτιστοποιημένα order types
            "order_types": {
                "entry": "limit",
                "exit": "limit",
                "stoploss": "market",
                "stoploss_on_exchange": False,
                "stoploss_on_exchange_interval": 60
            },

            # Entry/Exit pricing
            "entry_pricing": {
                "price_side": "same",
                "use_order_book": True,
                "order_book_top": 1,
                "price_last_balance": 0.0,
                "check_depth_of_market": {
                    "enabled": False,
                    "bids_to_ask_delta": 1
                }
            },

            "exit_pricing": {
                "price_side": "same",
                "use_order_book": True,
                "order_book_top": 1
            },

            # Exchange configuration
            "exchange": {
                "name": "binance",
                "key": "",
                "secret": "",
                "ccxt_config": {},
                "ccxt_async_config": {},
                "pair_whitelist": [
                    "BTC/USDC", "ETH/USDC", "SOL/USDC", "ADA/USDC", "DOT/USDC",
                    "AVAX/USDC", "LINK/USDC", "UNI/USDC", "ATOM/USDC", "ALGO/USDC",
                    "XTZ/USDC", "NEAR/USDC", "CRV/USDC", "AAVE/USDC", "MKR/USDC",
                    "DOGE/USDC", "SHIB/USDC", "TRX/USDC", "HBAR/USDC", "VET/USDC",
                    "SAND/USDC", "LTC/USDC", "BCH/USDC", "XRP/USDC", "XLM/USDC"
                ],
                "pair_blacklist": [
                    "BNB/.*", ".*UP/.*", ".*DOWN/.*", ".*BULL/.*", ".*BEAR/.*",
                    ".*HEDGE/.*", ".*HALF/.*", ".*3[LS]/.*", ".*[23][LS]/.*"
                ]
            },

            # Advanced Pairlist με φίλτρα
            "pairlists": [
                {
                    "method": "StaticPairList"
                }
            ],

            # Risk Management - Protections
            "protections": [
                {
                    "method": "StoplossGuard",
                    "lookback_period_candles": 24,
                    "trade_limit": 4,
                    "stop_duration_candles": 2,
                    "only_per_pair": False
                },
                {
                    "method": "MaxDrawdown",
                    "lookback_period_candles": 48,
                    "trade_limit": 20,
                    "stop_duration_candles": 4,
                    "max_allowed_drawdown": 0.2
                },
                {
                    "method": "LowProfitPairs",
                    "lookback_period_candles": 360,
                    "trade_limit": 2,
                    "stop_duration_candles": 60,
                    "required_profit": 0.02
                },
                {
                    "method": "CooldownPeriod",
                    "stop_duration_candles": 5
                }
            ],

            # Telegram notifications (optional)
            "telegram": {
                "enabled": False,
                "token": "",
                "chat_id": ""
            },

            # API Server
            "api_server": {
                "enabled": False,
                "listen_ip_address": "127.0.0.1",
                "listen_port": 8080,
                "verbosity": "error",
                "enable_openapi": False,
                "jwt_secret_key": "somethingrandom",
                "CORS_origins": [],
                "username": "",
                "password": ""
            },

            # Bot behavior
            "initial_state": "running",
            "force_entry_enable": False,
            "internals": {
                "process_throttle_secs": 5
            }
        }

        return config

    def save_config(self, config):
        """Αποθηκεύει το βελτιστοποιημένο config"""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"✅ Βελτιστοποιημένο config αποθηκεύτηκε: {self.config_path}")

    def run_hyperopt(self, timerange="20250301-20250601", epochs=500, spaces="buy sell roi stoploss"):
        """Εκτελεί hyperopt με βελτιστοποιημένες παραμέτρους"""
        print(f"🚀 Εκκίνηση Hyperopt για {self.strategy}")
        print(f"📅 Timerange: {timerange}")
        print(f"🔄 Epochs: {epochs}")
        print(f"🎯 Spaces: {spaces}")

        # Αλλαγή στο freqtrade directory
        original_dir = os.getcwd()
        os.chdir(Path.cwd() / self.freqtrade_path)

        try:
            # Hyperopt command με βελτιστοποιημένες παραμέτρους
            cmd = [
                "python3", "-m", "freqtrade", "hyperopt",
                "--config", "user_data/config_altcoins.json",
                "--strategy", self.strategy,
                "--timerange", timerange,
                "--timeframe", "5m",  # Επιβεβαίωση 5m
                "--epochs", str(epochs),
                "--spaces", *spaces.split(),
                "--hyperopt-loss", "SharpeHyperOptLossDaily",  # Καλύτερη loss function
                "--min-trades", "30",  # Ελάχιστες συναλλαγές για έγκυρα αποτελέσματα
                "--random-state", "42",  # Reproducible results
                "--print-all",  # Εμφάνιση όλων των αποτελεσμάτων
                "--disable-param-export"  # Αποφυγή auto-export για manual control
            ]

            print(f"🔧 Εκτέλεση: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)  # 2 ώρες timeout

            if result.returncode == 0:
                print("✅ Hyperopt ολοκληρώθηκε επιτυχώς!")
                print("\n📊 ΑΠΟΤΕΛΕΣΜΑΤΑ:")
                print(result.stdout)

                # Αποθήκευση αποτελεσμάτων
                results_file = Path("user_data/hyperopt_results") / f"{self.strategy}_hyperopt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                results_file.parent.mkdir(exist_ok=True)

                with open(results_file, 'w') as f:
                    f.write(f"Hyperopt Results for {self.strategy}\n")
                    f.write(f"Timerange: {timerange}\n")
                    f.write(f"Epochs: {epochs}\n")
                    f.write(f"Spaces: {spaces}\n")
                    f.write(f"Generated: {datetime.now()}\n\n")
                    f.write(result.stdout)

                print(f"📁 Αποτελέσματα αποθηκεύτηκαν: {results_file}")

            else:
                print("❌ Hyperopt απέτυχε!")
                print("STDERR:", result.stderr)
                print("STDOUT:", result.stdout)

        except subprocess.TimeoutExpired:
            print("⏰ Hyperopt timeout (2 ώρες)")
        except Exception as e:
            print(f"💥 Exception: {e}")
        finally:
            os.chdir(original_dir)

    def run_quick_optimization(self):
        """Γρήγορη βελτιστοποίηση για δοκιμή"""
        print("⚡ Γρήγορη βελτιστοποίηση (100 epochs)")
        self.run_hyperopt(
            timerange="20250401-20250601",  # 2 μήνες
            epochs=100,
            spaces="buy sell roi"  # Βασικά spaces
        )

    def run_full_optimization(self):
        """Πλήρης βελτιστοποίηση για production"""
        print("🎯 Πλήρης βελτιστοποίηση (1000 epochs)")
        self.run_hyperopt(
            timerange="20250101-20250601",  # 5 μήνες
            epochs=1000,
            spaces="roi stoploss trailing"  # Μόνο τα spaces που υποστηρίζει το X6
        )

    def run_conservative_optimization(self):
        """Συντηρητική βελτιστοποίηση με έμφαση στη σταθερότητα"""
        print("🛡️ Συντηρητική βελτιστοποίηση")
        self.run_hyperopt(
            timerange="20250201-20250601",  # 4 μήνες
            epochs=500,
            spaces="roi stoploss protection"  # Focus σε risk management
        )

def main():
    print("🤖 NFI Hyperopt Optimizer")
    print("=" * 50)

    optimizer = NFIHyperoptOptimizer()

    # Δημιουργία βελτιστοποιημένου config
    print("📝 Δημιουργία βελτιστοποιημένου config...")
    config = optimizer.create_optimized_config()
    optimizer.save_config(config)

    # Αυτόματη επιλογή 2: Πλήρης βελτιστοποίηση
    print("🎯 Εκτέλεση πλήρους βελτιστοποίησης (1000 epochs, 5 μήνες)")
    optimizer.run_full_optimization()

    print("\n🎯 Συμβουλές για βελτίωση:")
    print("• Χρησιμοποιήστε τα αποτελέσματα για να ενημερώσετε τη στρατηγική")
    print("• Δοκιμάστε διαφορετικές loss functions (SharpeHyperOptLoss, CalmarHyperOptLoss)")
    print("• Αυξήστε το dry_run_wallet για περισσότερες ευκαιρίες")
    print("• Προσθέστε περισσότερα pairs στο whitelist")
    print("• Χρησιμοποιήστε forward testing για επιβεβαίωση")

if __name__ == "__main__":
    main()