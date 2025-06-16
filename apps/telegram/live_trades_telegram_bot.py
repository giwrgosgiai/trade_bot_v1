#!/usr/bin/env python3
"""
Live Trades Telegram Bot - Παρακολούθηση ζωντανών συναλλαγών
Συνδέεται με το Freqtrade API και εμφανίζει κέρδη σε USDC
"""

import os
import json
import time
import requests
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
from typing import Dict, List, Optional

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('../../data/logs/live_trades_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LiveTradesBot:
    def __init__(self):
        self.freqtrade_url = "http://localhost:8080"
        self.freqtrade_auth = ("freqtrade", "freqtrade123")
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '')

        if not self.bot_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
            return

        if not self.chat_id:
            logger.error("❌ TELEGRAM_CHAT_ID not set!")
            return

    def get_freqtrade_data(self, endpoint: str) -> Optional[Dict]:
        """Get data from Freqtrade API"""
        try:
            url = f"{self.freqtrade_url}/api/v1/{endpoint}"
            response = requests.get(url, auth=self.freqtrade_auth, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"API error {response.status_code}: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Connection error: {e}")
            return None

    def format_profit_usdt(self, profit_abs: float) -> str:
        """Format profit in USDC with color emoji"""
        if profit_abs > 0:
            return f"🟢 +{profit_abs:.2f} USDC"
        elif profit_abs < 0:
            return f"🔴 {profit_abs:.2f} USDC"
        else:
            return f"⚪ {profit_abs:.2f} USDC"

    def get_open_trades_message(self) -> str:
        """Get formatted message for open trades"""
        data = self.get_freqtrade_data("status")

        if not data:
            return "❌ Δεν μπορώ να συνδεθώ στο Freqtrade API"

        trades = data.get('trades', [])

        if not trades:
            return "📊 **ΑΝΟΙΧΤΕΣ ΣΥΝΑΛΛΑΓΕΣ**\n\n✅ Δεν υπάρχουν ανοιχτές συναλλαγές"

        message = "📊 **ΑΝΟΙΧΤΕΣ ΣΥΝΑΛΛΑΓΕΣ**\n\n"

        for trade in trades:
            pair = trade.get('pair', 'N/A')
            profit_abs = trade.get('profit_abs', 0)
            profit_pct = trade.get('profit_pct', 0)
            open_date = trade.get('open_date', '')

            # Calculate time since open
            if open_date:
                try:
                    open_time = datetime.fromisoformat(open_date.replace('Z', '+00:00'))
                    time_diff = datetime.now() - open_time.replace(tzinfo=None)
                    hours = int(time_diff.total_seconds() // 3600)
                    minutes = int((time_diff.total_seconds() % 3600) // 60)
                    duration = f"{hours}h {minutes}m"
                except:
                    duration = "N/A"
            else:
                duration = "N/A"

            profit_str = self.format_profit_usdt(profit_abs)

            message += f"🔹 **{pair}**\n"
            message += f"   💰 {profit_str} ({profit_pct:.2f}%)\n"
            message += f"   ⏱️ Διάρκεια: {duration}\n\n"

        return message

    def get_recent_trades_message(self) -> str:
        """Get formatted message for recent closed trades"""
        data = self.get_freqtrade_data("trades")

        if not data:
            return "❌ Δεν μπορώ να συνδεθώ στο Freqtrade API"

        trades = data.get('trades', [])

        if not trades:
            return "📈 **ΠΡΌΣΦΑΤΕΣ ΣΥΝΑΛΛΑΓΕΣ**\n\n✅ Δεν υπάρχουν κλειστές συναλλαγές"

        # Get last 10 trades
        recent_trades = sorted(trades, key=lambda x: x.get('close_date', ''), reverse=True)[:10]

        message = "📈 **ΠΡΌΣΦΑΤΕΣ ΣΥΝΑΛΛΑΓΕΣ**\n\n"

        for trade in recent_trades:
            pair = trade.get('pair', 'N/A')
            profit_abs = trade.get('profit_abs', 0)
            profit_pct = trade.get('profit_pct', 0)
            close_date = trade.get('close_date', '')

            # Format close time
            if close_date:
                try:
                    close_time = datetime.fromisoformat(close_date.replace('Z', '+00:00'))
                    time_str = close_time.strftime('%H:%M')
                except:
                    time_str = "N/A"
            else:
                time_str = "N/A"

            profit_str = self.format_profit_usdt(profit_abs)

            message += f"🔹 **{pair}** ({time_str})\n"
            message += f"   💰 {profit_str} ({profit_pct:.2f}%)\n\n"

        return message

    def get_profit_summary_message(self) -> str:
        """Get formatted profit summary message"""
        # Get profit data
        profit_data = self.get_freqtrade_data("profit")
        balance_data = self.get_freqtrade_data("balance")

        if not profit_data:
            return "❌ Δεν μπορώ να συνδεθώ στο Freqtrade API"

        # Extract profit info
        profit_closed_coin = profit_data.get('profit_closed_coin', 0)
        profit_all_coin = profit_data.get('profit_all_coin', 0)
        trade_count = profit_data.get('trade_count', 0)
        winning_trades = profit_data.get('winning_trades', 0)
        losing_trades = profit_data.get('losing_trades', 0)

        # Calculate win rate
        win_rate = (winning_trades / max(trade_count, 1)) * 100

        # Get balance info
        total_balance = 0
        if balance_data and 'currencies' in balance_data:
            for currency in balance_data['currencies']:
                if currency.get('currency') == 'USDC':
                    total_balance = currency.get('total', 0)
                    break

        message = "💰 **ΣΥΝΟΨΗ ΚΕΡΔΩΝ**\n\n"
        message += f"🏆 Συνολικά κέρδη: **{self.format_profit_usdt(profit_closed_coin)}**\n"
        message += f"📊 Τρέχον κέρδος: **{self.format_profit_usdt(profit_all_coin)}**\n"
        message += f"💳 Υπόλοιπο: **{total_balance:.2f} USDC**\n\n"
        message += f"📈 Συναλλαγές: **{trade_count}**\n"
        message += f"✅ Κερδοφόρες: **{winning_trades}**\n"
        message += f"❌ Ζημιογόνες: **{losing_trades}**\n"
        message += f"🎯 Ποσοστό επιτυχίας: **{win_rate:.1f}%**\n"

        return message

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Ανοιχτές Συναλλαγές", callback_data="open_trades"),
                InlineKeyboardButton("📈 Πρόσφατες", callback_data="recent_trades")
            ],
            [
                InlineKeyboardButton("💰 Συνοψη Κερδών", callback_data="profit_summary"),
                InlineKeyboardButton("🔄 Ανανέωση", callback_data="refresh")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        welcome_message = (
            "🤖 **Live Trades Monitor**\n\n"
            "Καλώς ήρθες στον παρακολουθητή ζωντανών συναλλαγών!\n\n"
            "📊 Παρακολούθηση ανοιχτών θέσεων\n"
            "💰 Κέρδη σε USDC (όχι ποσοστά)\n"
            "📈 Πρόσφατες κλειστές συναλλαγές\n\n"
            "Επίλεξε μια επιλογή:"
        )

        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

    async def trades_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trades command"""
        message = self.get_open_trades_message()
        await update.message.reply_text(message, parse_mode='Markdown')

    async def profit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /profit command"""
        message = self.get_profit_summary_message()
        await update.message.reply_text(message, parse_mode='Markdown')

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()

        if query.data == "open_trades":
            message = self.get_open_trades_message()
        elif query.data == "recent_trades":
            message = self.get_recent_trades_message()
        elif query.data == "profit_summary":
            message = self.get_profit_summary_message()
        elif query.data == "refresh":
            message = "🔄 Ανανέωση δεδομένων...\n\n" + self.get_open_trades_message()
        else:
            message = "❌ Άγνωστη εντολή"

        # Update keyboard
        keyboard = [
            [
                InlineKeyboardButton("📊 Ανοιχτές", callback_data="open_trades"),
                InlineKeyboardButton("📈 Πρόσφατες", callback_data="recent_trades")
            ],
            [
                InlineKeyboardButton("💰 Κέρδη", callback_data="profit_summary"),
                InlineKeyboardButton("🔄 Ανανέωση", callback_data="refresh")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

    async def send_periodic_updates(self, context: ContextTypes.DEFAULT_TYPE):
        """Send periodic updates every 30 minutes"""
        if not self.chat_id:
            return

        message = "🔔 **Περιοδική Ενημέρωση**\n\n"
        message += self.get_open_trades_message()
        message += "\n" + self.get_profit_summary_message()

        try:
            await context.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error sending periodic update: {e}")

    def run(self):
        """Run the bot"""
        if not self.bot_token:
            logger.error("❌ Bot token not configured!")
            return

        logger.info("🚀 Starting Live Trades Telegram Bot...")

        # Create application
        application = Application.builder().token(self.bot_token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("trades", self.trades_command))
        application.add_handler(CommandHandler("profit", self.profit_command))
        application.add_handler(CallbackQueryHandler(self.button_callback))

        # Add periodic updates (every 30 minutes)
        job_queue = application.job_queue
        job_queue.run_repeating(self.send_periodic_updates, interval=1800, first=60)

        # Start bot
        logger.info("✅ Bot started successfully!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # Check environment variables
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("❌ Please set TELEGRAM_BOT_TOKEN environment variable")
        print("   export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        exit(1)

    if not os.getenv('TELEGRAM_CHAT_ID'):
        print("❌ Please set TELEGRAM_CHAT_ID environment variable")
        print("   export TELEGRAM_CHAT_ID='your_chat_id_here'")
        exit(1)

    bot = LiveTradesBot()
    bot.run()