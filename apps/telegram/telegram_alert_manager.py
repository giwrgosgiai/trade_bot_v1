#!/usr/bin/env python3
"""
Telegram Alert Manager - Διαχείριση alerts για το trading bot
"""

import json
import logging
import os
from datetime import datetime, time
from typing import Dict, Any, Optional
from pathlib import Path

# Alert settings file
ALERT_SETTINGS_FILE = "telegram_alert_settings.json"

logger = logging.getLogger(__name__)


class TelegramAlertManager:
    """Διαχειριστής alerts για το Telegram bot."""

    def __init__(self):
        self.settings = self.load_alert_settings()

    def load_alert_settings(self) -> Dict[str, Any]:
        """Φόρτωση ρυθμίσεων alerts από αρχείο."""
        default_settings = {
            "alerts_enabled": True,
            "trading_signals": True,
            "profit_loss_alerts": True,
            "system_status_alerts": True,
            "error_alerts": True,
            "backtest_completion": True,
            "strategy_changes": True,
            "entry_exit_signals": True,
            "risk_alerts": True,
            "min_profit_alert": 1.0,  # Minimum profit % για alert
            "min_loss_alert": -2.0,   # Minimum loss % για alert
            "alert_frequency": "immediate",  # immediate, hourly, daily
            "quiet_hours": {
                "enabled": False,
                "start": "23:00",
                "end": "07:00"
            },
            "alert_types": {
                "🚀": "Entry Signal",
                "🛑": "Exit Signal",
                "💰": "Profit Alert",
                "⚠️": "Loss Alert",
                "🔧": "System Alert",
                "📊": "Backtest Complete",
                "⚡": "Strategy Change",
                "🚨": "Risk Alert"
            }
        }

        try:
            if os.path.exists(ALERT_SETTINGS_FILE):
                with open(ALERT_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                # Merge με default settings για νέα keys
                for key, value in default_settings.items():
                    if key not in settings:
                        settings[key] = value
                return settings
            else:
                self.save_alert_settings(default_settings)
                return default_settings
        except Exception as e:
            logger.error(f"Error loading alert settings: {e}")
            return default_settings

    def save_alert_settings(self, settings: Optional[Dict[str, Any]] = None):
        """Αποθήκευση ρυθμίσεων alerts σε αρχείο."""
        if settings is None:
            settings = self.settings

        try:
            with open(ALERT_SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            self.settings = settings
            logger.info("Alert settings saved successfully")
        except Exception as e:
            logger.error(f"Error saving alert settings: {e}")

    def should_send_alert(self, alert_type: str) -> bool:
        """Έλεγχος αν πρέπει να σταλεί alert."""
        if not self.settings.get("alerts_enabled", True):
            return False

        if not self.settings.get(alert_type, True):
            return False

        # Έλεγχος quiet hours
        quiet_hours = self.settings.get("quiet_hours", {})
        if quiet_hours.get("enabled", False):
            now = datetime.now().time()
            start_time = datetime.strptime(quiet_hours.get("start", "23:00"), "%H:%M").time()
            end_time = datetime.strptime(quiet_hours.get("end", "07:00"), "%H:%M").time()

            if start_time <= end_time:
                if start_time <= now <= end_time:
                    return False
            else:  # Crosses midnight
                if now >= start_time or now <= end_time:
                    return False

        return True

    def toggle_alert_type(self, alert_type: str) -> bool:
        """Εναλλαγή ενεργοποίησης/απενεργοποίησης τύπου alert."""
        if alert_type in self.settings:
            self.settings[alert_type] = not self.settings[alert_type]
            self.save_alert_settings()
            return self.settings[alert_type]
        return False

    def toggle_all_alerts(self) -> bool:
        """Εναλλαγή όλων των alerts."""
        self.settings["alerts_enabled"] = not self.settings["alerts_enabled"]
        self.save_alert_settings()
        return self.settings["alerts_enabled"]

    def set_quiet_hours(self, enabled: bool, start_time: str = "23:00", end_time: str = "07:00"):
        """Ρύθμιση quiet hours."""
        self.settings["quiet_hours"] = {
            "enabled": enabled,
            "start": start_time,
            "end": end_time
        }
        self.save_alert_settings()

    def set_profit_loss_thresholds(self, min_profit: float, min_loss: float):
        """Ρύθμιση κατωφλίων για profit/loss alerts."""
        self.settings["min_profit_alert"] = min_profit
        self.settings["min_loss_alert"] = min_loss
        self.save_alert_settings()

    def get_alert_status_text(self) -> str:
        """Επιστρέφει κείμενο με την κατάσταση των alerts."""
        status = "🔔 **Alert Settings Status**\n\n"

        # Γενική κατάσταση
        main_status = "🟢 Ενεργά" if self.settings.get("alerts_enabled") else "🔴 Ανενεργά"
        status += f"**Κύρια Alerts**: {main_status}\n\n"

        # Επιμέρους alerts
        alert_types = [
            ("trading_signals", "🚀 Trading Signals"),
            ("profit_loss_alerts", "💰 Profit/Loss Alerts"),
            ("system_status_alerts", "🔧 System Status"),
            ("error_alerts", "⚠️ Error Alerts"),
            ("backtest_completion", "📊 Backtest Complete"),
            ("strategy_changes", "⚡ Strategy Changes"),
            ("entry_exit_signals", "🎯 Entry/Exit Signals"),
            ("risk_alerts", "🚨 Risk Alerts")
        ]

        for key, name in alert_types:
            enabled = self.settings.get(key, True)
            icon = "✅" if enabled else "❌"
            status += f"{icon} {name}\n"

        # Quiet hours
        quiet = self.settings.get("quiet_hours", {})
        if quiet.get("enabled"):
            status += f"\n🌙 **Quiet Hours**: {quiet.get('start')} - {quiet.get('end')}"

        # Thresholds
        status += f"\n\n📈 **Profit Alert**: ≥{self.settings.get('min_profit_alert', 1.0)}%"
        status += f"\n📉 **Loss Alert**: ≤{self.settings.get('min_loss_alert', -2.0)}%"

        return status

    def format_alert_message(self, alert_type: str, title: str, message: str,
                           pair: str = None, profit: float = None) -> str:
        """Μορφοποίηση μηνύματος alert."""
        icons = self.settings.get("alert_types", {})
        icon = icons.get(alert_type, "🔔")

        formatted = f"{icon} **{title}**\n\n"

        if pair:
            formatted += f"**Pair**: {pair}\n"

        if profit is not None:
            profit_icon = "💰" if profit > 0 else "📉"
            formatted += f"**Profit**: {profit_icon} {profit:.2f}%\n"

        formatted += f"\n{message}\n"
        formatted += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

        return formatted

    def create_trading_signal_alert(self, signal_type: str, pair: str,
                                  price: float, reason: str) -> str:
        """Δημιουργία alert για trading signal."""
        if signal_type.upper() == "BUY":
            return self.format_alert_message(
                "🚀", "Entry Signal",
                f"**Action**: BUY\n**Price**: {price}\n**Reason**: {reason}",
                pair=pair
            )
        else:
            return self.format_alert_message(
                "🛑", "Exit Signal",
                f"**Action**: SELL\n**Price**: {price}\n**Reason**: {reason}",
                pair=pair
            )

    def create_profit_loss_alert(self, pair: str, profit_pct: float,
                               current_price: float, entry_price: float) -> str:
        """Δημιουργία alert για profit/loss."""
        alert_type = "💰" if profit_pct > 0 else "⚠️"
        title = "Profit Alert" if profit_pct > 0 else "Loss Alert"

        return self.format_alert_message(
            alert_type, title,
            f"**Entry Price**: {entry_price}\n**Current Price**: {current_price}",
            pair=pair, profit=profit_pct
        )

    def create_system_alert(self, message: str, alert_level: str = "info") -> str:
        """Δημιουργία system alert."""
        icons = {"info": "🔧", "warning": "⚠️", "error": "🚨", "success": "✅"}
        icon = icons.get(alert_level, "🔧")

        return self.format_alert_message(icon, "System Alert", message)

    def create_backtest_alert(self, strategy: str, profit: float,
                            trades: int, win_rate: float) -> str:
        """Δημιουργία alert για backtest completion."""
        return self.format_alert_message(
            "📊", "Backtest Complete",
            f"**Strategy**: {strategy}\n**Total Profit**: {profit:.2f}%\n**Trades**: {trades}\n**Win Rate**: {win_rate:.1f}%"
        )


# Singleton instance
alert_manager = TelegramAlertManager()