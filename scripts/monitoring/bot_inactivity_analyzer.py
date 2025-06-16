#!/usr/bin/env python3
"""
🔍 Bot Inactivity Analyzer - Ανάλυση γιατί τα bots δεν κάνουν trades
"""

import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime

class BotInactivityAnalyzer:
    def __init__(self):
        self.auth = HTTPBasicAuth('freqtrade', 'ruriu7AY')
        self.bots = [
            {'port': 8080, 'name': 'Main Coins Bot', 'pair': 'BTC/USDC'},
            {'port': 8081, 'name': 'Altcoin Bot', 'pair': 'UNI/USDC'},
            {'port': 8082, 'name': 'Scalping Bot', 'pair': 'BTC/USDC'}
        ]

    def analyze_bot_inactivity(self, bot):
        """Αναλύει γιατί ένα bot δεν κάνει trades"""
        print(f"🔍 Ανάλυση inactivity για {bot['name']}...")

        issues = []

        try:
            # 1. Έλεγχος configuration
            config_response = requests.get(
                f"http://localhost:{bot['port']}/api/v1/show_config",
                auth=self.auth,
                timeout=10
            )

            if config_response.status_code == 200:
                config = config_response.json()

                # Έλεγχος dry run
                if config.get('dry_run', False):
                    issues.append({
                        'type': 'warning',
                        'issue': 'DRY RUN MODE',
                        'description': 'Το bot είναι σε dry run mode - δεν κάνει πραγματικά trades',
                        'solution': 'Αλλάξτε dry_run: false στο config για live trading'
                    })

                # Έλεγχος stake amount
                stake_amount = config.get('stake_amount', 0)
                if isinstance(stake_amount, str):
                    try:
                        stake_amount = float(stake_amount)
                    except:
                        stake_amount = 0

                if stake_amount <= 0:
                    issues.append({
                        'type': 'error',
                        'issue': 'INVALID STAKE AMOUNT',
                        'description': f'Stake amount: {config.get("stake_amount", "N/A")}',
                        'solution': 'Ορίστε έγκυρο stake_amount στο config'
                    })

                # Έλεγχος max open trades
                max_trades = config.get('max_open_trades', 0)
                if max_trades <= 0:
                    issues.append({
                        'type': 'error',
                        'issue': 'NO OPEN TRADES ALLOWED',
                        'description': f'Max open trades: {max_trades}',
                        'solution': 'Ορίστε max_open_trades > 0'
                    })

                # Έλεγχος exchange
                exchange = config.get('exchange', 'Unknown')
                if exchange == 'Unknown':
                    issues.append({
                        'type': 'error',
                        'issue': 'NO EXCHANGE CONFIGURED',
                        'description': 'Δεν έχει οριστεί exchange',
                        'solution': 'Ορίστε έγκυρο exchange στο config'
                    })

            # 2. Έλεγχος balance
            balance_response = requests.get(
                f"http://localhost:{bot['port']}/api/v1/balance",
                auth=self.auth,
                timeout=10
            )

            if balance_response.status_code == 200:
                balance = balance_response.json()
                total_balance = balance.get('total', 0)

                if total_balance <= 0:
                    issues.append({
                        'type': 'error',
                        'issue': 'NO BALANCE',
                        'description': f'Total balance: {total_balance}',
                        'solution': 'Προσθέστε κεφάλαια στο wallet'
                    })
                elif total_balance < stake_amount:
                    issues.append({
                        'type': 'warning',
                        'issue': 'INSUFFICIENT BALANCE',
                        'description': f'Balance: {total_balance}, Stake: {stake_amount}',
                        'solution': 'Μειώστε το stake_amount ή προσθέστε κεφάλαια'
                    })

            # 3. Έλεγχος signals
            signals_response = requests.get(
                f"http://localhost:{bot['port']}/api/v1/pair_candles",
                auth=self.auth,
                params={'pair': bot['pair'], 'timeframe': '5m', 'limit': 1},
                timeout=10
            )

            if signals_response.status_code == 200:
                data = signals_response.json()
                if data.get('data') and len(data['data']) > 0:
                    latest_candle = data['data'][0]
                    columns = data.get('columns', [])

                    candle_dict = {}
                    for i, col in enumerate(columns):
                        if i < len(latest_candle):
                            candle_dict[col] = latest_candle[i]

                    enter_long = candle_dict.get('enter_long', 0)
                    exit_long = candle_dict.get('exit_long', 0)

                    if enter_long == 0 and exit_long == 0:
                        issues.append({
                            'type': 'info',
                            'issue': 'NO CURRENT SIGNALS',
                            'description': 'Δεν υπάρχουν active trading signals αυτή τη στιγμή',
                            'solution': 'Περιμένετε για trading opportunities'
                        })
                    elif enter_long == 1:
                        issues.append({
                            'type': 'info',
                            'issue': 'BUY SIGNAL ACTIVE',
                            'description': 'Υπάρχει active buy signal',
                            'solution': 'Το bot θα πρέπει να κάνει trade αν δεν είναι σε dry run'
                        })

            # 4. Έλεγχος whitelist
            whitelist_response = requests.get(
                f"http://localhost:{bot['port']}/api/v1/whitelist",
                auth=self.auth,
                timeout=10
            )

            if whitelist_response.status_code == 200:
                whitelist = whitelist_response.json()
                if not whitelist.get('whitelist', []):
                    issues.append({
                        'type': 'error',
                        'issue': 'EMPTY WHITELIST',
                        'description': 'Δεν υπάρχουν pairs στο whitelist',
                        'solution': 'Προσθέστε trading pairs στο whitelist'
                    })
                elif bot['pair'] not in whitelist.get('whitelist', []):
                    issues.append({
                        'type': 'warning',
                        'issue': 'PAIR NOT IN WHITELIST',
                        'description': f'{bot["pair"]} δεν είναι στο whitelist',
                        'solution': f'Προσθέστε {bot["pair"]} στο whitelist'
                    })

            return {
                'bot_name': bot['name'],
                'issues': issues,
                'config': config if 'config' in locals() else None
            }

        except Exception as e:
            return {
                'bot_name': bot['name'],
                'error': str(e),
                'issues': [{
                    'type': 'error',
                    'issue': 'CONNECTION ERROR',
                    'description': f'Σφάλμα σύνδεσης: {str(e)}',
                    'solution': 'Ελέγξτε αν το bot τρέχει'
                }]
            }

    def analyze_all_bots(self):
        """Αναλύει όλα τα bots"""
        print("🔍 BOT INACTIVITY ANALYZER")
        print("=" * 80)
        print(f"⏰ Έναρξη ανάλυσης: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        all_results = {}

        for bot in self.bots:
            print(f"🤖 ΑΝΑΛΥΣΗ: {bot['name']} (Port: {bot['port']})")
            print("=" * 60)

            result = self.analyze_bot_inactivity(bot)
            all_results[bot['name']] = result

            if 'error' in result:
                print(f"❌ Σφάλμα: {result['error']}")
            else:
                issues = result['issues']

                if not issues:
                    print("✅ Δεν βρέθηκαν προβλήματα!")
                else:
                    print(f"📋 Βρέθηκαν {len(issues)} θέματα:")
                    print()

                    for i, issue in enumerate(issues, 1):
                        icon = {
                            'error': '❌',
                            'warning': '⚠️',
                            'info': 'ℹ️'
                        }.get(issue['type'], '•')

                        print(f"   {i}. {icon} {issue['issue']}")
                        print(f"      📝 {issue['description']}")
                        print(f"      💡 {issue['solution']}")
                        print()

            print("=" * 60)
            print()

        # Σύνοψη
        self.print_summary(all_results)

        return all_results

    def print_summary(self, results):
        """Εκτύπωση σύνοψης"""
        print("📋 ΣΥΝΟΨΗ ΠΡΟΒΛΗΜΑΤΩΝ")
        print("=" * 80)

        total_errors = 0
        total_warnings = 0
        total_infos = 0

        for bot_name, result in results.items():
            if 'error' not in result:
                issues = result['issues']
                errors = len([i for i in issues if i['type'] == 'error'])
                warnings = len([i for i in issues if i['type'] == 'warning'])
                infos = len([i for i in issues if i['type'] == 'info'])

                total_errors += errors
                total_warnings += warnings
                total_infos += infos

                status = "🟢 OK" if not issues else "🔴 ISSUES"
                print(f"🤖 {bot_name}: {status}")
                if issues:
                    print(f"   ❌ Errors: {errors}")
                    print(f"   ⚠️ Warnings: {warnings}")
                    print(f"   ℹ️ Info: {infos}")
            else:
                total_errors += 1
                print(f"🤖 {bot_name}: 🔴 CONNECTION ERROR")

            print()

        print(f"📊 ΣΥΝΟΛΙΚΑ:")
        print(f"   ❌ Total Errors: {total_errors}")
        print(f"   ⚠️ Total Warnings: {total_warnings}")
        print(f"   ℹ️ Total Info: {total_infos}")
        print()

        # Κύριοι λόγοι inactivity
        print("🎯 ΚΥΡΙΟΙ ΛΟΓΟΙ INACTIVITY:")
        print("   1. 🔄 DRY RUN MODE - Τα bots είναι σε simulation mode")
        print("   2. 📊 NO TRADING SIGNALS - Δεν υπάρχουν κατάλληλες συνθήκες για trade")
        print("   3. 💰 BALANCE ISSUES - Προβλήματα με το available balance")
        print("   4. ⚙️ CONFIGURATION ISSUES - Λάθος ρυθμίσεις")
        print()
        print("✅ Ανάλυση ολοκληρώθηκε!")

def main():
    analyzer = BotInactivityAnalyzer()
    try:
        results = analyzer.analyze_all_bots()
        return results
    except Exception as e:
        print(f"❌ Σφάλμα: {str(e)}")
        return None

if __name__ == "__main__":
    main()