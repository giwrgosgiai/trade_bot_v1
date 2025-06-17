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
        active_trades = 0
        try:
            import requests
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth('freqtrade', 'ruriu7AY')
            response = requests.get("http://localhost:8080/api/v1/status", auth=auth, timeout=5)
            if response.status_code == 200:
                api_accessible = True
                trades_data = response.json()
                active_trades = len(trades_data) if isinstance(trades_data, list) else 0
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
            'active_trades': active_trades,
            'uptime': uptime,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {'error': str(e)}

def get_trading_signals():
    """Get current trading signals and why bot is not trading"""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        auth = HTTPBasicAuth('freqtrade', 'ruriu7AY')

        # Get whitelist
        whitelist_response = requests.get("http://localhost:8080/api/v1/whitelist", auth=auth, timeout=5)
        if whitelist_response.status_code != 200:
            return {'error': 'Cannot access FreqTrade API'}

        whitelist = whitelist_response.json().get('whitelist', [])

        # Get current status
        status_response = requests.get("http://localhost:8080/api/v1/status", auth=auth, timeout=5)
        active_trades = []
        if status_response.status_code == 200:
            active_trades = status_response.json()

        # Get balance
        balance_response = requests.get("http://localhost:8080/api/v1/balance", auth=auth, timeout=5)
        balance_info = {}
        if balance_response.status_code == 200:
            balance_data = balance_response.json()
            for currency in balance_data.get('currencies', []):
                if currency['currency'] == 'USDC':
                    balance_info = {
                        'free': currency.get('free', 0),
                        'used': currency.get('used', 0),
                        'total': currency.get('balance', 0)
                    }
                    break

        # Check why not trading
        reasons = []
        if len(active_trades) >= 3:  # max_open_trades
            reasons.append("🚫 Max trades reached (3/3)")

        if balance_info.get('free', 0) < 50:  # minimum stake
            reasons.append(f"💰 Low balance: {balance_info.get('free', 0):.2f} USDC")

        if not whitelist:
            reasons.append("📋 Empty whitelist")

        # If no specific reasons, it's likely strategy conditions not met
        if not reasons and len(active_trades) < 3:
            reasons.append("📊 Strategy conditions not met for entry")

        return {
            'whitelist_count': len(whitelist),
            'active_trades': len(active_trades),
            'max_trades': 3,
            'balance': balance_info,
            'reasons_not_trading': reasons,
            'pairs_monitored': whitelist[:5],  # Show first 5 pairs
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }

    except Exception as e:
        logger.error(f"Error getting trading signals: {e}")
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
• System monitoring & control
• Trading information & stats
• Strategy analysis & performance
• Real-time dashboard access

💡 **Επιλέξτε μια κατηγορία παρακάτω**:
    """

    keyboard = [
        [
            InlineKeyboardButton("📊 System Status", callback_data="system_status"),
            InlineKeyboardButton("📈 Trading Info", callback_data="trading_menu")
        ],
        [
            InlineKeyboardButton("🎯 Trading Signals", callback_data="trading_signals"),
            InlineKeyboardButton("❓ Why No Trades?", callback_data="why_no_trades")
        ],
        [
            InlineKeyboardButton("💰 Profit & Stats", callback_data="profit_menu"),
            InlineKeyboardButton("🎯 Strategy Info", callback_data="strategy_menu")
        ],
        [
            InlineKeyboardButton("🎛️ Dashboard", callback_data="dashboard_link"),
            InlineKeyboardButton("⚙️ Controls", callback_data="controls_menu")
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
📈 *Active Trades*: {system_info['active_trades']}/3
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

    elif data == "trading_menu":
        trading_msg = """
📈 **Trading Information Menu**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💼 **Επιλέξτε πληροφορίες trading**:
        """

        keyboard = [
            [
                InlineKeyboardButton("📊 Current Status", callback_data="status_table"),
                InlineKeyboardButton("💼 Open Trades", callback_data="trades")
            ],
            [
                InlineKeyboardButton("💰 Balance", callback_data="balance"),
                InlineKeyboardButton("📈 Performance", callback_data="performance")
            ],
            [
                InlineKeyboardButton("📋 Recent Trades", callback_data="trades_recent"),
                InlineKeyboardButton("📊 Count", callback_data="count")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="refresh_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(trading_msg, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "profit_menu":
        profit_msg = """
💰 **Profit & Statistics Menu**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Επιλέξτε ανάλυση κερδών**:
        """

        keyboard = [
            [
                InlineKeyboardButton("💰 Total Profit", callback_data="profit"),
                InlineKeyboardButton("📊 Stats", callback_data="stats")
            ],
            [
                InlineKeyboardButton("📅 Daily", callback_data="daily"),
                InlineKeyboardButton("📅 Weekly", callback_data="weekly")
            ],
            [
                InlineKeyboardButton("📅 Monthly", callback_data="monthly"),
                InlineKeyboardButton("🎯 Mix Tags", callback_data="mix_tags")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="refresh_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(profit_msg, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "strategy_menu":
        strategy_msg = """
🎯 **Strategy Information Menu**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **Επιλέξτε πληροφορίες στρατηγικής**:
        """

        keyboard = [
            [
                InlineKeyboardButton("🎯 NFI5MOHO Info", callback_data="nfi5moho_info"),
                InlineKeyboardButton("📊 Buy Signals", callback_data="buys")
            ],
            [
                InlineKeyboardButton("📈 Sell Signals", callback_data="sells"),
                InlineKeyboardButton("🔄 Reload Config", callback_data="reload_config")
            ],
            [
                InlineKeyboardButton("📋 Logs", callback_data="logs"),
                InlineKeyboardButton("ℹ️ Version", callback_data="version")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="refresh_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(strategy_msg, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "controls_menu":
        controls_msg = """
⚙️ **Bot Controls Menu**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 **Επιλέξτε ενέργεια ελέγχου**:
        """

        keyboard = [
            [
                InlineKeyboardButton("🚀 Start Trading", callback_data="start_trading"),
                InlineKeyboardButton("🛑 Stop Trading", callback_data="stop_trading")
            ],
            [
                InlineKeyboardButton("🔄 Restart Bot", callback_data="restart_bot"),
                InlineKeyboardButton("🔧 Force Buy", callback_data="force_buy")
            ],
            [
                InlineKeyboardButton("💰 Force Sell", callback_data="force_sell"),
                InlineKeyboardButton("🛑 Emergency Stop", callback_data="emergency_stop")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="refresh_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(controls_msg, reply_markup=reply_markup, parse_mode='Markdown')

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

    elif data == "trading_signals":
        signals_info = get_trading_signals()

        if 'error' in signals_info:
            signals_msg = f"❌ *Trading Signals Error*\n\n`{signals_info['error']}`"
        else:
            pairs_text = ", ".join(signals_info['pairs_monitored']) if signals_info['pairs_monitored'] else "None"
            balance_text = f"{signals_info['balance'].get('free', 0):.2f} USDC" if signals_info['balance'] else "Unknown"

            signals_msg = f"""
🎯 *Trading Signals Monitor*

📊 *Current Status*:
• Active Trades: {signals_info['active_trades']}/{signals_info['max_trades']}
• Pairs Monitored: {signals_info['whitelist_count']}
• Available Balance: {balance_text}

📋 *Top Pairs*: {pairs_text}

⏰ *Last Update*: {signals_info['timestamp']}
            """

        keyboard = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="trading_signals"),
                InlineKeyboardButton("❓ Why No Trades?", callback_data="why_no_trades")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="refresh_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(signals_msg, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "why_no_trades":
        signals_info = get_trading_signals()

        if 'error' in signals_info:
            why_msg = f"❌ *Cannot Check Trading Status*\n\n`{signals_info['error']}`"
        else:
            reasons = signals_info['reasons_not_trading']
            if not reasons:
                reasons = ["✅ No specific issues found"]

            reasons_text = "\n".join([f"• {reason}" for reason in reasons])

            why_msg = f"""
❓ *Why Bot Is Not Trading*

🔍 *Analysis Results*:
{reasons_text}

📊 *Current Situation*:
• Active: {signals_info['active_trades']}/{signals_info['max_trades']} trades
• Balance: {signals_info['balance'].get('free', 0):.2f} USDC free
• Monitoring: {signals_info['whitelist_count']} pairs

💡 *Tips*:
- Strategy needs specific market conditions
- Bot waits for optimal entry signals
- Check if max trades reached
- Verify sufficient balance available

⏰ *Checked*: {signals_info['timestamp']}
            """

        keyboard = [
            [
                InlineKeyboardButton("🔄 Check Again", callback_data="why_no_trades"),
                InlineKeyboardButton("📊 View Signals", callback_data="trading_signals")
            ],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="refresh_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(why_msg, reply_markup=reply_markup, parse_mode='Markdown')

    # FreqTrade API Commands
    elif data in ["status_table", "trades", "balance", "performance", "trades_recent", "count",
                  "profit", "stats", "daily", "weekly", "monthly", "mix_tags", "buys", "sells",
                  "reload_config", "logs", "version", "start_trading", "stop_trading", "restart_bot",
                  "force_buy", "force_sell", "emergency_stop"]:

        # API call to FreqTrade
        result_msg = await execute_freqtrade_command(data)

        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data=data)],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="refresh_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(result_msg, reply_markup=reply_markup, parse_mode='Markdown')

    else:
        await query.edit_message_text("🔧 Αυτή η λειτουργία είναι υπό ανάπτυξη...",
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Πίσω", callback_data="refresh_menu")]]))

async def execute_freqtrade_command(command):
    """Execute FreqTrade API commands"""
    try:
        import requests
        from requests.auth import HTTPBasicAuth

        auth = HTTPBasicAuth('freqtrade', 'ruriu7AY')
        base_url = "http://localhost:8080/api/v1"

        # Map commands to API endpoints
        command_map = {
            'status_table': '/status',
            'trades': '/status',
            'balance': '/balance',
            'performance': '/performance',
            'trades_recent': '/trades',
            'count': '/count',
            'profit': '/profit',
            'stats': '/stats',
            'daily': '/daily',
            'weekly': '/weekly',
            'monthly': '/monthly',
            'mix_tags': '/mix_tags',
            'buys': '/buys',
            'sells': '/sells',
            'reload_config': '/reload_config',
            'logs': '/logs',
            'version': '/version',
            'start_trading': '/start',
            'stop_trading': '/stop',
            'restart_bot': '/restart',
            'force_buy': '/forcebuy',
            'force_sell': '/forcesell',
            'emergency_stop': '/stop'
        }

        endpoint = command_map.get(command, '/status')

        if command in ['start_trading', 'stop_trading', 'restart_bot', 'emergency_stop']:
            # POST commands
            response = requests.post(f"{base_url}{endpoint}", auth=auth, timeout=10)
        else:
            # GET commands
            response = requests.get(f"{base_url}{endpoint}", auth=auth, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Format response based on command
            if command == 'balance':
                return format_balance_response(data)
            elif command == 'status_table' or command == 'trades':
                return format_trades_response(data)
            elif command == 'profit':
                return format_profit_response(data)
            elif command == 'performance':
                return format_performance_response(data)
            else:
                return f"✅ **{command.replace('_', ' ').title()}**\n\n```{str(data)[:1000]}```"

        else:
            return f"❌ **API Error**\n\nStatus: {response.status_code}\nResponse: {response.text[:500]}"

    except Exception as e:
        return f"❌ **Connection Error**\n\n`{str(e)}`"

def format_balance_response(data):
    """Format balance API response"""
    try:
        total = data.get('total', 0)
        free = data.get('free', 0)
        used = data.get('used', 0)

        return f"""
💰 **Account Balance**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💼 **Total**: {total:.2f} USDC
💚 **Free**: {free:.2f} USDC
🔒 **Used**: {used:.2f} USDC

📊 **Usage**: {(used/total*100):.1f}% if total > 0 else 0%
        """
    except:
        return f"💰 **Balance**: {str(data)[:500]}"

def format_trades_response(data):
    """Format trades API response"""
    try:
        if not data:
            return "📊 **No Active Trades**\n\nΔεν υπάρχουν ενεργές συναλλαγές αυτή τη στιγμή."

        trades_text = "📊 **Active Trades**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        for i, trade in enumerate(data[:5]):  # Show max 5 trades
            pair = trade.get('pair', 'Unknown')
            profit = trade.get('profit_pct', 0)
            amount = trade.get('amount', 0)

            profit_icon = "🟢" if profit > 0 else "🔴" if profit < 0 else "⚪"

            trades_text += f"{profit_icon} **{pair}**\n"
            trades_text += f"   💰 Amount: {amount:.4f}\n"
            trades_text += f"   📈 Profit: {profit:.2f}%\n\n"

        if len(data) > 5:
            trades_text += f"... και {len(data)-5} ακόμη trades\n"

        return trades_text
    except:
        return f"📊 **Trades**: {str(data)[:500]}"

def format_profit_response(data):
    """Format profit API response"""
    try:
        profit_closed_coin = data.get('profit_closed_coin', 0)
        profit_closed_percent = data.get('profit_closed_percent', 0)
        trade_count = data.get('trade_count', 0)

        return f"""
💰 **Profit Summary**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💵 **Total Profit**: {profit_closed_coin:.2f} USDC
📈 **Profit %**: {profit_closed_percent:.2f}%
📊 **Total Trades**: {trade_count}

{'🟢 Profitable' if profit_closed_coin > 0 else '🔴 Loss' if profit_closed_coin < 0 else '⚪ Break Even'}
        """
    except:
        return f"💰 **Profit**: {str(data)[:500]}"

def format_performance_response(data):
    """Format performance API response"""
    try:
        if not data:
            return "📈 **No Performance Data**\n\nΔεν υπάρχουν δεδομένα performance."

        perf_text = "📈 **Performance by Pair**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        for pair_data in data[:10]:  # Show top 10
            pair = pair_data.get('pair', 'Unknown')
            profit = pair_data.get('profit', 0)
            count = pair_data.get('count', 0)

            profit_icon = "🟢" if profit > 0 else "🔴" if profit < 0 else "⚪"

            perf_text += f"{profit_icon} **{pair}**\n"
            perf_text += f"   💰 Profit: {profit:.2f} USDC\n"
            perf_text += f"   📊 Trades: {count}\n\n"

        return perf_text
    except:
        return f"📈 **Performance**: {str(data)[:500]}"

def main():
    """Main function to run the bot"""
    print("🚀 Starting Enhanced Telegram Bot για NFI5MOHO_WIP...")
    print("🤖 Bot Token configured")
    print("📊 Strategy: NFI5MOHO_WIP")
    print("🔧 Features: Full FreqTrade integration")
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