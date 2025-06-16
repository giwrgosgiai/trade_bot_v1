#!/usr/bin/env python3
"""
Push Notification Service for Trading Bot
Sends real-time notifications for:
- Trade entries (BUY orders)
- Trade exits (SELL orders) with P&L
- Important alerts and status updates
- Performance summaries

Supports multiple notification channels:
- Telegram (primary)
- Email (backup)
- Discord (optional)
- Slack (optional)
"""

import asyncio
import aiohttp
import json
import logging
import smtplib
import requests
import sqlite3
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict, List, Optional
from pathlib import Path
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/push_notifications.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PushNotificationService:
    """Comprehensive push notification service for trading bot"""

    def __init__(self, config_path: str = "user_data/config_enhanced.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.api_url = f"http://localhost:{self.config['api_server']['listen_port']}/api/v1"
        self.auth = (self.config['api_server']['username'], self.config['api_server']['password'])

        # Notification settings
        self.telegram_token = self.config.get('telegram', {}).get('token')
        self.telegram_chat_id = self.config.get('telegram', {}).get('chat_id')

        # Email settings (configure these)
        self.email_enabled = False
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = ""  # Your email
        self.email_password = ""  # Your app password
        self.email_to = ""  # Recipient email

        # Discord webhook (optional)
        self.discord_webhook = None

        # Initialize database
        self.db_path = "data/databases/notifications.db"
        self._init_database()

        # Track last known trades
        self.last_trades = {}
        self.last_balance = 0.0

        logger.info("Push Notification Service initialized")

    def _load_config(self) -> dict:
        """Load freqtrade configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def _init_database(self):
        """Initialize database for notification tracking"""
        Path("data/databases").mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications_sent (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER,
                pair TEXT NOT NULL,
                action TEXT NOT NULL,
                amount REAL NOT NULL,
                price REAL NOT NULL,
                profit_pct REAL DEFAULT 0,
                profit_abs REAL DEFAULT 0,
                notification_type TEXT NOT NULL,
                channel TEXT NOT NULL,
                success BOOLEAN DEFAULT TRUE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                total_notifications INTEGER DEFAULT 0,
                successful_notifications INTEGER DEFAULT 0,
                failed_notifications INTEGER DEFAULT 0,
                telegram_sent INTEGER DEFAULT 0,
                email_sent INTEGER DEFAULT 0,
                discord_sent INTEGER DEFAULT 0
            )
        ''')

        conn.commit()
        conn.close()

    async def get_freqtrade_data(self, endpoint: str) -> Optional[dict]:
        """Get data from Freqtrade API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/{endpoint}",
                    auth=aiohttp.BasicAuth(self.auth[0], self.auth[1]),
                    timeout=10
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"API request failed: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching {endpoint}: {e}")
            return None

    def send_telegram_notification(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Send notification via Telegram"""
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("Telegram credentials not configured")
            return False

        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }

            response = requests.post(url, data=data, timeout=10)

            if response.status_code == 200:
                logger.info("Telegram notification sent successfully")
                return True
            else:
                logger.error(f"Telegram notification failed: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            return False

    def send_email_notification(self, subject: str, message: str) -> bool:
        """Send notification via email"""
        if not self.email_enabled or not self.email_user:
            return False

        try:
            msg = MimeMultipart()
            msg['From'] = self.email_user
            msg['To'] = self.email_to
            msg['Subject'] = subject

            msg.attach(MimeText(message, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_user, self.email_to, text)
            server.quit()

            logger.info("Email notification sent successfully")
            return True

        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False

    def send_discord_notification(self, message: str) -> bool:
        """Send notification via Discord webhook"""
        if not self.discord_webhook:
            return False

        try:
            data = {"content": message}
            response = requests.post(self.discord_webhook, json=data, timeout=10)

            if response.status_code == 204:
                logger.info("Discord notification sent successfully")
                return True
            else:
                logger.error(f"Discord notification failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")
            return False

    def format_trade_notification(self, trade_data: dict, action: str) -> str:
        """Format trade notification message"""
        pair = trade_data.get('pair', 'Unknown')
        amount = trade_data.get('stake_amount', 0)
        price = trade_data.get('open_rate' if action == 'BUY' else 'close_rate', 0)
        profit_pct = trade_data.get('profit_pct', 0)
        profit_abs = trade_data.get('profit_abs', 0)

        # Emojis and formatting
        action_emoji = "🟢 BUY" if action == "BUY" else "🔴 SELL"
        profit_emoji = "📈" if profit_pct > 0 else "📉" if profit_pct < 0 else "➡️"

        if action == "BUY":
            message = f"""
{action_emoji} **TRADE OPENED**

💰 **Pair:** `{pair}`
💵 **Amount:** `{amount:.2f} USDC`
💲 **Entry Price:** `${price:.6f}`
🕐 **Time:** `{datetime.now().strftime('%H:%M:%S')}`

🎯 **Strategy:** Enhanced E0V1E
🤖 **Bot:** AI-Powered Trading
            """.strip()
        else:
            duration = ""
            if 'open_date' in trade_data:
                try:
                    open_time = datetime.fromisoformat(trade_data['open_date'].replace('Z', '+00:00'))
                    duration_delta = datetime.now() - open_time.replace(tzinfo=None)
                    hours = int(duration_delta.total_seconds() // 3600)
                    minutes = int((duration_delta.total_seconds() % 3600) // 60)
                    duration = f"⏱️ **Duration:** `{hours}h {minutes}m`\n"
                except:
                    pass

            message = f"""
{action_emoji} **TRADE CLOSED**

💰 **Pair:** `{pair}`
💵 **Amount:** `{amount:.2f} USDC`
💲 **Exit Price:** `${price:.6f}`

{profit_emoji} **Profit:** `{profit_pct:+.2f}%` (`{profit_abs:+.2f} USDC`)
{duration}🕐 **Time:** `{datetime.now().strftime('%H:%M:%S')}`

🎯 **Strategy:** Enhanced E0V1E
🤖 **Bot:** AI-Powered Trading
            """.strip()

        return message

    def format_performance_summary(self, performance_data: dict) -> str:
        """Format performance summary message"""
        total_profit = performance_data.get('profit_closed_coin', 0)
        total_trades = performance_data.get('closed_trades', 0)
        winning_trades = performance_data.get('winning_trades', 0)
        win_rate = (winning_trades / max(1, total_trades)) * 100

        profit_emoji = "📈" if total_profit > 0 else "📉" if total_profit < 0 else "➡️"

        message = f"""
📊 **DAILY PERFORMANCE SUMMARY**

{profit_emoji} **Total Profit:** `{total_profit:+.2f} USDC`
📈 **Win Rate:** `{win_rate:.1f}%` (`{winning_trades}/{total_trades}`)
🔄 **Total Trades:** `{total_trades}`

🎯 **Strategy:** Enhanced E0V1E
📅 **Date:** `{datetime.now().strftime('%Y-%m-%d')}`
        """.strip()

        return message

    async def monitor_trades(self):
        """Monitor for new trades and send notifications"""
        try:
            # Get current open trades
            trades_data = await self.get_freqtrade_data("status")
            if trades_data is None:
                return

            current_trades = {trade['trade_id']: trade for trade in trades_data}

            # Check for new trades (BUY notifications)
            for trade_id, trade in current_trades.items():
                if trade_id not in self.last_trades:
                    # New trade opened
                    message = self.format_trade_notification(trade, "BUY")
                    success = self.send_telegram_notification(message)

                    # Log notification
                    self._log_notification(
                        trade_id=trade_id,
                        pair=trade['pair'],
                        action="BUY",
                        amount=trade['stake_amount'],
                        price=trade['open_rate'],
                        profit_pct=0.0,
                        profit_abs=0.0,
                        channel="telegram",
                        success=success
                    )

            # Check for closed trades (SELL notifications)
            for trade_id, trade in self.last_trades.items():
                if trade_id not in current_trades:
                    # Trade was closed - get closed trade data
                    closed_trades = await self.get_freqtrade_data("trades")
                    if closed_trades:
                        for closed_trade in closed_trades:
                            if closed_trade['trade_id'] == trade_id and not closed_trade.get('is_open', True):
                                message = self.format_trade_notification(closed_trade, "SELL")
                                success = self.send_telegram_notification(message)

                                # Log notification
                                self._log_notification(
                                    trade_id=trade_id,
                                    pair=closed_trade['pair'],
                                    action="SELL",
                                    amount=closed_trade['stake_amount'],
                                    price=closed_trade.get('close_rate', 0),
                                    profit_pct=closed_trade.get('profit_pct', 0),
                                    profit_abs=closed_trade.get('profit_abs', 0),
                                    channel="telegram",
                                    success=success
                                )
                                break

            # Update last trades
            self.last_trades = current_trades

        except Exception as e:
            logger.error(f"Error monitoring trades: {e}")

    def _log_notification(self, trade_id: int, pair: str, action: str, amount: float,
                         price: float, profit_pct: float, profit_abs: float,
                         channel: str, success: bool):
        """Log notification to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO notifications_sent
            (trade_id, pair, action, amount, price, profit_pct, profit_abs,
             notification_type, channel, success)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade_id, pair, action, amount, price, profit_pct, profit_abs,
            'trade', channel, success
        ))

        conn.commit()
        conn.close()

    async def send_daily_summary(self):
        """Send daily performance summary"""
        try:
            performance_data = await self.get_freqtrade_data("profit")
            if performance_data:
                message = self.format_performance_summary(performance_data)
                success = self.send_telegram_notification(message)

                if success:
                    logger.info("Daily summary sent successfully")
                else:
                    logger.error("Failed to send daily summary")
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")

    async def send_status_alert(self, alert_type: str, message: str):
        """Send status alert notification"""
        try:
            alert_emojis = {
                'error': '🚨',
                'warning': '⚠️',
                'info': 'ℹ️',
                'success': '✅'
            }

            emoji = alert_emojis.get(alert_type, 'ℹ️')
            formatted_message = f"""
{emoji} **{alert_type.upper()} ALERT**

{message}

🕐 **Time:** `{datetime.now().strftime('%H:%M:%S')}`
🤖 **Bot:** AI-Powered Trading
            """.strip()

            success = self.send_telegram_notification(formatted_message)

            if success:
                logger.info(f"Status alert sent: {alert_type}")
            else:
                logger.error(f"Failed to send status alert: {alert_type}")

        except Exception as e:
            logger.error(f"Error sending status alert: {e}")

    async def check_bot_health(self):
        """Check bot health and send alerts if needed"""
        try:
            # Check if bot is responsive
            status_data = await self.get_freqtrade_data("status")
            if status_data is None:
                await self.send_status_alert("error", "Bot API is not responding!")
                return

            # Check balance
            balance_data = await self.get_freqtrade_data("balance")
            if balance_data:
                current_balance = balance_data.get('total', 0)

                # Alert on significant balance changes
                if self.last_balance > 0:
                    balance_change = current_balance - self.last_balance
                    change_pct = (balance_change / self.last_balance) * 100

                    if abs(change_pct) > 10:  # Alert on >10% balance change
                        change_emoji = "📈" if balance_change > 0 else "📉"
                        await self.send_status_alert(
                            "info",
                            f"{change_emoji} Balance changed by {change_pct:+.1f}%\n"
                            f"From: {self.last_balance:.2f} USDC\n"
                            f"To: {current_balance:.2f} USDC"
                        )

                self.last_balance = current_balance

        except Exception as e:
            logger.error(f"Error checking bot health: {e}")

    async def run_notification_service(self):
        """Main notification service loop"""
        logger.info("Starting Push Notification Service...")

        # Send startup notification
        await self.send_status_alert("success", "Push Notification Service started successfully!")

        last_daily_summary = datetime.now().date()

        while True:
            try:
                # Monitor trades every 30 seconds
                await self.monitor_trades()

                # Check bot health every 5 minutes
                if int(time.time()) % 300 == 0:
                    await self.check_bot_health()

                # Send daily summary at 23:59
                current_date = datetime.now().date()
                current_time = datetime.now().time()

                if (current_date != last_daily_summary and
                    current_time.hour == 23 and current_time.minute == 59):
                    await self.send_daily_summary()
                    last_daily_summary = current_date

                # Sleep for 30 seconds
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Error in notification service loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error

def main():
    """Main function to run the notification service"""
    service = PushNotificationService()

    try:
        asyncio.run(service.run_notification_service())
    except KeyboardInterrupt:
        logger.info("Push Notification Service stopped by user")
    except Exception as e:
        logger.error(f"Push Notification Service crashed: {e}")

if __name__ == "__main__":
    main()