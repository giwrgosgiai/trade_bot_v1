#!/usr/bin/env python3
"""
Clean Telegram Bot - Χωρίς εξωτερικές αναφορές
Διαχειρίζεται όλα τα features του project με καθαρά μηνύματα
"""

import asyncio
import logging
import os
import sys
import subprocess
import json
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading
import psutil

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️ Telegram integration not available. Install with: pip install python-telegram-bot")

# Configuration
BOT_TOKEN = "7295982134:AAF242CTc3vVc9m0qBT3wcF0wljByhlptMQ"
CHAT_ID = 930268785

# Alert settings file
ALERT_SETTINGS_FILE = "telegram_alert_settings.json"

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('../../data/logs/clean_telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def clean_message(message: str) -> str:
    """Clean message from external references and links."""
    # Remove external service names (case insensitive)
    cleaned = re.sub(r'\bbinance\b', 'exchange', message, flags=re.IGNORECASE)

    # Remove promotional content
    cleaned = re.sub(r'Buy/Sell.*?altcoins\.?', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'cryptocurrency market.*?altcoins\.?', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'The easiest way.*?altcoins\.?', '', cleaned, flags=re.IGNORECASE | re.DOTALL)

    # Remove URLs and links (more comprehensive)
    cleaned = re.sub(r'https?://[^\s\)]+', '', cleaned)
    cleaned = re.sub(r'www\.[^\s\)]+', '', cleaned)
    cleaned = re.sub(r'[a-zA-Z0-9.-]+\.(com|org|net|io|co)[^\s]*', '', cleaned)

    # Remove markdown links [text](url) - extract just the text
    cleaned = re.sub(r'\[([^\]]+)\]\([^\)]*\)', r'\1', cleaned)

    # Remove HTML links
    cleaned = re.sub(r'<a[^>]*>([^<]+)</a>', r'\1', cleaned)

    # Remove promotional phrases
    promotional_phrases = [
        r'crypto is better with.*',
        r'cryptocurrency exchange.*',
        r'market cap.*',
        r'token price charts.*',
        r'24h change.*',
        r'bitcoin and other altcoins.*'
    ]

    for phrase in promotional_phrases:
        cleaned = re.sub(phrase, '', cleaned, flags=re.IGNORECASE | re.DOTALL)

    # Remove any remaining parentheses that might be empty
    cleaned = re.sub(r'\(\s*\)', '', cleaned)

    # Remove empty lines and extra whitespace
    cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'\s*\|\s*', ' | ', cleaned)
    cleaned = cleaned.strip()

    return cleaned


class CleanTelegramBot:
    """Clean Telegram bot χωρίς εξωτερικές αναφορές."""

    def __init__(self, bot_token: str, chat_id: int):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.app = None
        self.running_processes = {}
        self.monitoring_active = False
        self.last_activity = time.time()
        self.alert_settings = self.load_alert_settings()
        self.alert_settings = self.load_alert_settings()

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
            "min_profit_alert": 1.0,  # Minimum profit % για alert
            "min_loss_alert": -2.0,   # Minimum loss % για alert
            "alert_frequency": "immediate",  # immediate, hourly, daily
            "quiet_hours": {
                "enabled": False,
                "start": "23:00",
                "end": "07:00"
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

    def save_alert_settings(self, settings: Dict[str, Any]):
        """Αποθήκευση ρυθμίσεων alerts σε αρχείο."""
        try:
            with open(ALERT_SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            self.alert_settings = settings
            logger.info("Alert settings saved successfully")
        except Exception as e:
            logger.error(f"Error saving alert settings: {e}")

    def should_send_alert(self, alert_type: str) -> bool:
        """Έλεγχος αν πρέπει να σταλεί alert."""
        if not self.alert_settings.get("alerts_enabled", True):
            return False

        if not self.alert_settings.get(alert_type, True):
            return False

        # Έλεγχος quiet hours
        quiet_hours = self.alert_settings.get("quiet_hours", {})
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

    async def send_alert(self, message: str, alert_type: str = "general"):
        """Αποστολή alert αν είναι ενεργοποιημένο."""
        if self.should_send_alert(alert_type):
            await self.send_clean_message(f"🚨 **ALERT** 🚨\n\n{message}")
            logger.info(f"Alert sent: {alert_type}")
        else:
            logger.info(f"Alert suppressed: {alert_type}")

    async def start_bot(self):
        """Start the Telegram bot."""
        if not TELEGRAM_AVAILABLE:
            raise ImportError("python-telegram-bot not installed")

        self.app = Application.builder().token(self.bot_token).build()

        # Register commands
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("stop_all", self.stop_all_command))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Set bot commands
        commands = [
            BotCommand("start", "Ξεκίνα το bot"),
            BotCommand("help", "Εμφάνιση όλων των features"),
            BotCommand("status", "System status"),
            BotCommand("stop_all", "Σταμάτα όλες τις διεργασίες")
        ]
        await self.app.bot.set_my_commands(commands)

        # Start monitoring thread
        self.start_monitoring()

        # Send startup message
        await self.send_clean_message("🚀 **Clean Trading Bot Started**\n\nΌλα τα features είναι διαθέσιμα!\nΠάτα /help για όλες τις επιλογές.")

                # Start polling - simple approach
        await self.app.run_polling(drop_pending_updates=True)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_msg = """
🤖 **Καλώς ήρθες στο Clean Trading Bot!**

Αυτό το bot διαχειρίζεται όλα τα features του trading system:

🔹 **Auto Backtesting** με hang detection
🔹 **AI Smart Monitoring**
🔹 **Data Management**
🔹 **Strategy Management**
🔹 **System Monitoring**
🔹 **Process Control**

**Πάτα /help για όλες τις επιλογές! 👇**
        """
        await update.message.reply_text(clean_message(welcome_msg), parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command with clean feature menu."""
        keyboard = [
            [
                InlineKeyboardButton("🚀 Auto Backtesting", callback_data="menu_backtest"),
                InlineKeyboardButton("🧠 AI Monitoring", callback_data="menu_ai_monitor")
            ],
            [
                InlineKeyboardButton("📊 Data Management", callback_data="menu_data"),
                InlineKeyboardButton("⚙️ Strategy Tools", callback_data="menu_strategy")
            ],
            [
                InlineKeyboardButton("📈 System Status", callback_data="menu_system"),
                InlineKeyboardButton("🔧 Process Control", callback_data="menu_process")
            ],
            [
                InlineKeyboardButton("📱 Quick Actions", callback_data="menu_quick"),
                InlineKeyboardButton("🛠️ Advanced Tools", callback_data="menu_advanced")
            ],
            [InlineKeyboardButton("🔄 Refresh Menu", callback_data="menu_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        help_text = """
🎯 **Clean Trading System Control Panel**

Επίλεξε κατηγορία:

🚀 **Auto Backtesting** - Automated backtesting
🧠 **AI Monitoring** - Smart system monitoring
📊 **Data Management** - Trading data management
⚙️ **Strategy Tools** - Strategy management
📈 **System Status** - Real-time monitoring
🔧 **Process Control** - Process management
📱 **Quick Actions** - Γρήγορες ενέργειες
🛠️ **Advanced Tools** - Προχωρημένα εργαλεία

**Όλα με ένα κλικ! 👆**
        """

        clean_text = clean_message(help_text)

        if update.callback_query:
            await update.callback_query.edit_message_text(clean_text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(clean_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks."""
        query = update.callback_query
        await query.answer()

        data = query.data

        # Main menu handlers
        if data == "menu_main":
            await self.help_command(update, context)
        elif data == "menu_backtest":
            await self.show_backtest_menu(query)
        elif data == "menu_ai_monitor":
            await self.show_ai_monitor_menu(query)
        elif data == "menu_data":
            await self.show_data_menu(query)
        elif data == "menu_strategy":
            await self.show_strategy_menu(query)
        elif data == "menu_system":
            await self.show_system_menu(query)
        elif data == "menu_process":
            await self.show_process_menu(query)
        elif data == "menu_quick":
            await self.show_quick_menu(query)
        elif data == "menu_advanced":
            await self.show_advanced_menu(query)

        # Action handlers
        elif data.startswith("action_"):
            await self.handle_action(query, data)

    async def show_backtest_menu(self, query):
        """Show backtesting menu."""
        keyboard = [
            [
                InlineKeyboardButton("🚀 Quick Backtest", callback_data="action_quick_backtest"),
                InlineKeyboardButton("📊 X5 Backtest", callback_data="action_x5_backtest")
            ],
            [
                InlineKeyboardButton("🔄 Comprehensive BT", callback_data="action_comprehensive_bt"),
                InlineKeyboardButton("⚡ Simple BT Basic", callback_data="action_simple_bt_basic")
            ],
            [
                InlineKeyboardButton("📈 View Results", callback_data="action_view_results"),
                InlineKeyboardButton("🛑 Stop Backtest", callback_data="action_stop_backtest")
            ],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = """
🚀 **Auto Backtesting Menu**

Επίλεξε τον τύπο backtesting:

🚀 **Quick Backtest** - Γρήγορο backtest
📊 **X5 Backtest** - Backtest με leverage
🔄 **Comprehensive BT** - Πλήρες backtesting
⚡ **Simple BT Basic** - Βασικό backtesting

📈 **View Results** - Δες αποτελέσματα
🛑 **Stop Backtest** - Σταμάτα backtest
        """

        await query.edit_message_text(clean_message(text), reply_markup=reply_markup, parse_mode='Markdown')

    async def show_ai_monitor_menu(self, query):
        """Show AI monitoring menu."""
        keyboard = [
            [
                InlineKeyboardButton("🧠 Start AI Monitor", callback_data="action_start_ai_monitor"),
                InlineKeyboardButton("🛑 Stop AI Monitor", callback_data="action_stop_ai_monitor")
            ],
            [
                InlineKeyboardButton("📊 AI Status", callback_data="action_ai_status"),
                InlineKeyboardButton("🔍 AI Activity Log", callback_data="action_ai_log")
            ],
            [
                InlineKeyboardButton("⚡ Smart Monitor", callback_data="action_smart_monitor"),
                InlineKeyboardButton("🤖 Auto Monitor", callback_data="action_auto_monitor")
            ],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = """
🧠 **AI Monitoring Menu**

Διαχείριση AI monitoring systems:

🧠 **Start/Stop AI Monitor** - AI monitoring control
📊 **AI Status** - Τρέχων status
🔍 **AI Activity Log** - Activity log

⚡ **Smart Monitor** - Έξυπνο monitoring
🤖 **Auto Monitor** - Αυτόματο monitoring
        """

        await query.edit_message_text(clean_message(text), reply_markup=reply_markup, parse_mode='Markdown')

    async def show_data_menu(self, query):
        """Show data management menu."""
        keyboard = [
            [
                InlineKeyboardButton("📥 Download Data", callback_data="action_download_data"),
                InlineKeyboardButton("🔄 Update Data", callback_data="action_update_data")
            ],
            [
                InlineKeyboardButton("📊 Data Status", callback_data="action_data_status"),
                InlineKeyboardButton("🗂️ Manage Files", callback_data="action_manage_files")
            ],
            [
                InlineKeyboardButton("🧹 Cleanup Data", callback_data="action_cleanup_data"),
                InlineKeyboardButton("💾 Backup Data", callback_data="action_backup_data")
            ],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = """
📊 **Data Management Menu**

Διαχείριση trading data:

📥 **Download Data** - Κατέβασε data
🔄 **Update Data** - Ενημέρωση data
📊 **Data Status** - Status check

🗂️ **Manage Files** - File management
🧹 **Cleanup Data** - Καθαρισμός
💾 **Backup Data** - Data backup
        """

        await query.edit_message_text(clean_message(text), reply_markup=reply_markup, parse_mode='Markdown')

    async def show_strategy_menu(self, query):
        """Show strategy management menu."""
        keyboard = [
            [
                InlineKeyboardButton("📋 List Strategies", callback_data="action_list_strategies"),
                InlineKeyboardButton("🧪 Test Strategy", callback_data="action_test_strategy")
            ],
            [
                InlineKeyboardButton("⚙️ Strategy Config", callback_data="action_strategy_config"),
                InlineKeyboardButton("📊 Strategy Stats", callback_data="action_strategy_stats")
            ],
            [
                InlineKeyboardButton("🔧 Optimize Strategy", callback_data="action_optimize_strategy"),
                InlineKeyboardButton("📈 Compare Strategies", callback_data="action_compare_strategies")
            ],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = """
⚙️ **Strategy Management Menu**

Διαχείριση strategies:

📋 **List Strategies** - Όλες οι strategies
🧪 **Test Strategy** - Strategy testing
⚙️ **Strategy Config** - Configuration

📊 **Strategy Stats** - Στατιστικά
🔧 **Optimize Strategy** - Optimization
📈 **Compare Strategies** - Σύγκριση
        """

        await query.edit_message_text(clean_message(text), reply_markup=reply_markup, parse_mode='Markdown')

    async def show_system_menu(self, query):
        """Show system monitoring menu."""
        keyboard = [
            [
                InlineKeyboardButton("💻 System Info", callback_data="action_system_info"),
                InlineKeyboardButton("📊 Resource Usage", callback_data="action_resource_usage")
            ],
            [
                InlineKeyboardButton("🔍 Process List", callback_data="action_process_list"),
                InlineKeyboardButton("📈 Performance", callback_data="action_performance")
            ],
            [
                InlineKeyboardButton("🗂️ Disk Usage", callback_data="action_disk_usage"),
                InlineKeyboardButton("🌐 Network Status", callback_data="action_network_status")
            ],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = """
📈 **System Monitoring Menu**

Real-time system monitoring:

💻 **System Info** - System information
📊 **Resource Usage** - CPU, Memory, Disk
🔍 **Process List** - Running processes

📈 **Performance** - Performance metrics
🗂️ **Disk Usage** - Disk space
🌐 **Network Status** - Network info
        """

        await query.edit_message_text(clean_message(text), reply_markup=reply_markup, parse_mode='Markdown')

    async def show_process_menu(self, query):
        """Show process control menu."""
        keyboard = [
            [
                InlineKeyboardButton("▶️ Start Services", callback_data="action_start_services"),
                InlineKeyboardButton("⏹️ Stop Services", callback_data="action_stop_services")
            ],
            [
                InlineKeyboardButton("🔄 Restart System", callback_data="action_restart_system"),
                InlineKeyboardButton("🛑 Kill Processes", callback_data="action_kill_processes")
            ],
            [
                InlineKeyboardButton("📊 Service Status", callback_data="action_service_status"),
                InlineKeyboardButton("🔧 Manage Services", callback_data="action_manage_services")
            ],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = """
🔧 **Process Control Menu**

Διαχείριση processes:

▶️ **Start/Stop Services** - Service control
🔄 **Restart System** - System restart
🛑 **Kill Processes** - Process termination

📊 **Service Status** - Service status
🔧 **Manage Services** - Service management
        """

        await query.edit_message_text(clean_message(text), reply_markup=reply_markup, parse_mode='Markdown')

    async def show_quick_menu(self, query):
        """Show quick actions menu."""
        keyboard = [
            [
                InlineKeyboardButton("⚡ Quick Start", callback_data="action_quick_start"),
                InlineKeyboardButton("🛑 Emergency Stop", callback_data="action_emergency_stop")
            ],
            [
                InlineKeyboardButton("📊 Quick Status", callback_data="action_quick_status"),
                InlineKeyboardButton("🔄 Quick Restart", callback_data="action_quick_restart")
            ],
            [
                InlineKeyboardButton("💾 Quick Backup", callback_data="action_quick_backup"),
                InlineKeyboardButton("🧹 Quick Cleanup", callback_data="action_quick_cleanup")
            ],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = """
📱 **Quick Actions Menu**

Γρήγορες ενέργειες:

⚡ **Quick Start** - Ξεκίνα όλα
🛑 **Emergency Stop** - Σταμάτα όλα
📊 **Quick Status** - Status check

🔄 **Quick Restart** - System restart
💾 **Quick Backup** - Backup
🧹 **Quick Cleanup** - Cleanup
        """

        await query.edit_message_text(clean_message(text), reply_markup=reply_markup, parse_mode='Markdown')

    async def show_advanced_menu(self, query):
        """Show advanced tools menu."""
        keyboard = [
            [
                InlineKeyboardButton("🔬 Debug Mode", callback_data="action_debug_mode"),
                InlineKeyboardButton("📝 View Logs", callback_data="action_view_logs")
            ],
            [
                InlineKeyboardButton("⚙️ Config Editor", callback_data="action_config_editor"),
                InlineKeyboardButton("🧪 Test Suite", callback_data="action_test_suite")
            ],
            [
                InlineKeyboardButton("📊 Analytics", callback_data="action_analytics"),
                InlineKeyboardButton("🔧 Maintenance", callback_data="action_maintenance")
            ],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = """
🛠️ **Advanced Tools Menu**

Προχωρημένα εργαλεία:

🔬 **Debug Mode** - Debug logging
📝 **View Logs** - System logs
⚙️ **Config Editor** - Configuration

🧪 **Test Suite** - Testing
📊 **Analytics** - Analytics
🔧 **Maintenance** - Maintenance
        """

        await query.edit_message_text(clean_message(text), reply_markup=reply_markup, parse_mode='Markdown')

    async def handle_action(self, query, action):
        """Handle action callbacks."""
        action_name = action.replace("action_", "")

        await query.edit_message_text(f"🔄 Εκτελώντας: {action_name}...", parse_mode='Markdown')

        try:
            result = await self.execute_action(action_name)

            # Show result with back button
            keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            clean_result = clean_message(result)
            await query.edit_message_text(clean_result, reply_markup=reply_markup, parse_mode='Markdown')

        except Exception as e:
            error_msg = f"❌ **Error**: {str(e)}\n\n🕐 {datetime.now().strftime('%H:%M:%S')}"
            keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(clean_message(error_msg), reply_markup=reply_markup, parse_mode='Markdown')

    async def execute_action(self, action: str) -> str:
        """Execute the requested action."""
        timestamp = datetime.now().strftime('%H:%M:%S')

        if action == "quick_backtest":
            return await self.run_quick_backtest()
        elif action == "x5_backtest":
            return await self.run_x5_backtest()
        elif action == "comprehensive_bt":
            return await self.run_comprehensive_backtest()
        elif action == "simple_bt_basic":
            return await self.run_simple_backtest()
        elif action == "start_ai_monitor":
            return await self.start_ai_monitor()
        elif action == "stop_ai_monitor":
            return await self.stop_ai_monitor()
        elif action == "ai_status":
            return await self.get_ai_status()
        elif action == "download_data":
            return await self.download_data()
        elif action == "system_info":
            return await self.get_system_info()
        elif action == "quick_status":
            return await self.get_quick_status()
        elif action == "emergency_stop":
            return await self.emergency_stop()
        elif action == "quick_start":
            return await self.quick_start()
        else:
            return f"⚠️ **Action not implemented**: {action}\n\n🕐 {timestamp}"

    async def run_quick_backtest(self) -> str:
        """Run quick backtest."""
        try:
            cmd = ["python", "simple_backtest_x5_basic.py"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.running_processes["backtest"] = process

            return "🚀 **Quick Backtest Started**\n\nBacktest ξεκίνησε στο background.\nΘα λάβεις notification όταν τελειώσει."

        except Exception as e:
            return f"❌ **Error starting backtest**: {str(e)}"

    async def run_x5_backtest(self) -> str:
        """Run X5 backtest."""
        try:
            cmd = ["python", "run_backtest_x5.py"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.running_processes["x5_backtest"] = process

            return "📊 **X5 Backtest Started**\n\nX5 backtest ξεκίνησε.\nΘα διαρκέσει περισσότερο."

        except Exception as e:
            return f"❌ **Error starting X5 backtest**: {str(e)}"

    async def run_comprehensive_backtest(self) -> str:
        """Run comprehensive backtest."""
        try:
            cmd = ["python", "comprehensive_backtest.py"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.running_processes["comprehensive"] = process

            return "🔄 **Comprehensive Backtest Started**\n\nΠλήρες backtesting ξεκίνησε.\nΘα διαρκέσει αρκετή ώρα."

        except Exception as e:
            return f"❌ **Error starting comprehensive backtest**: {str(e)}"

    async def run_simple_backtest(self) -> str:
        """Run simple backtest basic."""
        try:
            cmd = ["python", "simple_backtest_x5_basic.py"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.running_processes["simple"] = process

            return "⚡ **Simple Backtest Started**\n\nΒασικό backtest ξεκίνησε.\nΘα τελειώσει σύντομα."

        except Exception as e:
            return f"❌ **Error starting simple backtest**: {str(e)}"

    async def start_ai_monitor(self) -> str:
        """Start AI monitoring."""
        try:
            if not self.monitoring_active:
                cmd = ["python", "ai_smart_monitor.py"]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                self.running_processes["ai_monitor"] = process
                self.monitoring_active = True

                return "🧠 **AI Monitor Started**\n\nAI monitoring system ξεκίνησε.\nΠαρακολουθεί την δραστηριότητα."
            else:
                return "⚠️ **AI Monitor Already Running**\n\nAI monitoring είναι ήδη ενεργό."

        except Exception as e:
            return f"❌ **Error starting AI monitor**: {str(e)}"

    async def stop_ai_monitor(self) -> str:
        """Stop AI monitoring."""
        try:
            if "ai_monitor" in self.running_processes:
                self.running_processes["ai_monitor"].terminate()
                del self.running_processes["ai_monitor"]
                self.monitoring_active = False

                return "🛑 **AI Monitor Stopped**\n\nAI monitoring σταμάτησε."
            else:
                return "⚠️ **AI Monitor Not Running**\n\nAI monitoring δεν τρέχει."

        except Exception as e:
            return f"❌ **Error stopping AI monitor**: {str(e)}"

    async def get_ai_status(self) -> str:
        """Get AI monitoring status."""
        try:
            status = "🟢 Active" if self.monitoring_active else "🔴 Inactive"
            processes = len(self.running_processes)
            uptime = time.time() - self.last_activity

            return f"""
🧠 **AI Monitor Status**

Status: {status}
Running Processes: {processes}
Last Activity: {uptime:.1f}s ago
System Load: {psutil.cpu_percent()}%
Memory Usage: {psutil.virtual_memory().percent}%

🕐 {datetime.now().strftime('%H:%M:%S')}
            """

        except Exception as e:
            return f"❌ **Error getting AI status**: {str(e)}"

    async def download_data(self) -> str:
        """Download trading data."""
        try:
            cmd = ["python", "auto_download_binance_candles.py", "--mode", "once"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.running_processes["download"] = process

            return "📥 **Data Download Started**\n\nDownload των trading data ξεκίνησε.\nΘα λάβεις notification όταν τελειώσει."

        except Exception as e:
            return f"❌ **Error starting data download**: {str(e)}"

    async def get_system_info(self) -> str:
        """Get system information."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return f"""
💻 **System Information**

**CPU Usage**: {cpu_percent}%
**Memory**: {memory.percent}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)
**Disk**: {disk.percent}% ({disk.used // 1024 // 1024 // 1024}GB / {disk.total // 1024 // 1024 // 1024}GB)

**Running Processes**: {len(self.running_processes)}
**Monitoring**: {"🟢 Active" if self.monitoring_active else "🔴 Inactive"}

🕐 {datetime.now().strftime('%H:%M:%S')}
            """

        except Exception as e:
            return f"❌ **Error getting system info**: {str(e)}"

    async def get_quick_status(self) -> str:
        """Get quick system status."""
        try:
            processes = len(self.running_processes)
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent

            status_emoji = "🟢" if cpu < 80 and memory < 80 else "🟡" if cpu < 90 and memory < 90 else "🔴"

            return f"""
📊 **Quick Status** {status_emoji}

**System**: CPU {cpu}% | Memory {memory}%
**Processes**: {processes} running
**Monitoring**: {"🟢" if self.monitoring_active else "🔴"}

**Recent Activity**:
{self.get_recent_activity()}

🕐 {datetime.now().strftime('%H:%M:%S')}
            """

        except Exception as e:
            return f"❌ **Error getting quick status**: {str(e)}"

    async def emergency_stop(self) -> str:
        """Emergency stop all processes."""
        try:
            stopped = []
            for name, process in self.running_processes.items():
                try:
                    process.terminate()
                    stopped.append(name)
                except:
                    pass

            self.running_processes.clear()
            self.monitoring_active = False

            return f"""
🛑 **Emergency Stop Executed**

Stopped processes:
{chr(10).join(f"• {name}" for name in stopped)}

Όλες οι διεργασίες σταμάτησαν.

🕐 {datetime.now().strftime('%H:%M:%S')}
            """

        except Exception as e:
            return f"❌ **Error during emergency stop**: {str(e)}"

    async def quick_start(self) -> str:
        """Quick start essential services."""
        try:
            started = []

            # Start AI monitor
            if not self.monitoring_active:
                await self.start_ai_monitor()
                started.append("AI Monitor")

            # Start data download
            cmd = ["python", "auto_download_binance_candles.py", "--mode", "daemon"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.running_processes["data_daemon"] = process
            started.append("Data Daemon")

            return f"""
⚡ **Quick Start Complete**

Started services:
{chr(10).join(f"• {name}" for name in started)}

Το σύστημα είναι έτοιμο!

🕐 {datetime.now().strftime('%H:%M:%S')}
            """

        except Exception as e:
            return f"❌ **Error during quick start**: {str(e)}"

    def get_recent_activity(self) -> str:
        """Get recent activity summary."""
        try:
            activities = []

            # Check for recent log files
            log_files = ["../../data/logs/clean_telegram_bot.log", "../../data/logs/ai_smart_monitor.log", "../../data/logs/auto_download_binance_candles.log"]
            for log_file in log_files:
                if os.path.exists(log_file):
                    mtime = os.path.getmtime(log_file)
                    if time.time() - mtime < 300:  # Last 5 minutes
                        activities.append(f"• {log_file.replace('.log', '')} active")

            if not activities:
                activities.append("• No recent activity")

            return "\n".join(activities[:3])  # Max 3 activities

        except:
            return "• Unable to check activity"

    def start_monitoring(self):
        """Start background monitoring."""
        def monitor():
            while True:
                try:
                    # Check running processes
                    for name, process in list(self.running_processes.items()):
                        if process.poll() is not None:  # Process finished
                            asyncio.create_task(self.handle_process_completion(name, process))
                            del self.running_processes[name]

                    time.sleep(10)  # Check every 10 seconds

                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(30)

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

    async def handle_process_completion(self, name: str, process):
        """Handle process completion."""
        try:
            stdout, stderr = process.communicate()
            return_code = process.returncode

            if return_code == 0:
                message = f"✅ **{name.title()} Completed Successfully**\n\n🕐 {datetime.now().strftime('%H:%M:%S')}"
            else:
                message = f"❌ **{name.title()} Failed**\n\nReturn code: {return_code}\n\n🕐 {datetime.now().strftime('%H:%M:%S')}"

            await self.send_clean_message(message)

        except Exception as e:
            logger.error(f"Error handling process completion: {e}")

    async def send_clean_message(self, message: str):
        """Send clean message to Telegram."""
        try:
            if self.app and self.app.bot:
                clean_msg = clean_message(message)
                await self.app.bot.send_message(
                    chat_id=self.chat_id,
                    text=clean_msg,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        status_msg = await self.get_quick_status()
        await update.message.reply_text(clean_message(status_msg), parse_mode='Markdown')

    async def stop_all_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop_all command."""
        result = await self.emergency_stop()
        await update.message.reply_text(clean_message(result), parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages."""
        text = update.message.text.lower()

        if "status" in text:
            await self.status_command(update, context)
        elif "help" in text:
            await self.help_command(update, context)
        elif "stop" in text:
            await self.stop_all_command(update, context)
        else:
            await update.message.reply_text(
                "🤖 Δεν κατάλαβα την εντολή.\nΠάτα /help για όλες τις επιλογές!"
            )


async def main():
    """Main function."""
    if not TELEGRAM_AVAILABLE:
        print("❌ Telegram integration not available!")
        print("Install with: pip install python-telegram-bot")
        return

    bot = CleanTelegramBot(BOT_TOKEN, CHAT_ID)

    try:
        print("🚀 Starting Clean Telegram Bot...")
        await bot.start_bot()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
    finally:
        if bot and bot.app:
            try:
                await bot.app.stop()
                await bot.app.shutdown()
            except Exception:
                pass
        print("👋 Bot shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")
    except Exception as e:
        print(f"❌ Error: {e}")