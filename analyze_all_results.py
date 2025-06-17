#!/usr/bin/env python3
"""
Analyze All Backtest Results
Ανάλυση όλων των αποτελεσμάτων backtesting
"""

import json
import os
import glob
from datetime import datetime
import pandas as pd

class BacktestAnalyzer:
    def __init__(self):
        self.results = []

    def load_all_results(self):
        """Φορτώνει όλα τα αποτελέσματα από τον φάκελο backtest_results"""
        print("📂 Φόρτωση αποτελεσμάτων...")

        # Βρίσκει όλα τα αρχεία αποτελεσμάτων (όχι .meta)
        result_files = glob.glob("backtest_results/5m_*")
        result_files = [f for f in result_files if not f.endswith('.meta')]

        # Set για να αποφύγουμε διπλότυπα
        seen_files = set()

        for file_path in result_files:
            try:
                # Εξαγωγή πληροφοριών από το όνομα αρχείου
                filename = os.path.basename(file_path)

                # Δημιουργία unique key για να αποφύγουμε διπλότυπα
                unique_key = filename.split('-2025-')[0] if '-2025-' in filename else filename
                if unique_key in seen_files:
                    continue
                seen_files.add(unique_key)

                with open(file_path, 'r') as f:
                    data = json.load(f)

                if filename.startswith('5m_'):
                    parts = filename.replace('5m_', '').split('_')
                    if len(parts) >= 3:
                        timerange = parts[0]
                        pair_group = parts[1]
                        stake_amount = parts[2].replace('USDC', '').split('-')[0]  # Αφαιρεί timestamp

                        # Εξαγωγή στατιστικών από τα δεδομένα
                        strategy_stats = data.get('strategy', {}).get('NFI5MOHO_WIP', {})

                        # Εξαγωγή profit_total_pct - μπορεί να είναι είτε απευθείας στο strategy_stats είτε στα results_per_pair
                        total_profit_pct = strategy_stats.get('profit_total_pct', 0)

                        # Αν δεν υπάρχει στο κύριο επίπεδο, ψάχνω στα results_per_pair για το TOTAL
                        if total_profit_pct == 0:
                            results_per_pair = strategy_stats.get('results_per_pair', [])
                            for pair_result in results_per_pair:
                                if pair_result.get('key') == 'TOTAL':
                                    total_profit_pct = pair_result.get('profit_total_pct', 0)
                                    break

                        result = {
                            'filename': filename,
                            'timeframe': '5m',
                            'timerange': timerange,
                            'pair_group': pair_group,
                            'stake_amount': int(stake_amount) if stake_amount.isdigit() else 100,
                            'total_trades': strategy_stats.get('total_trades', 0),
                            'total_profit_pct': total_profit_pct,
                            'total_profit_abs': strategy_stats.get('profit_total_abs', 0),
                            'wins': strategy_stats.get('wins', 0),
                            'losses': strategy_stats.get('losses', 0),
                            'draws': strategy_stats.get('draws', 0),
                            'win_rate': strategy_stats.get('winrate', 0) * 100 if strategy_stats.get('winrate') else 0,
                            'profit_mean_pct': strategy_stats.get('profit_mean', 0) * 100 if strategy_stats.get('profit_mean') else 0,
                            'loss_mean_pct': 0,  # Θα υπολογιστεί αργότερα αν χρειαστεί
                            'max_drawdown_pct': strategy_stats.get('max_drawdown', 0) * 100 if strategy_stats.get('max_drawdown') else 0,
                        }

                        self.results.append(result)

            except Exception as e:
                print(f"⚠️ Σφάλμα στη φόρτωση {file_path}: {str(e)}")

        print(f"✅ Φορτώθηκαν {len(self.results)} αποτελέσματα")

    def analyze_by_timerange(self):
        """Ανάλυση ανά timerange"""
        print("\n📅 ΑΝΑΛΥΣΗ ΑΝΑ ΠΕΡΙΟΔΟ:")
        print("-" * 50)

        by_timerange = {}
        for result in self.results:
            tr = result['timerange']
            if tr not in by_timerange:
                by_timerange[tr] = []
            by_timerange[tr].append(result)

        timerange_summary = []
        for tr, results in by_timerange.items():
            profits = [r['total_profit_pct'] for r in results]
            trades = [r['total_trades'] for r in results]

            summary = {
                'timerange': tr,
                'avg_profit': sum(profits) / len(profits),
                'max_profit': max(profits),
                'min_profit': min(profits),
                'avg_trades': sum(trades) / len(trades),
                'test_count': len(results)
            }
            timerange_summary.append(summary)

        # Ταξινόμηση κατά μέσο profit
        timerange_summary.sort(key=lambda x: x['avg_profit'], reverse=True)

        for i, summary in enumerate(timerange_summary, 1):
            print(f"{i}. {summary['timerange']}:")
            print(f"   Μέσος Profit: {summary['avg_profit']:.2f}%")
            print(f"   Εύρος: {summary['min_profit']:.2f}% - {summary['max_profit']:.2f}%")
            print(f"   Μέσος αριθμός trades: {summary['avg_trades']:.0f}")
            print(f"   Αριθμός tests: {summary['test_count']}")
            print()

    def analyze_by_pair_group(self):
        """Ανάλυση ανά ομάδα pairs"""
        print("\n💰 ΑΝΑΛΥΣΗ ΑΝΑ ΟΜΑΔΑ PAIRS:")
        print("-" * 50)

        by_pair_group = {}
        for result in self.results:
            pg = result['pair_group']
            if pg not in by_pair_group:
                by_pair_group[pg] = []
            by_pair_group[pg].append(result)

        pair_summary = []
        for pg, results in by_pair_group.items():
            profits = [r['total_profit_pct'] for r in results]
            trades = [r['total_trades'] for r in results]
            win_rates = [r['win_rate'] for r in results]

            summary = {
                'pair_group': pg,
                'avg_profit': sum(profits) / len(profits),
                'max_profit': max(profits),
                'min_profit': min(profits),
                'avg_trades': sum(trades) / len(trades),
                'avg_win_rate': sum(win_rates) / len(win_rates),
                'test_count': len(results)
            }
            pair_summary.append(summary)

        # Ταξινόμηση κατά μέσο profit
        pair_summary.sort(key=lambda x: x['avg_profit'], reverse=True)

        for i, summary in enumerate(pair_summary, 1):
            print(f"{i}. {summary['pair_group'].upper()}:")
            print(f"   Μέσος Profit: {summary['avg_profit']:.2f}%")
            print(f"   Εύρος: {summary['min_profit']:.2f}% - {summary['max_profit']:.2f}%")
            print(f"   Μέσος αριθμός trades: {summary['avg_trades']:.0f}")
            print(f"   Μέσο Win Rate: {summary['avg_win_rate']:.1f}%")
            print(f"   Αριθμός tests: {summary['test_count']}")
            print()

    def analyze_by_stake_amount(self):
        """Ανάλυση ανά stake amount"""
        print("\n💵 ΑΝΑΛΥΣΗ ΑΝΑ STAKE AMOUNT:")
        print("-" * 50)

        by_stake = {}
        for result in self.results:
            stake = result['stake_amount']
            if stake not in by_stake:
                by_stake[stake] = []
            by_stake[stake].append(result)

        stake_summary = []
        for stake, results in by_stake.items():
            profits = [r['total_profit_pct'] for r in results]

            summary = {
                'stake_amount': stake,
                'avg_profit': sum(profits) / len(profits),
                'max_profit': max(profits),
                'min_profit': min(profits),
                'test_count': len(results)
            }
            stake_summary.append(summary)

        # Ταξινόμηση κατά stake amount
        stake_summary.sort(key=lambda x: x['stake_amount'])

        for summary in stake_summary:
            print(f"{summary['stake_amount']} USDC:")
            print(f"   Μέσος Profit: {summary['avg_profit']:.2f}%")
            print(f"   Εύρος: {summary['min_profit']:.2f}% - {summary['max_profit']:.2f}%")
            print(f"   Αριθμός tests: {summary['test_count']}")
            print()

    def show_top_results(self, n=10):
        """Δείχνει τα καλύτερα αποτελέσματα"""
        print(f"\n🏆 TOP {n} ΚΑΛΥΤΕΡΑ ΑΠΟΤΕΛΕΣΜΑΤΑ:")
        print("-" * 70)

        sorted_results = sorted(self.results, key=lambda x: x['total_profit_pct'], reverse=True)

        for i, result in enumerate(sorted_results[:n], 1):
            print(f"{i}. {result['timerange']} - {result['pair_group'].upper()} - {result['stake_amount']}USDC")
            print(f"   💰 Profit: {result['total_profit_pct']:.2f}%")
            print(f"   📊 Trades: {result['total_trades']} (Win Rate: {result['win_rate']:.1f}%)")
            print(f"   📈 Avg Profit per Trade: {result['profit_mean_pct']:.2f}%")
            print(f"   📉 Max Drawdown: {result['max_drawdown_pct']:.2f}%")
            print()

    def show_worst_results(self, n=5):
        """Δείχνει τα χειρότερα αποτελέσματα"""
        print(f"\n🔻 TOP {n} ΧΕΙΡΟΤΕΡΑ ΑΠΟΤΕΛΕΣΜΑΤΑ:")
        print("-" * 70)

        sorted_results = sorted(self.results, key=lambda x: x['total_profit_pct'])

        for i, result in enumerate(sorted_results[:n], 1):
            print(f"{i}. {result['timerange']} - {result['pair_group'].upper()} - {result['stake_amount']}USDC")
            print(f"   💰 Profit: {result['total_profit_pct']:.2f}%")
            print(f"   📊 Trades: {result['total_trades']} (Win Rate: {result['win_rate']:.1f}%)")
            print(f"   📈 Avg Profit per Trade: {result['profit_mean_pct']:.2f}%")
            print(f"   📉 Max Drawdown: {result['max_drawdown_pct']:.2f}%")
            print()

    def generate_overall_stats(self):
        """Δημιουργεί συνολικά στατιστικά"""
        print("\n📊 ΣΥΝΟΛΙΚΑ ΣΤΑΤΙΣΤΙΚΑ:")
        print("-" * 50)

        profits = [r['total_profit_pct'] for r in self.results]
        trades = [r['total_trades'] for r in self.results]
        win_rates = [r['win_rate'] for r in self.results]

        positive_results = len([p for p in profits if p > 0])
        negative_results = len([p for p in profits if p <= 0])

        print(f"Συνολικά tests: {len(self.results)}")
        print(f"Μέσος Profit: {sum(profits)/len(profits):.2f}%")
        print(f"Διάμεσος Profit: {sorted(profits)[len(profits)//2]:.2f}%")
        print(f"Καλύτερο αποτέλεσμα: {max(profits):.2f}%")
        print(f"Χειρότερο αποτέλεσμα: {min(profits):.2f}%")
        print(f"Μέσος αριθμός trades: {sum(trades)/len(trades):.0f}")
        print(f"Μέσο Win Rate: {sum(win_rates)/len(win_rates):.1f}%")
        print()
        print(f"✅ Θετικά αποτελέσματα: {positive_results}/{len(self.results)} ({positive_results/len(self.results)*100:.1f}%)")
        print(f"❌ Αρνητικά/Μηδενικά: {negative_results}/{len(self.results)} ({negative_results/len(self.results)*100:.1f}%)")

    def save_to_csv(self):
        """Αποθηκεύει τα αποτελέσματα σε CSV"""
        df = pd.DataFrame(self.results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backtest_results/comprehensive_analysis_{timestamp}.csv"
        df.to_csv(filename, index=False)
        print(f"\n💾 Αποτελέσματα αποθηκεύτηκαν: {filename}")

def main():
    """Main function"""
    print("📊 Comprehensive Backtest Analysis")
    print("=" * 40)

    analyzer = BacktestAnalyzer()
    analyzer.load_all_results()

    if not analyzer.results:
        print("❌ Δεν βρέθηκαν αποτελέσματα")
        return

    analyzer.generate_overall_stats()
    analyzer.analyze_by_timerange()
    analyzer.analyze_by_pair_group()
    analyzer.analyze_by_stake_amount()
    analyzer.show_top_results(10)
    analyzer.show_worst_results(5)
    analyzer.save_to_csv()

    print("\n🎉 Ανάλυση ολοκληρώθηκε!")

if __name__ == "__main__":
    main()