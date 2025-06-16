#!/usr/bin/env python3
"""
Script για δοκιμή βελτιωμένων ρυθμίσεων
"""

import json
import subprocess
import shutil
from pathlib import Path

def backup_current_config():
    """Δημιουργεί backup του τρέχοντος config"""
    config_path = Path("freqtrade/user_data/config_altcoins.json")
    backup_path = Path("freqtrade/user_data/config_altcoins_backup.json")

    shutil.copy2(config_path, backup_path)
    print(f"✅ Backup δημιουργήθηκε: {backup_path}")

def create_improved_configs():
    """Δημιουργεί βελτιωμένες ρυθμίσεις"""

    base_config_path = Path("freqtrade/user_data/config_altcoins.json")
    with open(base_config_path, 'r') as f:
        base_config = json.load(f)

    configs = {
        "high_budget": {
            "name": "Υψηλό Budget",
            "changes": {
                "dry_run_wallet": 2000,
                "stake_amount": 200,
                "max_open_trades": 10,
                "pair_whitelist": list(set(base_config["exchange"]["pair_whitelist"] + [
                    "BTC/USDC", "ETH/USDC"
                ]))
            },
            "expected": "+8-12% μηνιαίως"
        },

        "more_pairs": {
            "name": "Περισσότερα Pairs",
            "changes": {
                "dry_run_wallet": 1000,
                "stake_amount": 80,
                "max_open_trades": 15,
                "pair_whitelist": [
                    "BTC/USDC", "ETH/USDC", "BNB/USDC",
                    "ADA/USDC", "DOT/USDC", "SOL/USDC", "LINK/USDC",
                    "AVAX/USDC", "XRP/USDC", "UNI/USDC", "ATOM/USDC",
                    "ALGO/USDC", "NEAR/USDC", "MATIC/USDC", "LTC/USDC",
                    "DOGE/USDC", "SHIB/USDC", "TRX/USDC", "HBAR/USDC",
                    "VET/USDC", "FTM/USDC", "ONE/USDC", "AAVE/USDC"
                ]
            },
            "expected": "+6-10% μηνιαίως"
        },

        "aggressive": {
            "name": "Επιθετικό",
            "changes": {
                "dry_run_wallet": 3000,
                "stake_amount": 300,
                "max_open_trades": 12,
                "tradable_balance_ratio": 0.95,
                "pair_whitelist": [
                    "BTC/USDC", "ETH/USDC", "SOL/USDC", "AVAX/USDC",
                    "LINK/USDC", "DOT/USDC", "ADA/USDC", "MATIC/USDC",
                    "UNI/USDC", "ATOM/USDC"
                ]
            },
            "expected": "+10-15% μηνιαίως"
        },

        "conservative": {
            "name": "Συντηρητικό",
            "changes": {
                "dry_run_wallet": 1500,
                "stake_amount": 100,
                "max_open_trades": 6,
                "tradable_balance_ratio": 0.8,
                "pair_whitelist": [
                    "BTC/USDC", "ETH/USDC", "ADA/USDC", "DOT/USDC", "SOL/USDC"
                ]
            },
            "expected": "+3-6% μηνιαίως"
        }
    }

    return configs

def apply_config(config_name, config_data):
    """Εφαρμόζει μια ρύθμιση"""
    config_path = Path("freqtrade/user_data/config_altcoins.json")

    with open(config_path, 'r') as f:
        current_config = json.load(f)

    # Εφαρμογή αλλαγών
    for key, value in config_data["changes"].items():
        if key == "pair_whitelist":
            current_config["exchange"]["pair_whitelist"] = value
        else:
            current_config[key] = value

    # Αποθήκευση
    with open(config_path, 'w') as f:
        json.dump(current_config, f, indent=4)

    print(f"✅ Εφαρμόστηκε config: {config_data['name']}")

def run_backtest_for_config(config_name):
    """Εκτελεί backtest για μια ρύθμιση"""
    print(f"\n🚀 Εκτέλεση backtest για {config_name}...")

    cmd = [
        "python3", "-m", "freqtrade", "backtesting",
        "--config", "user_data/config_altcoins.json",
        "--strategy", "NFI5MOHO_WIP",
        "--timerange", "20250301-20250601",  # 3 μήνες
        "--export", "trades",
        "--export-filename", f"user_data/backtest_results/config_test_{config_name}.json",
        "--cache", "none"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd="freqtrade")

        if result.returncode == 0:
            # Εξαγωγή λεπτομερών αποτελεσμάτων
            output_lines = result.stdout.split('\n')

            profit_pct = "N/A"
            profit_abs = "N/A"
            trades_count = "N/A"
            starting_balance = "N/A"
            final_balance = "N/A"

            for line in output_lines:
                if 'Total profit %' in line and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        profit_pct = parts[2].strip()
                if 'Total profit abs' in line and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        profit_abs = parts[2].strip()
                if 'Total trades' in line and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        trades_count = parts[2].strip()
                if 'Starting balance' in line and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        starting_balance = parts[2].strip()
                if 'Final balance' in line and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        final_balance = parts[2].strip()

            return {
                "success": True,
                "profit_pct": profit_pct,
                "profit_abs": profit_abs,
                "trades": trades_count,
                "starting_balance": starting_balance,
                "final_balance": final_balance,
                "output": result.stdout
            }
        else:
            return {
                "success": False,
                "error": result.stderr
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Timeout"
        }

def restore_config():
    """Επαναφέρει το αρχικό config"""
    config_path = Path("freqtrade/user_data/config_altcoins.json")
    backup_path = Path("freqtrade/user_data/config_altcoins_backup.json")

    if backup_path.exists():
        shutil.copy2(backup_path, config_path)
        print("✅ Αρχικό config επαναφέρθηκε")

def main():
    print("🧪 Δοκιμή Βελτιωμένων Ρυθμίσεων")
    print("=" * 50)

    # Backup τρέχοντος config
    backup_current_config()

    # Δημιουργία configs
    configs = create_improved_configs()

    print("\nΔιαθέσιμες ρυθμίσεις:")
    for i, (key, config) in enumerate(configs.items(), 1):
        print(f"{i}. {config['name']} - Αναμενόμενο: {config['expected']}")

    choice = input("\nΕπιλέξτε ρύθμιση (1-4) ή 'all' για όλες: ").strip()

    results = {}

    if choice.lower() == 'all':
        # Δοκιμή όλων των ρυθμίσεων
        for config_key, config_data in configs.items():
            print(f"\n{'='*60}")
            print(f"🧪 ΔΟΚΙΜΗ: {config_data['name']}")
            print(f"{'='*60}")

            # Εφαρμογή config
            apply_config(config_key, config_data)

            # Εκτέλεση backtest
            result = run_backtest_for_config(config_key)
            results[config_key] = result

            if result["success"]:
                print(f"✅ Αποτελέσματα:")
                print(f"   💰 Budget: {result['starting_balance']} → {result['final_balance']}")
                print(f"   📈 Κέρδος: {result['profit_abs']} ({result['profit_pct']})")
                print(f"   📊 Trades: {result['trades']}")
                print(f"   ⏱️ Περίοδος: 1 Μάρτιος - 1 Ιούνιος 2025 (3 μήνες)")
            else:
                print(f"❌ Σφάλμα: {result['error']}")

    else:
        # Δοκιμή μιας ρύθμισης
        try:
            choice_idx = int(choice) - 1
            config_keys = list(configs.keys())

            if 0 <= choice_idx < len(config_keys):
                config_key = config_keys[choice_idx]
                config_data = configs[config_key]

                print(f"\n🧪 Δοκιμή: {config_data['name']}")

                # Εφαρμογή config
                apply_config(config_key, config_data)

                # Εκτέλεση backtest
                result = run_backtest_for_config(config_key)
                results[config_key] = result

                if result["success"]:
                    print(f"✅ Αποτελέσματα:")
                    print(f"   💰 Budget: {result['starting_balance']} → {result['final_balance']}")
                    print(f"   📈 Κέρδος: {result['profit_abs']} ({result['profit_pct']})")
                    print(f"   📊 Trades: {result['trades']}")
                    print(f"   ⏱️ Περίοδος: 1 Μάρτιος - 1 Ιούνιος 2025 (3 μήνες)")
                else:
                    print(f"❌ Σφάλμα: {result['error']}")
            else:
                print("❌ Μη έγκυρη επιλογή")

        except ValueError:
            print("❌ Μη έγκυρη επιλογή")

    # Εμφάνιση συνολικών αποτελεσμάτων
    if results:
        print(f"\n{'='*60}")
        print("📊 ΣΥΝΟΛΙΚΑ ΑΠΟΤΕΛΕΣΜΑΤΑ")
        print(f"{'='*60}")

        for config_key, result in results.items():
            config_name = configs[config_key]["name"]
            expected = configs[config_key]["expected"]

            if result["success"]:
                print(f"✅ {config_name}:")
                print(f"   💰 Budget: {result['starting_balance']} → {result['final_balance']}")
                print(f"   📈 Κέρδος: {result['profit_abs']} ({result['profit_pct']})")
                print(f"   📊 Trades: {result['trades']} σε 3 μήνες")
                print(f"   🎯 Αναμενόμενο: {expected}")
            else:
                print(f"❌ {config_name}: Απέτυχε")
            print()

    # Επαναφορά αρχικού config
    restore_config()

    print("🎯 Δοκιμή ολοκληρώθηκε!")

if __name__ == "__main__":
    main()