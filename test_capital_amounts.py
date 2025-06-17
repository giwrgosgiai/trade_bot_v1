#!/usr/bin/env python3
"""
Test NFI5MOHO_WIP strategy with different capital amounts
"""

import subprocess
import json
import os
import shutil
from datetime import datetime

def create_config_with_capital(capital_amount):
    """Create a temporary config file with specified capital amount"""

    # Read the base config
    with open('user_data/config.json', 'r') as f:
        config = json.load(f)

    # Update the dry_run_wallet
    config['dry_run_wallet'] = capital_amount

    # Create temp config filename
    temp_config = f'temp_config_capital_{capital_amount}.json'

    # Write temp config
    with open(temp_config, 'w') as f:
        json.dump(config, f, indent=4)

    return temp_config

def run_backtest(config_file, capital_amount):
    """Run backtest with specified config"""

    print(f"🚀 Testing with {capital_amount} USDC capital...")

    cmd = [
        'freqtrade', 'backtesting',
        '--config', config_file,
        '--strategy', 'NFI5MOHO_WIP',
        '--timerange', '20241101-20241217',
        '--export', 'trades'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            print(f"✅ Success with {capital_amount} USDC")
            return True, result.stdout
        else:
            print(f"❌ Failed with {capital_amount} USDC")
            print(f"Error: {result.stderr}")
            return False, result.stderr

    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout with {capital_amount} USDC")
        return False, "Timeout"
    except Exception as e:
        print(f"💥 Exception with {capital_amount} USDC: {e}")
        return False, str(e)

def extract_results(output_text, capital_amount):
    """Extract key metrics from backtest output"""

    results = {
        'capital': capital_amount,
        'total_trades': 0,
        'profit_usdc': 0.0,
        'profit_pct': 0.0,
        'win_rate': 0.0,
        'avg_duration': '0:00',
        'max_drawdown': 0.0,
        'sharpe': 0.0,
        'sortino': 0.0
    }

    lines = output_text.split('\n')

    for line in lines:
        if 'TOTAL |' in line and '|' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 8:
                try:
                    results['total_trades'] = int(parts[1])
                    results['profit_pct'] = float(parts[3])
                    results['profit_usdc'] = float(parts[4])
                    results['avg_duration'] = parts[6]
                    win_draw_loss = parts[7].split()
                    if len(win_draw_loss) >= 4:
                        results['win_rate'] = float(win_draw_loss[3])
                except (ValueError, IndexError):
                    pass

        elif 'Absolute Drawdown (Account)' in line:
            try:
                results['max_drawdown'] = float(line.split('|')[1].strip().replace('%', ''))
            except:
                pass

        elif 'Sharpe' in line:
            try:
                results['sharpe'] = float(line.split('|')[1].strip())
            except:
                pass

        elif 'Sortino' in line:
            try:
                results['sortino'] = float(line.split('|')[1].strip())
            except:
                pass

    return results

def main():
    """Main function to test different capital amounts"""

    print("🎯 Testing NFI5MOHO_WIP Strategy with Different Capital Amounts")
    print("📅 Timerange: 2024-11-01 to 2024-12-17 (1.5 months)")
    print("=" * 60)

    capital_amounts = [500, 1000, 2000, 3000, 4000]
    all_results = []

    for capital in capital_amounts:
        print(f"\n📊 Testing with {capital} USDC...")

        # Create temp config
        temp_config = create_config_with_capital(capital)

        try:
            # Run backtest
            success, output = run_backtest(temp_config, capital)

            if success:
                # Extract results
                results = extract_results(output, capital)
                all_results.append(results)

                print(f"   💰 Profit: {results['profit_usdc']:.2f} USDC ({results['profit_pct']:.2f}%)")
                print(f"   📈 Trades: {results['total_trades']}")
                print(f"   🎯 Win Rate: {results['win_rate']:.1f}%")
                print(f"   ⏱️  Avg Duration: {results['avg_duration']}")

        finally:
            # Clean up temp config
            if os.path.exists(temp_config):
                os.remove(temp_config)

    # Summary report
    if all_results:
        print("\n" + "=" * 60)
        print("📋 SUMMARY REPORT")
        print("=" * 60)
        print(f"{'Capital':<8} {'Profit USDC':<12} {'Profit %':<10} {'Trades':<8} {'Win Rate':<10} {'Duration':<12}")
        print("-" * 60)

        for result in all_results:
            print(f"{result['capital']:<8} "
                  f"{result['profit_usdc']:<12.2f} "
                  f"{result['profit_pct']:<10.2f} "
                  f"{result['total_trades']:<8} "
                  f"{result['win_rate']:<10.1f} "
                  f"{result['avg_duration']:<12}")

        # Best performance analysis
        print("\n🏆 ANALYSIS:")

        if any(r['total_trades'] > 0 for r in all_results):
            best_profit_pct = max([r for r in all_results if r['total_trades'] > 0], key=lambda x: x['profit_pct'])
            best_profit_abs = max([r for r in all_results if r['total_trades'] > 0], key=lambda x: x['profit_usdc'])
            most_trades = max(all_results, key=lambda x: x['total_trades'])
            best_win_rate = max([r for r in all_results if r['total_trades'] > 0], key=lambda x: x['win_rate'])

            print(f"   📈 Best % Return: {best_profit_pct['capital']} USDC ({best_profit_pct['profit_pct']:.2f}%)")
            print(f"   💰 Best Absolute Profit: {best_profit_abs['capital']} USDC ({best_profit_abs['profit_usdc']:.2f} USDC)")
            print(f"   🔄 Most Active: {most_trades['capital']} USDC ({most_trades['total_trades']} trades)")
            print(f"   🎯 Best Win Rate: {best_win_rate['capital']} USDC ({best_win_rate['win_rate']:.1f}%)")

            # Calculate efficiency (profit per 1000 USDC)
            print(f"\n💡 EFFICIENCY (Profit per 1000 USDC):")
            for result in all_results:
                if result['total_trades'] > 0:
                    efficiency = (result['profit_usdc'] / result['capital']) * 1000
                    print(f"   {result['capital']} USDC → {efficiency:.2f} USDC per 1000")
        else:
            print("   ⚠️  No trades executed in any test")

    print(f"\n✅ Testing completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()