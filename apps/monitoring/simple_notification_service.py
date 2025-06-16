#!/usr/bin/env python3
"""
Simple Push Notification Service
Sends Telegram notifications for trading events
"""

import os
import sys
import time
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/simple_notifications.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleNotificationService:
    def __init__(self):
        self.telegram_token = "7295982134:AAF242CTc3vVc9m0qBT3wcF0wljByhlptMQ"
        self.telegram_chat_id = "930268785"
        self.freqtrade_api = "http://localhost:8082"

        logger.info("Starting Simple Push Notification Service...")

    def send_telegram_message(self, message: str) -> bool:
        """Send message to Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }

            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                logger.info("Telegram notification sent successfully")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def get_freqtrade_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        try:
            response = requests.get(f"{self.freqtrade_api}/api/v1/status", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"Failed to get bot status: {e}")
            return {}

    def get_balance(self) -> Dict[str, Any]:
        """Get current balance"""
        try:
            response = requests.get(f"{self.freqtrade_api}/api/v1/balance", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return {}

    def format_trade_notification(self, trade_data: Dict[str, Any], action: str) -> str:
        """Format trade notification message"""
        pair = trade_data.get('pair', 'Unknown')

        if action == 'BUY':
            price = trade_data.get('open_rate', 0)
            stake = trade_data.get('stake_amount', 0)
            return f"🚀 <b>BUY EXECUTED</b>\n" \
                   f"Pair: {pair}\n" \
                   f"Price: ${price:.4f}\n" \
                   f"Stake: {stake:.2f} USDC\n" \
                   f"Time: {datetime.now().strftime('%H:%M:%S')}"

        elif action == 'SELL':
            price = trade_data.get('close_rate', 0)
            profit_pct = trade_data.get('profit_pct', 0)
            profit_abs = trade_data.get('profit_abs', 0)
            duration = trade_data.get('open_duration', 'Unknown')

            emoji = "💰" if profit_pct > 0 else "📉"
            return f"{emoji} <b>SELL EXECUTED</b>\n" \
                   f"Pair: {pair}\n" \
                   f"Price: ${price:.4f}\n" \
                   f"Profit: {profit_pct:.2f}% ({profit_abs:+.2f} USDC)\n" \
                   f"Duration: {duration}\n" \
                   f"Time: {datetime.now().strftime('%H:%M:%S')}"

        return f"📊 Trade Update: {pair} - {action}"

    def monitor_trades(self):
        """Monitor for new trades and send notifications"""
        last_trade_count = 0
        last_balance = 0

        while True:
            try:
                # Get current status
                status = self.get_freqtrade_status()
                balance_info = self.get_balance()

                if status and isinstance(status, list):
                    current_trade_count = len(status)

                    # Check for new trades
                    if current_trade_count != last_trade_count:
                        if current_trade_count > last_trade_count:
                            # New trade opened
                            for trade in status:
                                if trade.get('is_open', False):
                                    message = self.format_trade_notification(trade, 'BUY')
                                    self.send_telegram_message(message)

                        last_trade_count = current_trade_count

                # Check balance changes
                if balance_info and 'total' in balance_info:
                    current_balance = balance_info['total']
                    if last_balance > 0 and abs(current_balance - last_balance) > 0.1:
                        change = current_balance - last_balance
                        emoji = "📈" if change > 0 else "📉"
                        message = f"{emoji} <b>Balance Update</b>\n" \
                                f"New Balance: {current_balance:.2f} USDC\n" \
                                f"Change: {change:+.2f} USDC"
                        self.send_telegram_message(message)

                    last_balance = current_balance

                time.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.error(f"Error in trade monitoring: {e}")
                time.sleep(30)

    def send_status_alert(self, message: str) -> bool:
        """Send status alert"""
        try:
            full_message = f"🤖 <b>AI Trading System</b>\n{message}"
            return self.send_telegram_message(full_message)
        except Exception as e:
            logger.error(f"Failed to send status alert: {e}")
            return False

def main():
    service = SimpleNotificationService()

    # Send startup notification
    service.send_status_alert("✅ Notification Service Started\nMonitoring trades and balance changes...")

    try:
        service.monitor_trades()
    except KeyboardInterrupt:
        logger.info("Notification service stopped by user")
        service.send_status_alert("⚠️ Notification Service Stopped")
    except Exception as e:
        logger.error(f"Notification service crashed: {e}")
        service.send_status_alert(f"❌ Notification Service Error: {str(e)}")

if __name__ == "__main__":
    main()