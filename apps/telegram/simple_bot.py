#!/usr/bin/env python3
"""
🚀 Simple Telegram Bot για NFI5MOHO_WIP
Working version without complex dependencies
"""

import asyncio
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# Configuration
BOT_TOKEN = "7295982134:AAF242CTc3vVc9m0qBT3wcF0wljByhlptMQ"
CHAT_ID = 930268785

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/simple_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_system_info():
    """Get basic system information"""
    try:
        # Check if NFI5MOHO_WIP processes are running
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        nfi5moho_running = 'NFI5MOHO_WIP' in result.stdout

        # Check if FreqTrade API is accessible
        api_accessible = False
        try:
            import requests
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth('freqtrade', 'ruriu7AY')
            response = requests.get("http://localhost:8080/api/v1/status", auth=auth, timeout=5)
            api_accessible = response.status_code == 200
        except:
            pass

        # Check if Dashboard is running
        dashboard_running = False
        try:
            import requests
            response = requests.get("http://localhost:8500/api/system-status", timeout=5)
            dashboard_running = response.status_code == 200
        except:
            pass

        # Get basic system stats
        uptime_result = subprocess.run(['uptime'], capture_output=True, text=True)
        uptime = uptime_result.stdout.strip() if uptime_result.returncode == 0 else "Unknown"

        return {
            'nfi5moho_running': nfi5moho_running,
            'api_accessible': api_accessible,
            'dashboard_running': dashboard_running,
            'uptime': uptime,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {'error': str(e)}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    if update.message.chat_id != CHAT_ID:
        await update.message.reply_text("❌ Δεν έχεις δικαίωμα χρήσης!")
        return

    welcome_msg = """
🚀 **Enhanced Telegram Bot για NFI5MOHO_WIP**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **Bot Successfully Started!**

🎯 **Στρατηγική**: NFI5MOHO_WIP
🔧 **Λειτουργίες**:
• System monitoring
• Strategy status
• Basic controls

📱 **Διαθέσιμες Εντολές**:
• /help - Κύριο μενού
• /status - System status
• /nfi5moho - Strategy info

🇬🇷 **Καλώς ήρθες!**
    """

    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    if update.message.chat_id != CHAT_ID:
        await update.message.reply_text("❌ Δεν έχεις δικαίωμα χρήσης!")
        return

    help_msg = """
📋 **Κύριο Μενού - NFI5MOHO_WIP Bot**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Στρατηγική**: NFI5MOHO_WIP (Active)
⚡ **Status**: Online & Monitoring

🔧 **Διαθέσιμες Λειτουργίες**:
• System monitoring
• Strategy tracking
• Basic process control

💡 **Χρήσιμες Εντολές**:
• /status - Έλεγχος συστήματος
• /nfi5moho - Info στρατηγικής
• /help - Αυτό το μενού

🇬🇷 **Όλα λειτουργούν κανονικά!**
    """

    keyboard = [
        [
            InlineKeyboardButton("📊 System Status", callback_data="system_status"),
            InlineKeyboardButton("🎯 NFI5MOHO Info", callback_data="nfi5moho_info")
        ],
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_menu"),
            InlineKeyboardButton("ℹ️ Bot Info", callback_data="bot_info")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(help_msg, reply_markup=reply_markup, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    if update.message.chat_id != CHAT_ID:
        await update.message.reply_text("❌ Δεν έχεις δικαίωμα χρήσης!")
        return

    system_info = get_system_info()

    if 'error' in system_info:
        status_msg = f"❌ *System Error*\n\n`{system_info['error']}`"
    else:
        nfi5moho_status = "🟢 Running" if system_info['nfi5moho_running'] else "🔴 Not Running"
        api_status = "🟢 Connected" if system_info['api_accessible'] else "🔴 Offline"
        dashboard_status = "🟢 Online" if system_info['dashboard_running'] else "🔴 Offline"

        status_msg = f"""
📊 *System Status Report*

🎯 *NFI5MOHO_WIP*: {nfi5moho_status}
🔗 *API Status*: {api_status}
🎛️ *Dashboard*: {dashboard_status}
⏰ *System Uptime*: {system_info['uptime']}
🕐 *Last Check*: {system_info['timestamp']}

✅ *Bot Status*: Online & Monitoring
🔄 *Auto-refresh*: Active

🎛️ Dashboard: http://localhost:8500
        """

    keyboard = [
        [
            InlineKeyboardButton("🔄 Refresh Status", callback_data="system_status"),
            InlineKeyboardButton("🎛️ Dashboard", callback_data="dashboard_link")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(status_msg, reply_markup=reply_markup, parse_mode='Markdown')

async def nfi5moho_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /nfi5moho command"""
    if update.message.chat_id != CHAT_ID:
        await update.message.reply_text("❌ Δεν έχεις δικαίωμα χρήσης!")
        return

    nfi5moho_msg = """
🎯 **NFI5MOHO_WIP Strategy Info**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Strategy Details**:
• Name: NFI5MOHO_WIP
• Type: NostalgiaForInfinityV5 + MultiOffsetLamboV0
• Timeframe: 5m
• Max Open Trades: 5
• Stake Amount: 50 USDC

🔧 **Features**:
• 21 buy conditions
• 8 sell conditions
• Multi-offset indicators
• Protection mechanisms
• Optimized parameters

📈 **Monitoring**:
• Real-time status tracking
• Performance monitoring
• System integration
• Telegram notifications

💡 **Commands**:
• /status - Check system status
• /help - Full command list
    """

    keyboard = [
        [
            InlineKeyboardButton("📊 Check Status", callback_data="system_status"),
            InlineKeyboardButton("🔄 Refresh Info", callback_data="nfi5moho_info")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(nfi5moho_msg, reply_markup=reply_markup, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "system_status":
        system_info = get_system_info()

        if 'error' in system_info:
            status_msg = f"❌ *System Error*\n\n`{system_info['error']}`"
        else:
            nfi5moho_status = "🟢 Running" if system_info['nfi5moho_running'] else "🔴 Not Running"
            api_status = "🟢 Connected" if system_info['api_accessible'] else "🔴 Offline"
            dashboard_status = "🟢 Online" if system_info['dashboard_running'] else "🔴 Offline"

            status_msg = f"""
📊 *System Status Report*

🎯 *NFI5MOHO_WIP*: {nfi5moho_status}
🔗 *API Status*: {api_status}
🎛️ *Dashboard*: {dashboard_status}
⏰ *System Uptime*: {system_info['uptime']}
🕐 *Last Check*: {system_info['timestamp']}

✅ *Bot Status*: Online & Monitoring
🔄 *Auto-refresh*: Active

🎛️ Dashboard: http://localhost:8500
            """

        keyboard = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="system_status"),
                InlineKeyboardButton("🎛️ Dashboard", url="http://localhost:8500")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="refresh_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(status_msg, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "nfi5moho_info":
        nfi5moho_msg = """
🎯 **NFI5MOHO_WIP Strategy Info**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Strategy Details**:
• Name: NFI5MOHO_WIP
• Type: NostalgiaForInfinityV5 + MultiOffsetLamboV0
• Timeframe: 5m
• Max Open Trades: 5
• Stake Amount: 50 USDC

🔧 **Features**:
• 21 buy conditions
• 8 sell conditions
• Multi-offset indicators
• Protection mechanisms
• Optimized parameters

📈 **Monitoring**:
• Real-time status tracking
• Performance monitoring
• System integration
• Telegram notifications
        """

        keyboard = [
            [InlineKeyboardButton("📊 Check Status", callback_data="system_status")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="refresh_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(nfi5moho_msg, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "refresh_menu":
        await help_command(update, context)

    elif data == "bot_info":
        bot_info_msg = """
ℹ️ **Bot Information**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 **Bot Name**: NFI5MOHO_WIP Telegram Bot
📱 **Version**: 1.0 (Simple)
🎯 **Purpose**: Strategy monitoring & control
🇬🇷 **Language**: Greek + English

🔧 **Features**:
• System status monitoring
• Strategy information
• Real-time updates
• Simple & reliable

✅ **Status**: Fully operational
        """

        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="refresh_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(bot_info_msg, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "dashboard_link":
        dashboard_msg = """
🎛️ **Dashboard Access**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Unified Master Dashboard**
🌐 **URL**: http://localhost:8500

🔧 **Features**:
• System Status Monitoring
• Strategy Conditions Monitor (22 pairs)
• Portfolio Analytics & Performance
• Celebrity News Monitoring 🌟
• Market Sentiment Analysis 📈
• Risk Management Metrics ⚠️
• Trading Signals Generator 🚀
• Auto Trading Controls 🤖

💡 **Tip**: Ανοίξτε το link σε browser για πλήρη πρόσβαση
        """

        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="refresh_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(dashboard_msg, reply_markup=reply_markup, parse_mode='Markdown')

    else:
        await query.edit_message_text("🔧 Αυτή η λειτουργία είναι υπό ανάπτυξη...",
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Πίσω", callback_data="refresh_menu")]]))

def main():
    """Main function to run the bot"""
    print("🚀 Starting Simple Telegram Bot για NFI5MOHO_WIP...")
    print("🤖 Bot Token configured")
    print("📊 Strategy: NFI5MOHO_WIP")
    print("🔧 Features: Basic monitoring & control")
    print("🇬🇷 Interface: Greek + English")
    print()

    # Create application (simple version without job queue issues)
    application = Application.builder().token(BOT_TOKEN).job_queue(None).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("nfi5moho", nfi5moho_command))

    # Add callback handler
    application.add_handler(CallbackQueryHandler(button_callback))

    # Set bot commands
    commands = [
        BotCommand("start", "🚀 Ξεκίνα το bot"),
        BotCommand("help", "📋 Εμφάνιση μενού"),
        BotCommand("status", "📊 System status"),
        BotCommand("nfi5moho", "🎯 Strategy info"),
    ]

    # Run the bot
    try:
        print("✅ Bot starting...")

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