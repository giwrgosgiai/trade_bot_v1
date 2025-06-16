#!/usr/bin/env python3
"""
Simple script to check FreqTrade UI and display trade information
"""

import requests
import json
from requests.auth import HTTPBasicAuth

def check_bot_status(port, bot_name):
    """Check the status of a FreqTrade bot"""
    base_url = f"http://localhost:{port}/api/v1"
    auth = HTTPBasicAuth("freqtrade", "ruriu7AY")

    print(f"\n🤖 {bot_name} (Port {port})")
    print("=" * 50)

    try:
        # Check status
        response = requests.get(f"{base_url}/status", auth=auth, timeout=5)
        if response.status_code == 200:
            trades = response.json()
            print(f"✅ Active trades: {len(trades)}")

            for trade in trades:
                print(f"  📈 {trade['pair']}: {trade['profit_pct']:.2f}% profit")
        else:
            print(f"❌ Status check failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

    try:
        # Check profit
        response = requests.get(f"{base_url}/profit", auth=auth, timeout=5)
        if response.status_code == 200:
            profit = response.json()
            print(f"💰 Total profit: {profit.get('profit_all_coin', 0):.4f} USDT")
        else:
            print(f"❌ Profit check failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Profit check failed: {e}")

def main():
    """Main function"""
    print("🚀 FreqTrade Bot Status Check")
    print("=" * 50)

    bots = [
        (8080, "AI Learning Day Trading Bot"),
        (8081, "Ultimate Profit Altcoin Bot"),
        (8082, "Ultra Fast Scalping Bot")
    ]

    for port, name in bots:
        check_bot_status(port, name)

    print(f"\n🌐 Web Interface URLs:")
    print(f"Bot 1: http://localhost:8080")
    print(f"Bot 2: http://localhost:8081")
    print(f"Bot 3: http://localhost:8082")

    print(f"\n📊 To view in browser, open any of the above URLs")
    print(f"Username: freqtrade")
    print(f"Password: ruriu7AY")

if __name__ == "__main__":
    main()
"""
Simple script to check FreqTrade UI and display trade information
"""

import requests
import json
from requests.auth import HTTPBasicAuth

def check_bot_status(port, bot_name):
    """Check the status of a FreqTrade bot"""
    base_url = f"http://localhost:{port}/api/v1"
    auth = HTTPBasicAuth("freqtrade", "ruriu7AY")

    print(f"\n🤖 {bot_name} (Port {port})")
    print("=" * 50)

    try:
        # Check status
        response = requests.get(f"{base_url}/status", auth=auth, timeout=5)
        if response.status_code == 200:
            trades = response.json()
            print(f"✅ Active trades: {len(trades)}")

            for trade in trades:
                print(f"  📈 {trade['pair']}: {trade['profit_pct']:.2f}% profit")
        else:
            print(f"❌ Status check failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

    try:
        # Check profit
        response = requests.get(f"{base_url}/profit", auth=auth, timeout=5)
        if response.status_code == 200:
            profit = response.json()
            print(f"💰 Total profit: {profit.get('profit_all_coin', 0):.4f} USDT")
        else:
            print(f"❌ Profit check failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Profit check failed: {e}")

def main():
    """Main function"""
    print("🚀 FreqTrade Bot Status Check")
    print("=" * 50)

    bots = [
        (8080, "AI Learning Day Trading Bot"),
        (8081, "Ultimate Profit Altcoin Bot"),
        (8082, "Ultra Fast Scalping Bot")
    ]

    for port, name in bots:
        check_bot_status(port, name)

    print(f"\n🌐 Web Interface URLs:")
    print(f"Bot 1: http://localhost:8080")
    print(f"Bot 2: http://localhost:8081")
    print(f"Bot 3: http://localhost:8082")

    print(f"\n📊 To view in browser, open any of the above URLs")
    print(f"Username: freqtrade")
    print(f"Password: ruriu7AY")

if __name__ == "__main__":
    main()
"""
Simple script to check FreqTrade UI and display trade information
"""

import requests
import json
from requests.auth import HTTPBasicAuth

def check_bot_status(port, bot_name):
    """Check the status of a FreqTrade bot"""
    base_url = f"http://localhost:{port}/api/v1"
    auth = HTTPBasicAuth("freqtrade", "ruriu7AY")

    print(f"\n🤖 {bot_name} (Port {port})")
    print("=" * 50)

    try:
        # Check status
        response = requests.get(f"{base_url}/status", auth=auth, timeout=5)
        if response.status_code == 200:
            trades = response.json()
            print(f"✅ Active trades: {len(trades)}")

            for trade in trades:
                print(f"  📈 {trade['pair']}: {trade['profit_pct']:.2f}% profit")
        else:
            print(f"❌ Status check failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

    try:
        # Check profit
        response = requests.get(f"{base_url}/profit", auth=auth, timeout=5)
        if response.status_code == 200:
            profit = response.json()
            print(f"💰 Total profit: {profit.get('profit_all_coin', 0):.4f} USDT")
        else:
            print(f"❌ Profit check failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Profit check failed: {e}")

def main():
    """Main function"""
    print("🚀 FreqTrade Bot Status Check")
    print("=" * 50)

    bots = [
        (8080, "AI Learning Day Trading Bot"),
        (8081, "Ultimate Profit Altcoin Bot"),
        (8082, "Ultra Fast Scalping Bot")
    ]

    for port, name in bots:
        check_bot_status(port, name)

    print(f"\n🌐 Web Interface URLs:")
    print(f"Bot 1: http://localhost:8080")
    print(f"Bot 2: http://localhost:8081")
    print(f"Bot 3: http://localhost:8082")

    print(f"\n📊 To view in browser, open any of the above URLs")
    print(f"Username: freqtrade")
    print(f"Password: ruriu7AY")

if __name__ == "__main__":
    main()
"""
Simple script to check FreqTrade UI and display trade information
"""

import requests
import json
from requests.auth import HTTPBasicAuth

def check_bot_status(port, bot_name):
    """Check the status of a FreqTrade bot"""
    base_url = f"http://localhost:{port}/api/v1"
    auth = HTTPBasicAuth("freqtrade", "ruriu7AY")

    print(f"\n🤖 {bot_name} (Port {port})")
    print("=" * 50)

    try:
        # Check status
        response = requests.get(f"{base_url}/status", auth=auth, timeout=5)
        if response.status_code == 200:
            trades = response.json()
            print(f"✅ Active trades: {len(trades)}")

            for trade in trades:
                print(f"  📈 {trade['pair']}: {trade['profit_pct']:.2f}% profit")
        else:
            print(f"❌ Status check failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

    try:
        # Check profit
        response = requests.get(f"{base_url}/profit", auth=auth, timeout=5)
        if response.status_code == 200:
            profit = response.json()
            print(f"💰 Total profit: {profit.get('profit_all_coin', 0):.4f} USDT")
        else:
            print(f"❌ Profit check failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Profit check failed: {e}")

def main():
    """Main function"""
    print("🚀 FreqTrade Bot Status Check")
    print("=" * 50)

    bots = [
        (8080, "AI Learning Day Trading Bot"),
        (8081, "Ultimate Profit Altcoin Bot"),
        (8082, "Ultra Fast Scalping Bot")
    ]

    for port, name in bots:
        check_bot_status(port, name)

    print(f"\n🌐 Web Interface URLs:")
    print(f"Bot 1: http://localhost:8080")
    print(f"Bot 2: http://localhost:8081")
    print(f"Bot 3: http://localhost:8082")

    print(f"\n📊 To view in browser, open any of the above URLs")
    print(f"Username: freqtrade")
    print(f"Password: ruriu7AY")

if __name__ == "__main__":
    main()
"""
Simple script to check FreqTrade UI and display trade information
"""

import requests
import json
from requests.auth import HTTPBasicAuth

def check_bot_status(port, bot_name):
    """Check the status of a FreqTrade bot"""
    base_url = f"http://localhost:{port}/api/v1"
    auth = HTTPBasicAuth("freqtrade", "ruriu7AY")

    print(f"\n🤖 {bot_name} (Port {port})")
    print("=" * 50)

    try:
        # Check status
        response = requests.get(f"{base_url}/status", auth=auth, timeout=5)
        if response.status_code == 200:
            trades = response.json()
            print(f"✅ Active trades: {len(trades)}")

            for trade in trades:
                print(f"  📈 {trade['pair']}: {trade['profit_pct']:.2f}% profit")
        else:
            print(f"❌ Status check failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

    try:
        # Check profit
        response = requests.get(f"{base_url}/profit", auth=auth, timeout=5)
        if response.status_code == 200:
            profit = response.json()
            print(f"💰 Total profit: {profit.get('profit_all_coin', 0):.4f} USDT")
        else:
            print(f"❌ Profit check failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Profit check failed: {e}")

def main():
    """Main function"""
    print("🚀 FreqTrade Bot Status Check")
    print("=" * 50)

    bots = [
        (8080, "AI Learning Day Trading Bot"),
        (8081, "Ultimate Profit Altcoin Bot"),
        (8082, "Ultra Fast Scalping Bot")
    ]

    for port, name in bots:
        check_bot_status(port, name)

    print(f"\n🌐 Web Interface URLs:")
    print(f"Bot 1: http://localhost:8080")
    print(f"Bot 2: http://localhost:8081")
    print(f"Bot 3: http://localhost:8082")

    print(f"\n📊 To view in browser, open any of the above URLs")
    print(f"Username: freqtrade")
    print(f"Password: ruriu7AY")

if __name__ == "__main__":
    main()
"""
Simple script to check FreqTrade UI and display trade information
"""

import requests
import json
from requests.auth import HTTPBasicAuth

def check_bot_status(port, bot_name):
    """Check the status of a FreqTrade bot"""
    base_url = f"http://localhost:{port}/api/v1"
    auth = HTTPBasicAuth("freqtrade", "ruriu7AY")

    print(f"\n🤖 {bot_name} (Port {port})")
    print("=" * 50)

    try:
        # Check status
        response = requests.get(f"{base_url}/status", auth=auth, timeout=5)
        if response.status_code == 200:
            trades = response.json()
            print(f"✅ Active trades: {len(trades)}")

            for trade in trades:
                print(f"  📈 {trade['pair']}: {trade['profit_pct']:.2f}% profit")
        else:
            print(f"❌ Status check failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

    try:
        # Check profit
        response = requests.get(f"{base_url}/profit", auth=auth, timeout=5)
        if response.status_code == 200:
            profit = response.json()
            print(f"💰 Total profit: {profit.get('profit_all_coin', 0):.4f} USDT")
        else:
            print(f"❌ Profit check failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Profit check failed: {e}")

def main():
    """Main function"""
    print("🚀 FreqTrade Bot Status Check")
    print("=" * 50)

    bots = [
        (8080, "AI Learning Day Trading Bot"),
        (8081, "Ultimate Profit Altcoin Bot"),
        (8082, "Ultra Fast Scalping Bot")
    ]

    for port, name in bots:
        check_bot_status(port, name)

    print(f"\n🌐 Web Interface URLs:")
    print(f"Bot 1: http://localhost:8080")
    print(f"Bot 2: http://localhost:8081")
    print(f"Bot 3: http://localhost:8082")

    print(f"\n📊 To view in browser, open any of the above URLs")
    print(f"Username: freqtrade")
    print(f"Password: ruriu7AY")

if __name__ == "__main__":
    main()
"""
Simple script to check FreqTrade UI and display trade information
"""

import requests
import json
from requests.auth import HTTPBasicAuth

def check_bot_status(port, bot_name):
    """Check the status of a FreqTrade bot"""
    base_url = f"http://localhost:{port}/api/v1"
    auth = HTTPBasicAuth("freqtrade", "ruriu7AY")

    print(f"\n🤖 {bot_name} (Port {port})")
    print("=" * 50)

    try:
        # Check status
        response = requests.get(f"{base_url}/status", auth=auth, timeout=5)
        if response.status_code == 200:
            trades = response.json()
            print(f"✅ Active trades: {len(trades)}")

            for trade in trades:
                print(f"  📈 {trade['pair']}: {trade['profit_pct']:.2f}% profit")
        else:
            print(f"❌ Status check failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

    try:
        # Check profit
        response = requests.get(f"{base_url}/profit", auth=auth, timeout=5)
        if response.status_code == 200:
            profit = response.json()
            print(f"💰 Total profit: {profit.get('profit_all_coin', 0):.4f} USDT")
        else:
            print(f"❌ Profit check failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Profit check failed: {e}")

def main():
    """Main function"""
    print("🚀 FreqTrade Bot Status Check")
    print("=" * 50)

    bots = [
        (8080, "AI Learning Day Trading Bot"),
        (8081, "Ultimate Profit Altcoin Bot"),
        (8082, "Ultra Fast Scalping Bot")
    ]

    for port, name in bots:
        check_bot_status(port, name)

    print(f"\n🌐 Web Interface URLs:")
    print(f"Bot 1: http://localhost:8080")
    print(f"Bot 2: http://localhost:8081")
    print(f"Bot 3: http://localhost:8082")

    print(f"\n📊 To view in browser, open any of the above URLs")
    print(f"Username: freqtrade")
    print(f"Password: ruriu7AY")

if __name__ == "__main__":
    main()