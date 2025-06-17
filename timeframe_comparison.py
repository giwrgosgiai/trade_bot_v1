#!/usr/bin/env python3
"""
Timeframe Comparison Script
Σύγκριση διαφορετικών timeframes για backtesting
"""

import subprocess
import json
import os
import re
from datetime import datetime

class TimeframeComparison:
    def __init__(self):
        self.results = []

    def extract_key_metrics(self, output):
        """Εξάγει βασικές μετρικές από το output"""
        metrics = {}

        lines = output.split('\n')
        for line in lines:
            if 'Total profit %' in line:
                match = re.search(r'(\d+\.?\d*)%', line)
                if match:
                    metrics['total_profit_pct'] = float(match.group(1))
            elif 'Total/Daily Avg Trades' in line:
                match = re.search(r'(\d+) /', line)
                if match:
                    metrics['total_trades'] = int(match.group(1))
            elif 'Win%' in line and 'Win  Draw  Loss' in line:
                match = re.search(r'(\d+\.?\d*)$', line.strip())
                if match:
                    metrics['win_rate'] = float(match.group(1))
            elif 'Sharpe' in line:
                match = re.search(r'(\d+\.?\d*)$', line.strip())
                if match:
                    metrics['sharpe'] = float(match.group(1))
            elif 'Max % of account underwater' in line:
                match = re.search(r'(\d+\.?\d*)%', line)
                if match:
                    metrics['max_drawdown'] = float(match.group(1))
            elif 'Best Pair' in line:
                match = re.search(r'(\w+/\w+) ([\d\.-]+)%', line)
                if match:
                    metrics['best_pair'] = match.group(1)
                    metrics['best_pair_profit'] = float(match.group(2))
            elif 'Avg. Duration Winners' in line:
                match = re.search(r'(\d+:\d+:\d+)', line)
                if match:
                    metrics['avg_duration'] = match.group(1)

        return metrics

    def create_temp_config(self, timeframe):
        """Δημιουργεί προσωρινό config με συγκεκριμένο timeframe"""
        with open("user_data/config.json", 'r') as f:
            config = json.load(f)

        config["timeframe"] = timeframe

        temp_config_path = f"temp_config_{timeframe}.json"
        with open(temp_config_path, 'w') as f:
            json.dump(config, f, indent=4)

        return temp_config_path

    def run_backtest_timeframe(self, timeframe, timerange, description):
        """Τρέχει backtest για συγκεκριμένο timeframe"""
        print(f"\n🚀 {description}")
        print(f"   Timeframe: {timeframe}")
        print(f"   Περίοδος: {timerange}")

        # Δημιουργία προσωρινού config
        temp_config = self.create_temp_config(timeframe)

        cmd = [
            "freqtrade", "backtesting",
            "--config", temp_config,
            "--strategy", "NFI5MOHO_WIP",
            "--timerange", timerange
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=240)

            # Καθαρισμός προσωρινού config
            if os.path.exists(temp_config):
                os.remove(temp_config)

            if result.returncode == 0:
                metrics = self.extract_key_metrics(result.stdout)
                metrics['timeframe'] = timeframe
                metrics['timerange'] = timerange
                metrics['description'] = description

                print(f"   ✅ Επιτυχές!")
                print(f"   📊 Profit: {metrics.get('total_profit_pct', 0):.2f}%")
                print(f"   📈 Trades: {metrics.get('total_trades', 0)}")
                print(f"   🎯 Win Rate: {metrics.get('win_rate', 0):.1f}%")
                print(f"   ⚡ Sharpe: {metrics.get('sharpe', 0):.2f}")
                print(f"   ⏱️ Avg Duration: {metrics.get('avg_duration', 'N/A')}")

                self.results.append(metrics)
                return metrics
            else:
                print(f"   ❌ Αποτυχία: {result.stderr[:200]}...")
                return None

        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout")
            if os.path.exists(temp_config):
                os.remove(temp_config)
            return None
        except Exception as e:
            print(f"   💥 Σφάλμα: {str(e)}")
            if os.path.exists(temp_config):
                os.remove(temp_config)
            return None

    def generate_timeframe_report(self):
        """Δημιουργεί συγκριτικό report για timeframes"""
        if not self.results:
            print("❌ Δεν υπάρχουν αποτελέσματα")
            return

        print("\n" + "="*80)
        print("⏰ ΣΥΓΚΡΙΣΗ TIMEFRAMES")
        print("="*80)

        # Ομαδοποίηση ανά timeframe
        by_timeframe = {}
        for result in self.results:
            tf = result['timeframe']
            if tf not in by_timeframe:
                by_timeframe[tf] = []
            by_timeframe[tf].append(result)

        # Ανάλυση ανά timeframe
        print(f"\n📊 ΑΝΑΛΥΣΗ ΑΝΑ TIMEFRAME:")
        print("-" * 80)

        timeframe_summary = []
        for tf, results in by_timeframe.items():
            profits = [r.get('total_profit_pct', 0) for r in results]
            trades = [r.get('total_trades', 0) for r in results]
            win_rates = [r.get('win_rate', 0) for r in results]

            avg_profit = sum(profits) / len(profits)
            avg_trades = sum(trades) / len(trades)
            avg_win_rate = sum(win_rates) / len(win_rates)
            max_profit = max(profits)

            timeframe_summary.append({
                'timeframe': tf,
                'avg_profit': avg_profit,
                'max_profit': max_profit,
                'avg_trades': avg_trades,
                'avg_win_rate': avg_win_rate,
                'test_count': len(results)
            })

            print(f"🕐 {tf}:")
            print(f"   Μέσος Profit: {avg_profit:.2f}%")
            print(f"   Μέγιστος Profit: {max_profit:.2f}%")
            print(f"   Μέσος αριθμός trades: {avg_trades:.0f}")
            print(f"   Μέσο Win Rate: {avg_win_rate:.1f}%")
            print(f"   Αριθμός tests: {len(results)}")
            print()

        # Ταξινόμηση κατά μέσο profit
        timeframe_summary.sort(key=lambda x: x['avg_profit'], reverse=True)

        print(f"🏆 ΚΑΛΥΤΕΡΟΙ TIMEFRAMES (κατά μέσο profit):")
        print("-" * 50)
        for i, tf_data in enumerate(timeframe_summary, 1):
            print(f"{i}. {tf_data['timeframe']}: {tf_data['avg_profit']:.2f}% "
                  f"(max: {tf_data['max_profit']:.2f}%)")

        # Καλύτερα αποτελέσματα συνολικά
        sorted_results = sorted(self.results, key=lambda x: x.get('total_profit_pct', 0), reverse=True)

        print(f"\n🥇 TOP 5 ΚΑΛΥΤΕΡΑ ΑΠΟΤΕΛΕΣΜΑΤΑ:")
        print("-" * 80)
        for i, result in enumerate(sorted_results[:5], 1):
            print(f"{i}. {result['description']} ({result['timeframe']})")
            print(f"   💰 Profit: {result.get('total_profit_pct', 0):.2f}%")
            print(f"   📊 Trades: {result.get('total_trades', 0)} (Win: {result.get('win_rate', 0):.1f}%)")
            print(f"   🏅 Best Pair: {result.get('best_pair', 'N/A')} ({result.get('best_pair_profit', 0):.2f}%)")
            print()

def main():
    """Main function"""
    print("⏰ Timeframe Comparison")
    print("=" * 25)

    comparator = TimeframeComparison()

    # Διαφορετικά timeframes για σύγκριση
    timeframes = ["5m", "15m", "1h"]

    # Δύο περίοδοι για testing
    test_periods = [
        ("20241115-20241217", "Τελευταίος μήνας"),
        ("20241201-20241217", "Τελευταίες 2+ εβδομάδες")
    ]

    for timeframe in timeframes:
        for timerange, period_desc in test_periods:
            description = f"{period_desc} - {timeframe}"
            comparator.run_backtest_timeframe(timeframe, timerange, description)

    # Δημιουργία συγκριτικού report
    comparator.generate_timeframe_report()

    print(f"\n🎉 Σύγκριση timeframes ολοκληρώθηκε! Συνολικά tests: {len(comparator.results)}")

if __name__ == "__main__":
    main()