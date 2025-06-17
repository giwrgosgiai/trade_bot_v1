#!/usr/bin/env python3
"""
Comprehensive Backtesting Script
Τρέχει πολλά backtests με διαφορετικά δεδομένα και παράγει συνολικά αποτελέσματα
"""

import os
import subprocess
import json
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
from pathlib import Path

class MultipleBacktestRunner:
    def __init__(self):
        self.results = []
        self.base_config = "user_data/config.json"
        self.strategy = "NFI5MOHO_WIP"

        # Διαφορετικά timeframes για testing
        self.timeframes = ["5m", "15m", "1h"]

        # Διαφορετικές περίοδοι για backtesting
        self.timeranges = [
            "20241201-20241217",  # Τελευταίες 2+ εβδομάδες
            "20241115-20241217",  # Τελευταίος μήνας
            "20241101-20241217",  # Τελευταίοι 1.5 μήνες
            "20241015-20241217",  # Τελευταίοι 2 μήνες
        ]

        # Top pairs για testing
        self.pair_groups = {
            "major": ["BTC/USDC", "ETH/USDC", "BNB/USDC"],
            "defi": ["LINK/USDC", "INJ/USDC", "OP/USDC"],
            "meme": ["DOGE/USDC", "PEPE/USDC"],
            "layer1": ["SOL/USDC", "ARB/USDC"],
            "all": ["BTC/USDC", "ETH/USDC", "BNB/USDC", "SOL/USDC", "LINK/USDC",
                   "INJ/USDC", "OP/USDC", "ARB/USDC", "DOGE/USDC", "PEPE/USDC"]
        }

        # Διαφορετικά stake amounts για testing
        self.stake_amounts = [100, 200, 500]

    def create_temp_config(self, timeframe, pairs, stake_amount):
        """Δημιουργεί προσωρινό config file για το backtest"""
        with open(self.base_config, 'r') as f:
            config = json.load(f)

        # Ενημέρωση config
        config["timeframe"] = timeframe
        config["exchange"]["pair_whitelist"] = pairs
        config["stake_amount"] = stake_amount
        config["dry_run_wallet"] = stake_amount * 30  # 30x του stake amount

        # Αποθήκευση προσωρινού config
        temp_config_path = f"temp_config_{timeframe}_{len(pairs)}pairs_{stake_amount}.json"
        with open(temp_config_path, 'w') as f:
            json.dump(config, f, indent=4)

        return temp_config_path

    def run_backtest(self, config_path, timerange, test_name):
        """Τρέχει ένα backtest και επιστρέφει τα αποτελέσματα"""
        print(f"\n🚀 Τρέχω backtest: {test_name}")
        print(f"   Config: {config_path}")
        print(f"   Timerange: {timerange}")

        cmd = [
            "freqtrade", "backtesting",
            "--config", config_path,
            "--strategy", self.strategy,
            "--timerange", timerange,
            "--export", "trades",
            "--export-filename", f"backtest_results/{test_name}",
            "--breakdown", "day"
        ]

        try:
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            end_time = time.time()

            if result.returncode == 0:
                print(f"   ✅ Επιτυχές! Διάρκεια: {end_time - start_time:.1f}s")
                return self.parse_backtest_results(result.stdout, test_name, end_time - start_time)
            else:
                print(f"   ❌ Αποτυχία: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout μετά από 5 λεπτά")
            return None
        except Exception as e:
            print(f"   💥 Σφάλμα: {str(e)}")
            return None

    def parse_backtest_results(self, output, test_name, duration):
        """Παρσάρει τα αποτελέσματα του backtest"""
        lines = output.split('\n')
        result = {
            'test_name': test_name,
            'duration': duration,
            'timestamp': datetime.now().isoformat(),
            'total_trades': 0,
            'total_profit_pct': 0.0,
            'total_profit_usdc': 0.0,
            'avg_duration': 'N/A',
            'best_pair': 'N/A',
            'worst_pair': 'N/A',
            'win_rate': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'calmar_ratio': 0.0
        }

        # Εξαγωγή βασικών μετρικών
        for line in lines:
            if 'Total trades' in line:
                result['total_trades'] = self.extract_number(line)
            elif 'Total Profit' in line and '%' in line:
                result['total_profit_pct'] = self.extract_percentage(line)
            elif 'Total profit' in line and 'USDC' in line:
                result['total_profit_usdc'] = self.extract_number(line)
            elif 'Avg. Duration' in line:
                result['avg_duration'] = line.split(':')[-1].strip()
            elif 'Best Pair' in line:
                result['best_pair'] = line.split(':')[-1].strip()
            elif 'Worst Pair' in line:
                result['worst_pair'] = line.split(':')[-1].strip()
            elif 'Win Rate' in line:
                result['win_rate'] = self.extract_percentage(line)
            elif 'Max Drawdown' in line:
                result['max_drawdown'] = self.extract_percentage(line)
            elif 'Sharpe Ratio' in line:
                result['sharpe_ratio'] = self.extract_number(line)
            elif 'Calmar Ratio' in line:
                result['calmar_ratio'] = self.extract_number(line)

        return result

    def extract_number(self, text):
        """Εξάγει αριθμό από κείμενο"""
        import re
        numbers = re.findall(r'-?\d+\.?\d*', text)
        return float(numbers[0]) if numbers else 0

    def extract_percentage(self, text):
        """Εξάγει ποσοστό από κείμενο"""
        import re
        percentages = re.findall(r'-?\d+\.?\d*%', text)
        if percentages:
            return float(percentages[0].replace('%', ''))
        return 0

    def cleanup_temp_files(self):
        """Καθαρίζει προσωρινά αρχεία"""
        for file in Path('.').glob('temp_config_*.json'):
            file.unlink()

    def run_all_backtests(self):
        """Τρέχει όλα τα backtests"""
        print("🎯 Ξεκινάω πολλαπλά backtests...")
        print(f"📊 Στρατηγική: {self.strategy}")
        print(f"⏰ Timeframes: {', '.join(self.timeframes)}")
        print(f"📅 Περίοδοι: {len(self.timeranges)} διαφορετικές")
        print(f"💰 Stake amounts: {', '.join(map(str, self.stake_amounts))}")

        # Δημιουργία φακέλου για αποτελέσματα
        os.makedirs("backtest_results", exist_ok=True)

        test_counter = 0
        total_tests = len(self.timeframes) * len(self.timeranges) * len(self.pair_groups) * len(self.stake_amounts)

        for timeframe in self.timeframes:
            for timerange in self.timeranges:
                for group_name, pairs in self.pair_groups.items():
                    for stake_amount in self.stake_amounts:
                        test_counter += 1
                        test_name = f"{timeframe}_{timerange}_{group_name}_{stake_amount}USDC"

                        print(f"\n📈 Test {test_counter}/{total_tests}: {test_name}")

                        # Δημιουργία προσωρινού config
                        temp_config = self.create_temp_config(timeframe, pairs, stake_amount)

                        # Εκτέλεση backtest
                        result = self.run_backtest(temp_config, timerange, test_name)

                        if result:
                            result.update({
                                'timeframe': timeframe,
                                'timerange': timerange,
                                'pair_group': group_name,
                                'pairs_count': len(pairs),
                                'stake_amount': stake_amount
                            })
                            self.results.append(result)

                        # Καθαρισμός προσωρινού config
                        if os.path.exists(temp_config):
                            os.remove(temp_config)

                        # Μικρή παύση μεταξύ tests
                        time.sleep(2)

        self.generate_summary_report()

    def generate_summary_report(self):
        """Δημιουργεί συνολικό report με όλα τα αποτελέσματα"""
        if not self.results:
            print("❌ Δεν υπάρχουν αποτελέσματα για report")
            return

        print(f"\n📊 Δημιουργώ συνολικό report με {len(self.results)} αποτελέσματα...")

        try:
            # Δημιουργία DataFrame
            df = pd.DataFrame(self.results)

            # Έλεγχος ότι υπάρχουν τα απαραίτητα columns
            required_columns = ['total_profit_pct', 'total_trades', 'win_rate']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = 0.0

            # Αποθήκευση σε CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"backtest_results/summary_report_{timestamp}.csv"
            df.to_csv(csv_filename, index=False)

            # Δημιουργία αναλυτικού report
            self.create_detailed_report(df, timestamp)

            print(f"✅ Report αποθηκεύτηκε: {csv_filename}")

        except Exception as e:
            print(f"💥 Σφάλμα στη δημιουργία report: {str(e)}")
            # Αποθήκευση raw results σε περίπτωση σφάλματος
            import json
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_filename = f"backtest_results/raw_results_{timestamp}.json"
            with open(raw_filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"📄 Raw results αποθηκεύτηκαν: {raw_filename}")

    def create_detailed_report(self, df, timestamp):
        """Δημιουργεί αναλυτικό report"""
        report_filename = f"backtest_results/detailed_analysis_{timestamp}.txt"

        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("🎯 ΣΥΝΟΛΙΚΑ ΑΠΟΤΕΛΕΣΜΑΤΑ BACKTESTING\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"📅 Ημερομηνία: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"📊 Στρατηγική: {self.strategy}\n")
            f.write(f"🔢 Συνολικά tests: {len(df)}\n\n")

            # Top 10 καλύτερα αποτελέσματα
            f.write("🏆 TOP 10 ΚΑΛΥΤΕΡΑ ΑΠΟΤΕΛΕΣΜΑΤΑ (Profit %)\n")
            f.write("-" * 50 + "\n")
            if 'total_profit_pct' in df.columns and len(df) > 0:
                top_10 = df.nlargest(min(10, len(df)), 'total_profit_pct')
                for idx, row in top_10.iterrows():
                    f.write(f"{row['test_name']}: {row.get('total_profit_pct', 0):.2f}% "
                           f"({int(row.get('total_trades', 0))} trades, {row.get('win_rate', 0):.1f}% win rate)\n")
            else:
                f.write("Δεν υπάρχουν διαθέσιμα δεδομένα\n")

            f.write("\n" + "🔻 TOP 10 ΧΕΙΡΟΤΕΡΑ ΑΠΟΤΕΛΕΣΜΑΤΑ\n")
            f.write("-" * 50 + "\n")
            if 'total_profit_pct' in df.columns and len(df) > 0:
                worst_10 = df.nsmallest(min(10, len(df)), 'total_profit_pct')
                for idx, row in worst_10.iterrows():
                    f.write(f"{row['test_name']}: {row.get('total_profit_pct', 0):.2f}% "
                           f"({int(row.get('total_trades', 0))} trades)\n")
            else:
                f.write("Δεν υπάρχουν διαθέσιμα δεδομένα\n")

            # Ανάλυση ανά timeframe
            f.write("\n" + "⏰ ΑΝΑΛΥΣΗ ΑΝΑ TIMEFRAME\n")
            f.write("-" * 50 + "\n")
            timeframe_analysis = df.groupby('timeframe').agg({
                'total_profit_pct': ['mean', 'std', 'max', 'min'],
                'total_trades': 'mean',
                'win_rate': 'mean'
            }).round(2)
            f.write(str(timeframe_analysis) + "\n\n")

            # Ανάλυση ανά pair group
            f.write("💰 ΑΝΑΛΥΣΗ ΑΝΑ PAIR GROUP\n")
            f.write("-" * 50 + "\n")
            pair_analysis = df.groupby('pair_group').agg({
                'total_profit_pct': ['mean', 'std', 'max', 'min'],
                'total_trades': 'mean',
                'win_rate': 'mean'
            }).round(2)
            f.write(str(pair_analysis) + "\n\n")

            # Ανάλυση ανά stake amount
            f.write("💵 ΑΝΑΛΥΣΗ ΑΝΑ STAKE AMOUNT\n")
            f.write("-" * 50 + "\n")
            stake_analysis = df.groupby('stake_amount').agg({
                'total_profit_pct': ['mean', 'std', 'max', 'min'],
                'total_trades': 'mean',
                'win_rate': 'mean'
            }).round(2)
            f.write(str(stake_analysis) + "\n\n")

            # Συνολικά στατιστικά
            f.write("📈 ΣΥΝΟΛΙΚΑ ΣΤΑΤΙΣΤΙΚΑ\n")
            f.write("-" * 50 + "\n")
            if 'total_profit_pct' in df.columns and len(df) > 0:
                f.write(f"Μέσος Profit: {df['total_profit_pct'].mean():.2f}%\n")
                f.write(f"Διάμεσος Profit: {df['total_profit_pct'].median():.2f}%\n")
                f.write(f"Καλύτερο αποτέλεσμα: {df['total_profit_pct'].max():.2f}%\n")
                f.write(f"Χειρότερο αποτέλεσμα: {df['total_profit_pct'].min():.2f}%\n")
                f.write(f"Τυπική απόκλιση: {df['total_profit_pct'].std():.2f}%\n")
                f.write(f"Μέσος αριθμός trades: {df['total_trades'].mean():.1f}\n")
                f.write(f"Μέσο Win Rate: {df['win_rate'].mean():.1f}%\n")

                # Θετικά vs αρνητικά αποτελέσματα
                positive_results = len(df[df['total_profit_pct'] > 0])
                negative_results = len(df[df['total_profit_pct'] < 0])
                f.write(f"\n✅ Θετικά αποτελέσματα: {positive_results} ({positive_results/len(df)*100:.1f}%)\n")
                f.write(f"❌ Αρνητικά αποτελέσματα: {negative_results} ({negative_results/len(df)*100:.1f}%)\n")
            else:
                f.write("Δεν υπάρχουν διαθέσιμα δεδομένα για στατιστικά\n")

        print(f"📄 Αναλυτικό report: {report_filename}")

def main():
    """Main function"""
    print("🤖 Multiple Backtest Runner")
    print("=" * 30)

    runner = MultipleBacktestRunner()

    try:
        runner.run_all_backtests()
        print("\n🎉 Όλα τα backtests ολοκληρώθηκαν!")
        print("📁 Τα αποτελέσματα βρίσκονται στο φάκελο: backtest_results/")

    except KeyboardInterrupt:
        print("\n⏹️ Διακοπή από χρήστη")
        runner.cleanup_temp_files()
    except Exception as e:
        print(f"\n💥 Σφάλμα: {str(e)}")
        runner.cleanup_temp_files()
    finally:
        runner.cleanup_temp_files()

if __name__ == "__main__":
    main()