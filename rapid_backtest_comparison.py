#!/usr/bin/env python3
"""
Rapid Backtest Comparison
Γρήγορη σύγκριση backtests με διαφορετικές περιόδους
"""

import subprocess
import json
import os
import re
from datetime import datetime

class RapidBacktestComparison:
    def __init__(self):
        self.results = []

    def extract_key_metrics(self, output):
        """Εξάγει βασικές μετρικές από το output"""
        metrics = {}

        # Εξαγωγή βασικών στατιστικών
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

        return metrics

    def run_backtest_period(self, timerange, description):
        """Τρέχει backtest για συγκεκριμένη περίοδο"""
        print(f"\n🚀 {description}")
        print(f"   Περίοδος: {timerange}")

        cmd = [
            "freqtrade", "backtesting",
            "--config", "user_data/config.json",
            "--strategy", "NFI5MOHO_WIP",
            "--timerange", timerange
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if result.returncode == 0:
                metrics = self.extract_key_metrics(result.stdout)
                metrics['timerange'] = timerange
                metrics['description'] = description

                print(f"   ✅ Επιτυχές!")
                print(f"   📊 Profit: {metrics.get('total_profit_pct', 0):.2f}%")
                print(f"   📈 Trades: {metrics.get('total_trades', 0)}")
                print(f"   🎯 Win Rate: {metrics.get('win_rate', 0):.1f}%")
                print(f"   ⚡ Sharpe: {metrics.get('sharpe', 0):.2f}")

                self.results.append(metrics)
                return metrics
            else:
                print(f"   ❌ Αποτυχία")
                return None

        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout")
            return None
        except Exception as e:
            print(f"   💥 Σφάλμα: {str(e)}")
            return None

    def generate_comparison_report(self):
        """Δημιουργεί συγκριτικό report"""
        if not self.results:
            print("❌ Δεν υπάρχουν αποτελέσματα")
            return

        print("\n" + "="*80)
        print("📊 ΣΥΓΚΡΙΤΙΚΑ ΑΠΟΤΕΛΕΣΜΑΤΑ BACKTESTING")
        print("="*80)

        # Ταξινόμηση κατά profit
        sorted_results = sorted(self.results, key=lambda x: x.get('total_profit_pct', 0), reverse=True)

        print(f"\n🏆 ΚΑΛΥΤΕΡΑ ΑΠΟΤΕΛΕΣΜΑΤΑ:")
        print("-" * 80)
        for i, result in enumerate(sorted_results[:5], 1):
            print(f"{i}. {result['description']}")
            print(f"   💰 Profit: {result.get('total_profit_pct', 0):.2f}%")
            print(f"   📊 Trades: {result.get('total_trades', 0)} (Win: {result.get('win_rate', 0):.1f}%)")
            print(f"   ⚡ Sharpe: {result.get('sharpe', 0):.2f}")
            print(f"   🏅 Best Pair: {result.get('best_pair', 'N/A')} ({result.get('best_pair_profit', 0):.2f}%)")
            print()

        # Στατιστικά
        profits = [r.get('total_profit_pct', 0) for r in self.results]
        trades = [r.get('total_trades', 0) for r in self.results]
        win_rates = [r.get('win_rate', 0) for r in self.results]

        print(f"📈 ΣΥΝΟΛΙΚΑ ΣΤΑΤΙΣΤΙΚΑ:")
        print("-" * 40)
        print(f"Μέσος Profit: {sum(profits)/len(profits):.2f}%")
        print(f"Καλύτερο: {max(profits):.2f}%")
        print(f"Χειρότερο: {min(profits):.2f}%")
        print(f"Μέσος αριθμός trades: {sum(trades)/len(trades):.0f}")
        print(f"Μέσο Win Rate: {sum(win_rates)/len(win_rates):.1f}%")

        # Θετικά vs αρνητικά
        positive = len([p for p in profits if p > 0])
        negative = len([p for p in profits if p <= 0])
        print(f"\n✅ Θετικά αποτελέσματα: {positive}/{len(profits)} ({positive/len(profits)*100:.1f}%)")
        print(f"❌ Αρνητικά/Μηδενικά: {negative}/{len(profits)} ({negative/len(profits)*100:.1f}%)")

def main():
    """Main function"""
    print("⚡ Rapid Backtest Comparison")
    print("=" * 30)

    comparator = RapidBacktestComparison()

    # Διαφορετικές περίοδοι για σύγκριση
    test_periods = [
        ("20241210-20241217", "Τελευταία εβδομάδα"),
        ("20241203-20241217", "Τελευταίες 2 εβδομάδες"),
        ("20241201-20241217", "Τελευταίες 2+ εβδομάδες"),
        ("20241120-20241217", "Τελευταίες 4 εβδομάδες"),
        ("20241115-20241217", "Τελευταίος μήνας"),
        ("20241101-20241217", "Τελευταίοι 1.5 μήνες"),
        ("20241015-20241217", "Τελευταίοι 2 μήνες"),
    ]

    for timerange, description in test_periods:
        comparator.run_backtest_period(timerange, description)

    # Δημιουργία συγκριτικού report
    comparator.generate_comparison_report()

    print(f"\n🎉 Σύγκριση ολοκληρώθηκε! Συνολικά tests: {len(comparator.results)}")

if __name__ == "__main__":
    main()