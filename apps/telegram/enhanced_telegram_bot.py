#!/usr/bin/env python3
"""
🚀 Enhanced Telegram Bot με Beautiful Designer Styling
Comprehensive monitoring and control system
"""

import asyncio
import logging
import os
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import psutil
import pytz
from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

# Import του simple formatter
from simple_beautiful_formatter import SimpleFormatter
import random

# Configuration
BOT_TOKEN = "7295982134:AAF242CTc3vVc9m0qBT3wcF0wljByhlptMQ"
CHAT_ID = 930268785
INITIAL_BALANCE = 500.0  # 500€ αρχικό κεφάλαιο
BASE_CURRENCY = "USDC"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemManager:
    """Διαχείριση συστήματος και processes"""

    @staticmethod
    def get_system_status():
        """Παίρνει το system status"""
        try:
            # CPU και Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Running processes
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        if any(keyword in cmdline for keyword in ['bot', 'dashboard', 'monitor', 'strategy']):
                            python_processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': cmdline[:100] + '...' if len(cmdline) > 100 else cmdline,
                                'cpu': proc.info['cpu_percent'] or 0,
                                'memory': proc.info['memory_percent'] or 0
                            })

            return {
                'cpu_percent': cpu_percent,
                'memory_used': memory.used / (1024**3),  # GB
                'memory_total': memory.total / (1024**3),  # GB
                'memory_percent': memory.percent,
                'disk_used': disk.used / (1024**3),  # GB
                'disk_total': disk.total / (1024**3),  # GB
                'disk_percent': (disk.used / disk.total) * 100,
                'python_processes': python_processes,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}

    @staticmethod
    def get_ai_monitor_status():
        """Παίρνει το AI monitor status"""
        try:
            # Ελέγχουμε αν τρέχει το AI monitor
            ai_running = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'ai_smart_monitor.py' in cmdline:
                        ai_running = True
                        break

            # Διαβάζουμε το activity marker
            activity_file = Path('ai_activity_marker.txt')
            last_activity = None
            if activity_file.exists():
                try:
                    with open(activity_file, 'r') as f:
                        lines = f.readlines()
                        if len(lines) >= 2:
                            last_activity = lines[1].strip()
                except:
                    pass

            # Διαβάζουμε το log
            log_file = Path('../../data/logs/ai_smart_monitor.log')
            recent_logs = []
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        recent_logs = lines[-10:]  # Τελευταίες 10 γραμμές
                except:
                    pass

            return {
                'ai_running': ai_running,
                'last_activity': last_activity,
                'recent_logs': recent_logs,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting AI monitor status: {e}")
            return {'error': str(e)}

    @staticmethod
    def run_command(command, timeout=30):
        """Εκτελεί command με timeout"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Command timed out after {timeout} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

class TradingDatabase:
    """Βάση δεδομένων για trading"""

    def __init__(self):
        self.db_path = "trading_data.db"
        self.init_database()

    def init_database(self):
        """Δημιουργία βάσης δεδομένων"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Πίνακας παραγγελιών
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                amount REAL NOT NULL,
                price REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'open',
                profit REAL DEFAULT 0
            )
        ''')

        # Πίνακας υπολοίπου
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Αρχικό υπόλοιπο
        cursor.execute('SELECT COUNT(*) FROM balance')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO balance (amount) VALUES (?)', (INITIAL_BALANCE,))

        conn.commit()
        conn.close()

    def add_order(self, symbol: str, side: str, amount: float, price: float):
        """Προσθήκη παραγγελίας"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (symbol, side, amount, price)
            VALUES (?, ?, ?, ?)
        ''', (symbol, side, amount, price))
        conn.commit()
        conn.close()

    def get_orders(self, limit: int = 10):
        """Λήψη παραγγελιών"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM orders
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        orders = cursor.fetchall()
        conn.close()
        return orders

    def update_balance(self, new_balance: float):
        """Ενημέρωση υπολοίπου"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO balance (amount) VALUES (?)', (new_balance,))
        conn.commit()
        conn.close()

    def get_current_balance(self):
        """Τρέχον υπόλοιπο"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT amount FROM balance ORDER BY timestamp DESC LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else INITIAL_BALANCE

class TradingSimulator:
    """Προσομοίωση trading"""

    def __init__(self):
        self.db = TradingDatabase()
        self.current_prices = {
            'BTC/USDC': 43250.0,
            'ETH/USDC': 2580.0,
            'ADA/USDC': 0.485,
            'DOT/USDC': 7.25,
            'LINK/USDC': 14.80
        }

    def get_price(self, symbol: str) -> float:
        """Τρέχουσα τιμή (προσομοίωση)"""
        if symbol in self.current_prices:
            # Προσομοίωση μικρών αλλαγών τιμής
            base_price = self.current_prices[symbol]
            change = random.uniform(-0.02, 0.02)  # ±2%
            new_price = base_price * (1 + change)
            self.current_prices[symbol] = new_price
            return new_price
        return 0.0

    def place_order(self, symbol: str, side: str, amount: float):
        """Τοποθέτηση παραγγελίας"""
        price = self.get_price(symbol)
        total_cost = amount * price if side == 'buy' else 0

        current_balance = self.db.get_current_balance()

        if side == 'buy' and total_cost > current_balance:
            return False, "Ανεπαρκές υπόλοιπο"

        self.db.add_order(symbol, side, amount, price)

        if side == 'buy':
            new_balance = current_balance - total_cost
        else:  # sell
            new_balance = current_balance + (amount * price)

        self.db.update_balance(new_balance)
        return True, f"Παραγγελία {side} εκτελέστηκε"

class ChartGenerator:
    """Δημιουργία charts χωρίς matplotlib"""

    def __init__(self):
        self.db = TradingDatabase()

    def create_balance_chart(self):
        """Επιστρέφει None αντί για chart"""
        return None

    def create_orders_chart(self):
        """Επιστρέφει None αντί για chart"""
        return None

# Global instances
trading_simulator = TradingSimulator()
chart_generator = ChartGenerator()

def clean_message(message: str) -> str:
    """Clean message from external references and links."""
    # Remove external service names (case insensitive)
    cleaned = re.sub(r'\bbinance\b', 'exchange', message, flags=re.IGNORECASE)

    # Remove promotional content
    cleaned = re.sub(r'Buy/Sell.*?altcoins\.?', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'cryptocurrency market.*?altcoins\.?', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'The easiest way.*?altcoins\.?', '', cleaned, flags=re.IGNORECASE | re.DOTALL)

    # Remove URLs and links
    cleaned = re.sub(r'https?://[^\s\)]+', '', cleaned)
    cleaned = re.sub(r'www\.[^\s\)]+', '', cleaned)
    cleaned = re.sub(r'[a-zA-Z0-9.-]+\.(com|org|net|io|co)[^\s]*', '', cleaned)

    # Remove markdown links [text](url) - extract just the text
    cleaned = re.sub(r'\[([^\]]+)\]\([^\)]*\)', r'\1', cleaned)

    # Remove HTML links
    cleaned = re.sub(r'<a[^>]*>([^<]+)</a>', r'\1', cleaned)

    # Clean up whitespace
    cleaned = re.sub(r'\(\s*\)', '', cleaned)
    cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()

    return cleaned

async def show_main_menu(query):
    """Show the main menu"""
    text = """
🇬🇷 **ΕΛΛΗΝΙΚΟ TRADING BOT**

🎯 **Τι θέλεις να κάνεις;**

💰 **Trading με 500€ κεφάλαιο**
📊 **Όμορφα Charts & Γραφήματα**
🚀 **Απλά Ελληνικά μηνύματα**
💎 **Όλα σε USDC**

👇 **Επίλεξε κατηγορία:**
    """

    keyboard = [
        [
            InlineKeyboardButton("📊 Auto Backtest", callback_data="menu_backtest"),
            InlineKeyboardButton("🧠 AI Monitor", callback_data="menu_ai_monitor")
        ],
        [
            InlineKeyboardButton("📈 Data Management", callback_data="menu_data"),
            InlineKeyboardButton("⚙️ Strategy Tools", callback_data="menu_strategy")
        ],
        [
            InlineKeyboardButton("🖥️ System Control", callback_data="menu_system"),
            InlineKeyboardButton("⚙️ Process Control", callback_data="menu_process")
        ],
        [
            InlineKeyboardButton("⚡ Quick Actions", callback_data="menu_quick"),
            InlineKeyboardButton("🔧 Advanced Tools", callback_data="menu_advanced")
        ],
        [
            InlineKeyboardButton("ℹ️ Bot Info", callback_data="bot_info"),
            InlineKeyboardButton("🔄 Refresh", callback_data="menu_main")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(clean_message(text), reply_markup=reply_markup, parse_mode='Markdown')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Εντολή έναρξης με ελληνικά"""
    welcome_msg = """
🇬🇷 **ΚΑΛΩΣ ΗΡΘΕΣ ΣΤΟ ΕΛΛΗΝΙΚΟ TRADING BOT!**

🎯 **Τι κάνει αυτό το bot:**
• 📊 Δείχνει το υπόλοιπό σου σε πραγματικό χρόνο
• 📈 Δημιουργεί όμορφα charts με τις συναλλαγές σου
• 💰 Ξεκινάς με 500€ σε USDC
• 🚀 Απλά και κατανοητά μηνύματα στα ελληνικά

💡 **Τι είναι το USDC:**
• Είναι σαν δολάρια για crypto
• 1 USDC = περίπου 1 δολάριο
• Το χρησιμοποιούμε για να αγοράζουμε άλλα νομίσματα

👇 **Πάτησε /help για να ξεκινήσεις!**
    """
    await update.message.reply_text(clean_message(welcome_msg), parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Εντολή /help"""
    if update.message.chat_id != CHAT_ID:
        await update.message.reply_text("❌ Δεν έχεις δικαίωμα χρήσης!")
        return

    help_msg = """
🚀 **Enhanced Trading Bot - NFI5MOHO_WIP Edition**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **NFI5MOHO_WIP Commands:**
• `/nfi5moho` - Strategy information & controls
• `/hyperopt` - Start/manage hyperopt optimization
• `/status` - System and bot status
• `/help` - This help message

📊 **Quick Actions:**
• 💰 Το Πορτοφόλι μου - Balance & portfolio
• 📈 Τιμές Crypto - Current prices
• 📋 Οι Συναλλαγές μου - Trading history
• 📊 Charts - Visual analytics

🔧 **Advanced Features:**
• 🤖 AI Monitor - Smart monitoring
• 📊 System Status - Resource monitoring
• 🚀 Backtesting - Strategy testing
• ⚙️ Strategy Management - NFI5MOHO_WIP tools

💡 **Tips:**
• Use buttons for easy navigation
• Check hyperopt status regularly
• Monitor live tracking for performance
• Emergency stop available in Quick Actions

🎯 **Current Strategy**: NFI5MOHO_WIP (Optimized)
    """

    keyboard = [
        [
            InlineKeyboardButton("💰 Το Πορτοφόλι μου", callback_data="greek_balance"),
            InlineKeyboardButton("📈 Τιμές Crypto", callback_data="greek_prices")
        ],
        [
            InlineKeyboardButton("📋 Οι Συναλλαγές μου", callback_data="greek_orders"),
            InlineKeyboardButton("📊 Charts", callback_data="greek_charts")
        ],
        [
            InlineKeyboardButton("🛒 Αγορά Crypto", callback_data="greek_buy_menu"),
            InlineKeyboardButton("💸 Πώληση Crypto", callback_data="greek_sell_menu")
        ],
        [
            InlineKeyboardButton("🎯 NFI5MOHO Strategy", callback_data="menu_strategy"),
            InlineKeyboardButton("🔧 Hyperopt", callback_data="hyperopt_status")
        ],
        [
            InlineKeyboardButton("🤖 AI Monitor", callback_data="menu_ai_monitor"),
            InlineKeyboardButton("📊 System Status", callback_data="menu_system")
        ],
        [
            InlineKeyboardButton("🚀 Backtesting", callback_data="menu_backtest"),
            InlineKeyboardButton("📊 Data Management", callback_data="menu_data")
        ],
        [
            InlineKeyboardButton("🔧 Process Control", callback_data="menu_process"),
            InlineKeyboardButton("📱 Quick Actions", callback_data="menu_quick")
        ],
        [
            InlineKeyboardButton("🛠️ Advanced Tools", callback_data="menu_advanced"),
            InlineKeyboardButton("ℹ️ Bot Info", callback_data="bot_info")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(help_msg, reply_markup=reply_markup, parse_mode='Markdown')

async def system_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /system command με beautiful styling."""
    status = SystemManager.get_system_status()

    # Χρήση του simple formatter
    beautiful_msg = SimpleFormatter.format_system_status(status)

    await update.message.reply_text(clean_message(beautiful_msg), parse_mode='Markdown')

async def ai_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Εντολή /ai για AI monitor status"""
    if update.message.chat_id != CHAT_ID:
        await update.message.reply_text("❌ Δεν έχεις δικαίωμα χρήσης!")
        return

    ai_status = SystemManager.get_ai_monitor_status()
    status_msg = SimpleFormatter.format_ai_status(ai_status)
    await update.message.reply_text(status_msg, parse_mode='Markdown')

async def hyperopt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Εντολή /hyperopt για NFI5MOHO_WIP optimization"""
    if update.message.chat_id != CHAT_ID:
        await update.message.reply_text("❌ Δεν έχεις δικαίωμα χρήσης!")
        return

    # Check if hyperopt is already running
    hyperopt_running = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['cmdline']:
            cmdline = ' '.join(proc.info['cmdline'])
            if 'hyperopt' in cmdline and 'NFI5MOHO_WIP' in cmdline:
                hyperopt_running = True
                break

    if hyperopt_running:
        text = """
🔄 **NFI5MOHO_WIP Hyperopt Already Running**

⚠️ Hyperopt is currently running for NFI5MOHO_WIP strategy.
Use /status to check progress or buttons below to manage.
        """
        keyboard = [
            [
                InlineKeyboardButton("📊 Check Status", callback_data="hyperopt_status"),
                InlineKeyboardButton("🛑 Stop Hyperopt", callback_data="stop_hyperopt")
            ],
            [
                InlineKeyboardButton("📊 View Results", callback_data="hyperopt_results")
            ]
        ]
    else:
        text = """
🎯 **NFI5MOHO_WIP Hyperopt Control**

🚀 **Ready to optimize NFI5MOHO_WIP strategy**

⚙️ **Configuration**:
• Strategy: NFI5MOHO_WIP
• Spaces: Buy/Sell parameters
• Max Epochs: 1000
• Early Stop: 20 epochs
• Loss Function: SharpeHyperOptLoss

💡 **Estimated Time**: 2-6 hours depending on system
        """
        keyboard = [
            [
                InlineKeyboardButton("🚀 Start Hyperopt", callback_data="start_hyperopt"),
                InlineKeyboardButton("📊 Check Status", callback_data="hyperopt_status")
            ],
            [
                InlineKeyboardButton("📊 View Results", callback_data="hyperopt_results")
            ]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def nfi5moho_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Εντολή /nfi5moho για strategy info"""
    if update.message.chat_id != CHAT_ID:
        await update.message.reply_text("❌ Δεν έχεις δικαίωμα χρήσης!")
        return

    text = """
🎯 **NFI5MOHO_WIP Strategy Info**

📊 **Strategy Details**:
• Name: NFI5MOHO_WIP
• Type: NostalgiaForInfinityV5 + MultiOffsetLamboV0
• Timeframe: 5m
• Max Open Trades: 5
• Stake Amount: 50 USDC

🔧 **Features**:
• Live P&L tracking
• 21 buy conditions
• 8 sell conditions
• Multi-offset indicators
• Protection mechanisms
• Hyperopt optimization

📈 **Performance Tracking**:
• Real-time profit monitoring
• Win/Loss statistics
• Trade analytics
• Runtime metrics

💡 **Commands**:
• /hyperopt - Start optimization
• /status - Check bot status
• /help - Full command list
    """

    keyboard = [
        [
            InlineKeyboardButton("🚀 Test Strategy", callback_data="test_nfi5moho"),
            InlineKeyboardButton("🔧 Hyperopt", callback_data="hyperopt_status")
        ],
        [
            InlineKeyboardButton("📊 Live Tracking", callback_data="nfi5moho_live_tracking"),
            InlineKeyboardButton("📈 Performance", callback_data="strat_performance")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "menu_main":
        await help_command(update, context)

    # Ελληνικά Trading Buttons
    elif data == "greek_balance":
        balance = trading_simulator.db.get_current_balance()
        balance_msg = SimpleFormatter.format_greek_balance(balance, INITIAL_BALANCE)
        keyboard = [[InlineKeyboardButton("🔙 Πίσω στο Μενού", callback_data="menu_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(clean_message(balance_msg), reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "greek_prices":
        prices_msg = SimpleFormatter.format_greek_prices(trading_simulator.current_prices)
        keyboard = [[InlineKeyboardButton("🔙 Πίσω στο Μενού", callback_data="menu_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(clean_message(prices_msg), reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "greek_orders":
        orders = trading_simulator.db.get_orders(10)
        orders_msg = SimpleFormatter.format_greek_orders(orders)
        keyboard = [[InlineKeyboardButton("🔙 Πίσω στο Μενού", callback_data="menu_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(clean_message(orders_msg), reply_markup=reply_markup, parse_mode='Markdown')

    else:
        # Default response for unhandled callbacks
        await query.edit_message_text("🔧 Αυτή η λειτουργία είναι υπό ανάπτυξη...",
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Πίσω", callback_data="menu_main")]]))

# Initialize global objects
trading_simulator = TradingSimulator()
chart_generator = ChartGenerator()

def main():
    """Main function to run the bot"""
    print("🚀 Starting Enhanced Telegram Bot για NFI5MOHO_WIP...")
    print("🤖 Bot Token configured")
    print("📊 Strategy: NFI5MOHO_WIP")
    print("🔧 Features: Hyperopt, Live Tracking, System Monitoring")
    print("🇬🇷 Interface: Greek + English")
    print()

                # Set timezone for APScheduler using pytz
    import os
    os.environ['TZ'] = 'UTC'

    # Monkey patch the timezone issue
    import apscheduler.util
    original_get_localzone = apscheduler.util.get_localzone

    def patched_get_localzone():
        return pytz.UTC

    apscheduler.util.get_localzone = patched_get_localzone

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("system", system_status_command))
    application.add_handler(CommandHandler("ai", ai_status_command))
    application.add_handler(CommandHandler("hyperopt", hyperopt_command))
    application.add_handler(CommandHandler("nfi5moho", nfi5moho_command))

    # Add callback handler
    application.add_handler(CallbackQueryHandler(button_callback))

    # Set bot commands
    commands = [
        BotCommand("start", "🚀 Ξεκίνα το bot"),
        BotCommand("help", "📋 Εμφάνιση μενού"),
        BotCommand("system", "💻 System status"),
        BotCommand("ai", "🤖 AI monitor status"),
        BotCommand("hyperopt", "🔧 NFI5MOHO_WIP optimization"),
        BotCommand("nfi5moho", "🎯 Strategy info"),
    ]

    async def set_commands():
        await application.bot.set_my_commands(commands)

    # Run the bot
    try:
        # Set commands
        asyncio.run(set_commands())
        print("✅ Bot commands set successfully")

        # Start polling
        print("🔄 Starting bot polling...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        logger.error(f"Bot error: {e}")

if __name__ == "__main__":
    main()
