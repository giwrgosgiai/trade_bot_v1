#!/usr/bin/env python3
"""
🚀 Final Force Trades - Τελικό script για να εμφανιστούν trades στο UI
"""

import requests
from requests.auth import HTTPBasicAuth
import time
import json

def force_trade_on_bot(port, pair):
    """Αναγκάζει ένα bot να κάνει trade"""
    auth = HTTPBasicAuth('freqtrade', 'ruriu7AY')

    try:
        print(f"🚀 Forcing trade on port {port} for {pair}...")

        # Δοκιμάζω forcebuy
        response = requests.post(
            f"http://localhost:{port}/api/v1/forcebuy",
            auth=auth,
            json={'pair': pair},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Trade forced successfully: {result}")
            return True
        else:
            print(f"❌ Force trade failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_bot_status(port):
    """Ελέγχει το status ενός bot"""
    auth = HTTPBasicAuth('freqtrade', 'ruriu7AY')

    try:
        # Ελέγχω αν το bot είναι προσβάσιμο
        response = requests.get(f"http://localhost:{port}/api/v1/ping", auth=auth, timeout=5)
        if response.status_code != 200:
            return False

        # Ελέγχω config
        config_response = requests.get(f"http://localhost:{port}/api/v1/show_config", auth=auth, timeout=5)
        if config_response.status_code == 200:
            config = config_response.json()
            print(f"   📊 Port {port}:")
            print(f"      • Dry run: {config.get('dry_run', 'Unknown')}")
            print(f"      • Force entry: {config.get('force_entry_enable', 'Unknown')}")
            print(f"      • Max trades: {config.get('max_open_trades', 'Unknown')}")
            print(f"      • Stake amount: {config.get('stake_amount', 'Unknown')}")
            return True

        return False

    except Exception as e:
        print(f"   ❌ Port {port}: {str(e)}")
        return False

def main():
    print("🚀 FINAL FORCE TRADES")
    print("=" * 50)

    # Ελέγχω όλα τα bots
    ports = [8080, 8081, 8082]
    pairs = ['BTC/USDC', 'UNI/USDC', 'BTC/USDC']

    print("🔍 Checking bot status...")
    active_bots = []

    for port in ports:
        if check_bot_status(port):
            active_bots.append(port)
        else:
            print(f"   ❌ Port {port}: Not accessible")

    print(f"\n✅ Found {len(active_bots)} active bots")

    if not active_bots:
        print("❌ No active bots found!")
        return

    # Προσπαθώ να κάνω force trades
    print("\n🚀 Attempting to force trades...")

    for i, port in enumerate(active_bots):
        pair = pairs[i] if i < len(pairs) else 'BTC/USDC'

        if force_trade_on_bot(port, pair):
            print(f"✅ Successfully forced trade on port {port}")

            # Περιμένω λίγο και ελέγχω το αποτέλεσμα
            time.sleep(3)

            # Ελέγχω αν εμφανίστηκε trade
            auth = HTTPBasicAuth('freqtrade', 'ruriu7AY')
            try:
                status_response = requests.get(f"http://localhost:{port}/api/v1/status", auth=auth, timeout=5)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   📊 Open trades after force: {len(status_data)}")

                    if status_data:
                        for trade in status_data:
                            print(f"      • {trade.get('pair', 'N/A')}: {trade.get('current_profit_abs', 0):.2f}€")

                trades_response = requests.get(f"http://localhost:{port}/api/v1/trades", auth=auth, timeout=5)
                if trades_response.status_code == 200:
                    trades_data = trades_response.json()
                    total_trades = trades_data.get('total_trades', 0)
                    print(f"   📈 Total trades: {total_trades}")

            except Exception as e:
                print(f"   ❌ Error checking results: {str(e)}")
        else:
            print(f"❌ Failed to force trade on port {port}")

    print("\n🌐 Check the FreqUI now:")
    for port in active_bots:
        print(f"   • http://localhost:{port}")

    print("\n✅ Force trading completed!")

if __name__ == "__main__":
    main()