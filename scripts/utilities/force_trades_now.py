#!/usr/bin/env python3
"""
🚀 FORCE TRADES NOW - Immediate Trading Activity
Εξαναγκάζει τα bots να κάνουν trades για άμεση δοκιμή
"""

import requests
import json
import time
from datetime import datetime

# Bot configurations
BOTS = {
    'MainCoins': {
        'port': 8080,
        'pairs': ['BTC/USDC', 'ETH/USDC', 'BNB/USDC'],
        'name': 'MainCoins Bot'
    },
    'Altcoin': {
        'port': 8082,
        'pairs': ['ADA/USDC', 'UNI/USDC', 'LINK/USDC'],
        'name': 'Altcoin Bot'
    },
    'Scalping': {
        'port': 8084,
        'pairs': ['BTC/USDC', 'ETH/USDC'],
        'name': 'Scalping Bot'
    }
}

AUTH = ('freqtrade', 'ruriu7AY')

def force_entry(bot_name, port, pair):
    """Force entry for a specific pair"""
    try:
        url = f"http://localhost:{port}/api/v1/forceentry"
        data = {
            "pair": pair,
            "side": "long"
        }

        response = requests.post(url, json=data, auth=AUTH, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ {bot_name}: Force entry {pair} - {result.get('status', 'Success')}")
            return True
        else:
            print(f"❌ {bot_name}: Failed to force entry {pair} - {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ {bot_name}: Error forcing entry {pair} - {str(e)}")
        return False

def get_bot_status(port):
    """Get bot status"""
    try:
        url = f"http://localhost:{port}/api/v1/status"
        response = requests.get(url, auth=AUTH, timeout=5)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except Exception as e:
        return None

def main():
    print("🚀 FORCE TRADES NOW - Starting...")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    total_forced = 0

    for bot_key, bot_config in BOTS.items():
        print(f"\n🤖 Processing {bot_config['name']}...")

        # Check if bot is running
        status = get_bot_status(bot_config['port'])
        if not status:
            print(f"❌ {bot_config['name']}: Bot not responding")
            continue

        print(f"✅ {bot_config['name']}: Bot is running")

        # Force entries for each pair
        for pair in bot_config['pairs']:
            if force_entry(bot_config['name'], bot_config['port'], pair):
                total_forced += 1
                time.sleep(2)  # Wait between requests

    print("\n" + "=" * 50)
    print(f"🎯 SUMMARY: Forced {total_forced} trades across all bots")

    # Wait and show final status
    print("\n⏳ Waiting 10 seconds for trades to process...")
    time.sleep(10)

    print("\n📊 FINAL STATUS:")
    for bot_key, bot_config in BOTS.items():
        status = get_bot_status(bot_config['port'])
        if status:
            trade_count = len(status)
            print(f"   {bot_config['name']}: {trade_count} active trades")
        else:
            print(f"   {bot_config['name']}: Not responding")

    print("\n✅ Force trades completed!")

if __name__ == "__main__":
    main()