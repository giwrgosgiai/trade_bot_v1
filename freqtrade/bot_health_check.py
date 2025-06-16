#!/usr/bin/env python3
"""
🏥 FreqTrade Bot Health Check System
Detailed monitoring and diagnostics for FreqTrade bots
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from requests.auth import HTTPBasicAuth
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/giwrgosgiai/freqtrade/logs/health_check.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class BotHealthChecker:
    def __init__(self):
        self.bots = {
            'bot1': {
                'name': 'AI Learning Day Trading Bot',
                'port': 8080,
                'strategy': 'AILearningDayTradingStrategy'
            },
            'bot2': {
                'name': 'Ultimate Profit Altcoin Bot',
                'port': 8081,
                'strategy': 'UltimateProfitAltcoinStrategy'
            },
            'bot3': {
                'name': 'Ultra Fast Scalping Bot',
                'port': 8082,
                'strategy': 'UltraFastScalpingStrategy'
            }
        }
        self.auth = HTTPBasicAuth("freqtrade", "ruriu7AY")

    def check_api_endpoint(self, port, endpoint, timeout=5):
        """Check if a specific API endpoint responds"""
        try:
            url = f"http://localhost:{port}/api/v1/{endpoint}"
            response = requests.get(url, auth=self.auth, timeout=timeout)
            return response.status_code == 200, response
        except Exception as e:
            return False, str(e)

    def get_bot_status(self, port):
        """Get detailed bot status"""
        status = {
            'api_responsive': False,
            'active_trades': 0,
            'total_profit': 0.0,
            'balance': 0.0,
            'last_update': None,
            'errors': []
        }

        # Check ping
        ping_ok, ping_response = self.check_api_endpoint(port, 'ping')
        if not ping_ok:
            status['errors'].append(f"Ping failed: {ping_response}")
            return status

        status['api_responsive'] = True

        # Check status
        status_ok, status_response = self.check_api_endpoint(port, 'status')
        if status_ok:
            try:
                trades = status_response.json()
                status['active_trades'] = len(trades)
            except Exception as e:
                status['errors'].append(f"Status parse error: {e}")
        else:
            status['errors'].append(f"Status check failed: {status_response}")

        # Check profit
        profit_ok, profit_response = self.check_api_endpoint(port, 'profit')
        if profit_ok:
            try:
                profit_data = profit_response.json()
                status['total_profit'] = profit_data.get('profit_all_coin', 0.0)
            except Exception as e:
                status['errors'].append(f"Profit parse error: {e}")
        else:
            status['errors'].append(f"Profit check failed: {profit_response}")

        # Check balance
        balance_ok, balance_response = self.check_api_endpoint(port, 'balance')
        if balance_ok:
            try:
                balance_data = balance_response.json()
                if 'currencies' in balance_data:
                    for currency in balance_data['currencies']:
                        if currency['currency'] == 'USDT':
                            status['balance'] = currency.get('free', 0.0)
                            break
            except Exception as e:
                status['errors'].append(f"Balance parse error: {e}")
        else:
            status['errors'].append(f"Balance check failed: {balance_response}")

        status['last_update'] = datetime.now().isoformat()
        return status

    def check_all_bots(self):
        """Check health of all bots"""
        results = {}

        for bot_id, bot_info in self.bots.items():
            logger.info(f"🔍 Checking {bot_info['name']}...")
            results[bot_id] = {
                'info': bot_info,
                'status': self.get_bot_status(bot_info['port'])
            }

        return results

    def print_status_report(self, results):
        """Print a formatted status report"""
        print("\n" + "="*60)
        print("🏥 FreqTrade Bot Health Report")
        print("="*60)
        print(f"📅 Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        all_healthy = True

        for bot_id, data in results.items():
            bot_info = data['info']
            status = data['status']

            print(f"🤖 {bot_info['name']}")
            print(f"   Port: {bot_info['port']}")
            print(f"   Strategy: {bot_info['strategy']}")

            if status['api_responsive']:
                print("   ✅ API: Responsive")
                print(f"   📊 Active Trades: {status['active_trades']}")
                print(f"   💰 Total Profit: {status['total_profit']:.4f} USDT")
                print(f"   💳 Balance: {status['balance']:.2f} USDT")

                if status['errors']:
                    print("   ⚠️  Warnings:")
                    for error in status['errors']:
                        print(f"      - {error}")
            else:
                print("   ❌ API: Not Responsive")
                all_healthy = False
                if status['errors']:
                    print("   🚨 Errors:")
                    for error in status['errors']:
                        print(f"      - {error}")

            print()

        if all_healthy:
            print("🎉 All bots are healthy!")
        else:
            print("⚠️  Some bots need attention!")

        print("\n🌐 Web Interfaces:")
        for bot_id, data in results.items():
            port = data['info']['port']
            status_icon = "✅" if data['status']['api_responsive'] else "❌"
            print(f"   {status_icon} Bot {bot_id[-1]}: http://localhost:{port}")

        print("\n🔑 Credentials: freqtrade / ruriu7AY")
        print("="*60)

        return all_healthy

    def continuous_monitoring(self, interval=60):
        """Continuously monitor bots"""
        logger.info("🔄 Starting continuous monitoring...")

        while True:
            try:
                results = self.check_all_bots()
                healthy = self.print_status_report(results)

                if not healthy:
                    logger.warning("⚠️  Some bots are unhealthy!")

                time.sleep(interval)

            except KeyboardInterrupt:
                logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                time.sleep(10)

def main():
    checker = BotHealthChecker()

    if len(sys.argv) > 1:
        if sys.argv[1] == "monitor":
            checker.continuous_monitoring()
        elif sys.argv[1] == "check":
            results = checker.check_all_bots()
            healthy = checker.print_status_report(results)
            sys.exit(0 if healthy else 1)
        else:
            print("Usage: python3 bot_health_check.py [check|monitor]")
            sys.exit(1)
    else:
        # Default: single check
        results = checker.check_all_bots()
        healthy = checker.print_status_report(results)
        sys.exit(0 if healthy else 1)

if __name__ == "__main__":
    main()