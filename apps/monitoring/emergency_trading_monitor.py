#!/usr/bin/env python3
"""
🚨 Emergency Trading Monitor - Critical Safety System
🎯 Features:
- Real-time portfolio monitoring
- Automatic emergency stops
- Drawdown protection
- Market crash detection
- Telegram alerts
- Auto-backup of critical data
"""

import json
import sqlite3
import pandas as pd
import numpy as np
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import subprocess
import signal
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../../data/logs/emergency_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EmergencyTradingMonitor:
    """🚨 Emergency Trading Monitor"""

    def __init__(self, config_path: str = "user_data/config.json"):
        self.config_path = config_path
        self.config = self.load_config()

        # Emergency thresholds
        self.max_drawdown = 0.05  # 5% max drawdown
        self.max_daily_loss = 0.03  # 3% max daily loss
        self.max_consecutive_losses = 5
        self.min_account_balance = 1500  # Minimum balance in EUR

        # Monitoring state
        self.is_monitoring = True
        self.emergency_stop_triggered = False
        self.last_check_time = datetime.now()

        # Performance tracking
        self.initial_balance = 2000.0
        self.current_balance = 2000.0
        self.peak_balance = 2000.0
        self.daily_start_balance = 2000.0

        # Trade tracking
        self.consecutive_losses = 0
        self.total_trades = 0
        self.winning_trades = 0

        logger.info("🚨 Emergency Trading Monitor initialized")

    def load_config(self) -> Dict:
        """Load trading configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def get_telegram_config(self) -> Dict:
        """Get Telegram configuration"""
        telegram_config = self.config.get('telegram', {})
        return {
            'token': telegram_config.get('token', ''),
            'chat_id': telegram_config.get('chat_id', '')
        }

    def send_telegram_alert(self, message: str, urgent: bool = False):
        """Send Telegram alert"""
        try:
            telegram = self.get_telegram_config()
            if not telegram['token'] or not telegram['chat_id']:
                logger.warning("Telegram not configured")
                return

            if urgent:
                message = f"🚨 URGENT ALERT 🚨\n{message}"
            else:
                message = f"⚠️ WARNING ⚠️\n{message}"

            url = f"https://api.telegram.org/bot{telegram['token']}/sendMessage"
            data = {
                'chat_id': telegram['chat_id'],
                'text': message,
                'parse_mode': 'HTML'
            }

            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                logger.info("Telegram alert sent successfully")
            else:
                logger.error(f"Failed to send Telegram alert: {response.status_code}")

        except Exception as e:
            logger.error(f"Telegram alert failed: {e}")

    def get_account_balance(self) -> float:
        """Get current account balance from database"""
        try:
            db_path = self.config.get('db_url', 'sqlite:///tradesv3.sqlite').replace('sqlite:///', '')

            if not os.path.exists(db_path):
                logger.warning(f"Database not found: {db_path}")
                return self.current_balance

            conn = sqlite3.connect(db_path)

            # Get total profit from closed trades
            query = """
            SELECT COALESCE(SUM(profit_abs), 0) as total_profit
            FROM trades
            WHERE is_open = 0
            """

            result = pd.read_sql_query(query, conn)
            total_profit = result['total_profit'].iloc[0] if len(result) > 0 else 0

            conn.close()

            # Calculate current balance
            current_balance = self.initial_balance + total_profit
            return current_balance

        except Exception as e:
            logger.error(f"Failed to get account balance: {e}")
            return self.current_balance

    def get_recent_trades(self, hours: int = 24) -> List[Dict]:
        """Get recent trades from database"""
        try:
            db_path = self.config.get('db_url', 'sqlite:///tradesv3.sqlite').replace('sqlite:///', '')

            if not os.path.exists(db_path):
                return []

            conn = sqlite3.connect(db_path)

            # Get recent trades
            cutoff_time = datetime.now() - timedelta(hours=hours)
            query = """
            SELECT pair, profit_abs, profit_ratio, close_date, is_open
            FROM trades
            WHERE close_date > ? OR is_open = 1
            ORDER BY close_date DESC
            """

            trades = pd.read_sql_query(query, conn, params=[cutoff_time])
            conn.close()

            return trades.to_dict('records')

        except Exception as e:
            logger.error(f"Failed to get recent trades: {e}")
            return []

    def calculate_drawdown(self) -> float:
        """Calculate current drawdown"""
        if self.peak_balance <= 0:
            return 0.0

        drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
        return max(0.0, drawdown)

    def calculate_daily_performance(self) -> float:
        """Calculate daily performance"""
        if self.daily_start_balance <= 0:
            return 0.0

        daily_change = (self.current_balance - self.daily_start_balance) / self.daily_start_balance
        return daily_change

    def count_consecutive_losses(self, trades: List[Dict]) -> int:
        """Count consecutive losing trades"""
        consecutive = 0

        for trade in trades:
            if trade['is_open'] == 1:  # Skip open trades
                continue

            if trade['profit_abs'] < 0:
                consecutive += 1
            else:
                break

        return consecutive

    def check_market_crash(self) -> bool:
        """Detect potential market crash"""
        try:
            # Simple crash detection based on rapid balance decline
            recent_trades = self.get_recent_trades(hours=2)

            if len(recent_trades) < 3:
                return False

            # Check if last 3 trades are all losses > 1%
            recent_losses = [t for t in recent_trades[:3] if t['profit_ratio'] < -0.01]

            if len(recent_losses) >= 3:
                logger.warning("Potential market crash detected - multiple large losses")
                return True

            # Check for rapid balance decline
            balance_decline = (self.peak_balance - self.current_balance) / self.peak_balance
            if balance_decline > 0.03:  # 3% decline from peak
                logger.warning(f"Rapid balance decline detected: {balance_decline:.2%}")
                return True

            return False

        except Exception as e:
            logger.error(f"Market crash detection failed: {e}")
            return False

    def emergency_stop_trading(self, reason: str):
        """Emergency stop all trading"""
        try:
            logger.critical(f"🚨 EMERGENCY STOP TRIGGERED: {reason}")

            # Send urgent Telegram alert
            alert_message = f"""
🚨 EMERGENCY STOP ACTIVATED 🚨

Reason: {reason}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Current Balance: {self.current_balance:.2f}€
Drawdown: {self.calculate_drawdown():.2%}
Daily Performance: {self.calculate_daily_performance():.2%}

All trading has been stopped immediately!
Manual intervention required.
"""
            self.send_telegram_alert(alert_message, urgent=True)

            # Try to stop freqtrade processes
            try:
                subprocess.run(['pkill', '-f', 'freqtrade'], check=False)
                logger.info("Freqtrade processes terminated")
            except Exception as e:
                logger.error(f"Failed to stop freqtrade: {e}")

            # Create emergency stop file
            with open('EMERGENCY_STOP.txt', 'w') as f:
                f.write(f"Emergency stop triggered at {datetime.now()}\n")
                f.write(f"Reason: {reason}\n")
                f.write(f"Balance: {self.current_balance:.2f}€\n")

            self.emergency_stop_triggered = True

        except Exception as e:
            logger.critical(f"Emergency stop procedure failed: {e}")

    def backup_critical_data(self):
        """Backup critical trading data"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = f"emergency_backup_{timestamp}"
            os.makedirs(backup_dir, exist_ok=True)

            # Backup database
            db_path = self.config.get('db_url', 'sqlite:///tradesv3.sqlite').replace('sqlite:///', '')
            if os.path.exists(db_path):
                subprocess.run(['cp', db_path, f"{backup_dir}/trades_backup.sqlite"], check=False)

            # Backup config
            if os.path.exists(self.config_path):
                subprocess.run(['cp', self.config_path, f"{backup_dir}/config_backup.json"], check=False)

            # Backup logs
            for log_file in ['freqtrade.log', 'emergency_monitor.log']:
                if os.path.exists(log_file):
                    subprocess.run(['cp', log_file, f"{backup_dir}/{log_file}"], check=False)

            logger.info(f"Critical data backed up to {backup_dir}")

        except Exception as e:
            logger.error(f"Backup failed: {e}")

    def run_safety_checks(self):
        """Run all safety checks"""
        try:
            # Update current balance
            self.current_balance = self.get_account_balance()

            # Update peak balance
            if self.current_balance > self.peak_balance:
                self.peak_balance = self.current_balance

            # Get recent trades
            recent_trades = self.get_recent_trades()

            # Calculate metrics
            drawdown = self.calculate_drawdown()
            daily_performance = self.calculate_daily_performance()
            consecutive_losses = self.count_consecutive_losses(recent_trades)

            # Log current status
            logger.info(f"Balance: {self.current_balance:.2f}€ | Drawdown: {drawdown:.2%} | Daily: {daily_performance:.2%} | Consecutive Losses: {consecutive_losses}")

            # Check emergency conditions
            emergency_reasons = []

            # 1. Maximum drawdown exceeded
            if drawdown > self.max_drawdown:
                emergency_reasons.append(f"Max drawdown exceeded: {drawdown:.2%} > {self.max_drawdown:.2%}")

            # 2. Daily loss limit exceeded
            if daily_performance < -self.max_daily_loss:
                emergency_reasons.append(f"Daily loss limit exceeded: {daily_performance:.2%} < -{self.max_daily_loss:.2%}")

            # 3. Too many consecutive losses
            if consecutive_losses >= self.max_consecutive_losses:
                emergency_reasons.append(f"Too many consecutive losses: {consecutive_losses} >= {self.max_consecutive_losses}")

            # 4. Account balance too low
            if self.current_balance < self.min_account_balance:
                emergency_reasons.append(f"Account balance too low: {self.current_balance:.2f}€ < {self.min_account_balance}€")

            # 5. Market crash detected
            if self.check_market_crash():
                emergency_reasons.append("Market crash conditions detected")

            # Trigger emergency stop if any condition is met
            if emergency_reasons:
                reason = "; ".join(emergency_reasons)
                self.emergency_stop_trading(reason)
                return False

            # Send warning alerts for concerning conditions
            warning_conditions = []

            if drawdown > self.max_drawdown * 0.8:  # 80% of max drawdown
                warning_conditions.append(f"High drawdown: {drawdown:.2%}")

            if daily_performance < -self.max_daily_loss * 0.7:  # 70% of daily limit
                warning_conditions.append(f"High daily loss: {daily_performance:.2%}")

            if consecutive_losses >= self.max_consecutive_losses - 1:
                warning_conditions.append(f"High consecutive losses: {consecutive_losses}")

            if warning_conditions:
                warning_message = f"Trading Warning:\n" + "\n".join(warning_conditions)
                self.send_telegram_alert(warning_message, urgent=False)

            return True

        except Exception as e:
            logger.error(f"Safety checks failed: {e}")
            return False

    def reset_daily_metrics(self):
        """Reset daily metrics at market open"""
        current_date = datetime.now().date()
        last_date = self.last_check_time.date()

        if current_date != last_date:
            self.daily_start_balance = self.current_balance
            logger.info(f"Daily metrics reset. Starting balance: {self.daily_start_balance:.2f}€")

    def run_monitor(self, check_interval: int = 60):
        """Run the monitoring loop"""
        logger.info(f"🚨 Emergency monitor started. Check interval: {check_interval}s")

        try:
            while self.is_monitoring and not self.emergency_stop_triggered:
                # Reset daily metrics if needed
                self.reset_daily_metrics()

                # Run safety checks
                if not self.run_safety_checks():
                    break

                # Update last check time
                self.last_check_time = datetime.now()

                # Wait for next check
                time.sleep(check_interval)

        except KeyboardInterrupt:
            logger.info("Monitor stopped by user")
        except Exception as e:
            logger.critical(f"Monitor crashed: {e}")
            self.emergency_stop_trading(f"Monitor system failure: {e}")
        finally:
            # Backup data on exit
            self.backup_critical_data()
            logger.info("🚨 Emergency monitor stopped")

    def signal_handler(self, signum, frame):
        """Handle system signals"""
        logger.info(f"Received signal {signum}, stopping monitor...")
        self.is_monitoring = False


def main():
    """Main function"""
    monitor = EmergencyTradingMonitor()

    # Setup signal handlers
    signal.signal(signal.SIGINT, monitor.signal_handler)
    signal.signal(signal.SIGTERM, monitor.signal_handler)

    # Start monitoring
    monitor.run_monitor(check_interval=30)  # Check every 30 seconds


if __name__ == "__main__":
    main()