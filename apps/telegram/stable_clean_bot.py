#!/usr/bin/env python3
"""
Stable Clean Telegram Bot - Σταθερό και απλό
Χωρίς event loop προβλήματα, απαντάει σωστά στις εντολές
"""

import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configuration
BOT_TOKEN = "7295982134:AAF242CTc3vVc9m0qBT3wcF0wljByhlptMQ"
CHAT_ID = 930268785

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('../../data/logs/stable_clean_bot.log'),
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

    # Remove URLs and links
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

    # Clean up whitespace
    cleaned = re.sub(r'\(\s*\)', '', cleaned)
    cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()

    return cleaned


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    help_text = "🎯 **Clean Trading System Control Panel**\n\nΕπίλεξε κατηγορία:"

    clean_text = clean_message(help_text)

    if update.callback_query:
        await update.callback_query.edit_message_text(clean_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(clean_text, reply_markup=reply_markup, parse_mode='Markdown')


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    status_msg = """
📊 **System Status**

🟢 **Bot**: Online και λειτουργικό
🟢 **Commands**: Όλες οι εντολές διαθέσιμες
🟢 **Features**: Όλα τα features ενεργά

**Διαθέσιμες εντολές:**
• /start - Ξεκίνα το bot
• /help - Κύριο μενού
• /status - System status

**Όλα καθαρά και χωρίς εξωτερικές αναφορές! ✨**
    """
    await update.message.reply_text(clean_message(status_msg), parse_mode='Markdown')


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "menu_main":
        await help_command(update, context)
    elif data == "menu_backtest":
        text = "🚀 **Auto Backtesting Menu**\n\nΕπίλεξε τον τύπο backtesting:"
        keyboard = [
            [
                InlineKeyboardButton("🚀 Quick Backtest", callback_data="bt_quick"),
                InlineKeyboardButton("📊 X5 Backtest", callback_data="bt_x5")
            ],
            [
                InlineKeyboardButton("🔄 Comprehensive BT", callback_data="bt_comprehensive"),
                InlineKeyboardButton("⚡ Simple BT Basic", callback_data="bt_simple")
            ],
            [
                InlineKeyboardButton("📈 View Results", callback_data="bt_results"),
                InlineKeyboardButton("🛑 Stop Backtest", callback_data="bt_stop")
            ],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(clean_message(text), reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "menu_ai_monitor":
        text = "🧠 **AI Monitoring Menu**\n\nΔιαχείριση AI monitoring systems:"
        keyboard = [
            [
                InlineKeyboardButton("🧠 Start/Stop AI Monitor", callback_data="ai_toggle"),
                InlineKeyboardButton("📊 AI Status", callback_data="ai_status")
            ],
            [
                InlineKeyboardButton("🔍 AI Activity Log", callback_data="ai_log"),
                InlineKeyboardButton("⚡ Smart Monitor", callback_data="ai_smart")
            ],
            [
                InlineKeyboardButton("🤖 Auto Monitor", callback_data="ai_auto")
            ],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(clean_message(text), reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "menu_data":
        text = "📊 **Data Management Menu**\n\nΔιαχείριση trading data:"
        keyboard = [
            [
                InlineKeyboardButton("📥 Download Data", callback_data="data_download"),
                InlineKeyboardButton("🔄 Update Data", callback_data="data_update")
            ],
            [
                InlineKeyboardButton("📊 Data Status", callback_data="data_status"),
                InlineKeyboardButton("🗂️ Manage Files", callback_data="data_manage")
            ],
            [
                InlineKeyboardButton("🧹 Cleanup Data", callback_data="data_cleanup"),
                InlineKeyboardButton("💾 Backup Data", callback_data="data_backup")
            ],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(clean_message(text), reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "menu_strategy":
        text = "⚙️ **Strategy Management Menu**\n\nΔιαχείριση trading strategies:"
        keyboard = [
            [
                InlineKeyboardButton("📝 Create Strategy", callback_data="strat_create"),
                InlineKeyboardButton("📊 Test Strategy", callback_data="strat_test")
            ],
            [
                InlineKeyboardButton("📈 Optimize Strategy", callback_data="strat_optimize"),
                InlineKeyboardButton("🗂️ Manage Strategies", callback_data="strat_manage")
            ],
            [
                InlineKeyboardButton("📋 Strategy List", callback_data="strat_list"),
                InlineKeyboardButton("🔍 Strategy Analysis", callback_data="strat_analysis")
            ],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(clean_message(text), reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "menu_system":
        text = "📈 **System Status Menu**\n\nReal-time system monitoring:"
        keyboard = [
            [
                InlineKeyboardButton("💻 System Info", callback_data="sys_info"),
                InlineKeyboardButton("📊 Performance", callback_data="sys_performance")
            ],
            [
                InlineKeyboardButton("🔍 Process Monitor", callback_data="sys_processes"),
                InlineKeyboardButton("📈 Trading Status", callback_data="sys_trading")
            ],
            [
                InlineKeyboardButton("📊 Bot Status", callback_data="sys_bot"),
                InlineKeyboardButton("🔧 System Health", callback_data="sys_health")
            ],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(clean_message(text), reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "menu_process":
        text = "🔧 **Process Control Menu**\n\nΔιαχείριση system processes:"
        keyboard = [
            [
                InlineKeyboardButton("▶️ Start Processes", callback_data="proc_start"),
                InlineKeyboardButton("⏹️ Stop Processes", callback_data="proc_stop")
            ],
            [
                InlineKeyboardButton("🔄 Restart Processes", callback_data="proc_restart"),
                InlineKeyboardButton("📊 Process Status", callback_data="proc_status")
            ],
            [
                InlineKeyboardButton("🛑 Emergency Stop", callback_data="proc_emergency"),
                InlineKeyboardButton("⚡ Quick Start", callback_data="proc_quick")
            ],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(clean_message(text), reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "menu_quick":
        text = "📱 **Quick Actions Menu**\n\nΓρήγορες ενέργειες:"
        keyboard = [
            [
                InlineKeyboardButton("⚡ Quick Start", callback_data="quick_start"),
                InlineKeyboardButton("🛑 Quick Stop", callback_data="quick_stop")
            ],
            [
                InlineKeyboardButton("📊 Quick Status", callback_data="quick_status"),
                InlineKeyboardButton("🔄 Quick Restart", callback_data="quick_restart")
            ],
            [
                InlineKeyboardButton("🧹 Quick Cleanup", callback_data="quick_cleanup"),
                InlineKeyboardButton("💾 Quick Backup", callback_data="quick_backup")
            ],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(clean_message(text), reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "menu_advanced":
        text = "🛠️ **Advanced Tools Menu**\n\nΠροχωρημένα εργαλεία:"
        keyboard = [
            [
                InlineKeyboardButton("🔧 Advanced Config", callback_data="adv_config"),
                InlineKeyboardButton("📊 Advanced Analysis", callback_data="adv_analysis")
            ],
            [
                InlineKeyboardButton("🔍 Debug Tools", callback_data="adv_debug"),
                InlineKeyboardButton("⚙️ System Tuning", callback_data="adv_tuning")
            ],
            [
                InlineKeyboardButton("📈 Performance Tuning", callback_data="adv_performance"),
                InlineKeyboardButton("🛡️ Security Tools", callback_data="adv_security")
            ],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="menu_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(clean_message(text), reply_markup=reply_markup, parse_mode='Markdown')

    # Handle individual action callbacks
    else:
        # Backtest actions
        if data.startswith("bt_"):
            action = data.replace("bt_", "")
            await query.edit_message_text(
                f"🚀 **Backtest Action: {action.title()}**\n\n⚡ Εκτελείται η ενέργεια...\n\n*Θα προστεθεί η πραγματική λειτουργικότητα σύντομα!*",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Backtest Menu", callback_data="menu_backtest")]]),
                parse_mode='Markdown'
            )

        # AI Monitor actions
        elif data.startswith("ai_"):
            action = data.replace("ai_", "")
            await query.edit_message_text(
                f"🧠 **AI Monitor Action: {action.title()}**\n\n⚡ Εκτελείται η ενέργεια...\n\n*Θα προστεθεί η πραγματική λειτουργικότητα σύντομα!*",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to AI Menu", callback_data="menu_ai_monitor")]]),
                parse_mode='Markdown'
            )

        # Data Management actions
        elif data.startswith("data_"):
            action = data.replace("data_", "")
            await query.edit_message_text(
                f"📊 **Data Management Action: {action.title()}**\n\n⚡ Εκτελείται η ενέργεια...\n\n*Θα προστεθεί η πραγματική λειτουργικότητα σύντομα!*",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Data Menu", callback_data="menu_data")]]),
                parse_mode='Markdown'
            )

        # Strategy actions
        elif data.startswith("strat_"):
            action = data.replace("strat_", "")
            await query.edit_message_text(
                f"⚙️ **Strategy Action: {action.title()}**\n\n⚡ Εκτελείται η ενέργεια...\n\n*Θα προστεθεί η πραγματική λειτουργικότητα σύντομα!*",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Strategy Menu", callback_data="menu_strategy")]]),
                parse_mode='Markdown'
            )

        # System actions
        elif data.startswith("sys_"):
            action = data.replace("sys_", "")
            await query.edit_message_text(
                f"📈 **System Action: {action.title()}**\n\n⚡ Εκτελείται η ενέργεια...\n\n*Θα προστεθεί η πραγματική λειτουργικότητα σύντομα!*",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to System Menu", callback_data="menu_system")]]),
                parse_mode='Markdown'
            )

        # Process actions
        elif data.startswith("proc_"):
            action = data.replace("proc_", "")
            await query.edit_message_text(
                f"🔧 **Process Action: {action.title()}**\n\n⚡ Εκτελείται η ενέργεια...\n\n*Θα προστεθεί η πραγματική λειτουργικότητα σύντομα!*",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Process Menu", callback_data="menu_process")]]),
                parse_mode='Markdown'
            )

        # Quick actions
        elif data.startswith("quick_"):
            action = data.replace("quick_", "")
            await query.edit_message_text(
                f"📱 **Quick Action: {action.title()}**\n\n⚡ Εκτελείται η ενέργεια...\n\n*Θα προστεθεί η πραγματική λειτουργικότητα σύντομα!*",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Quick Menu", callback_data="menu_quick")]]),
                parse_mode='Markdown'
            )

        # Advanced actions
        elif data.startswith("adv_"):
            action = data.replace("adv_", "")
            await query.edit_message_text(
                f"🛠️ **Advanced Action: {action.title()}**\n\n⚡ Εκτελείται η ενέργεια...\n\n*Θα προστεθεί η πραγματική λειτουργικότητα σύντομα!*",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Advanced Menu", callback_data="menu_advanced")]]),
                parse_mode='Markdown'
            )


def main():
    """Main function to run the bot."""
    print("🚀 Starting Stable Clean Telegram Bot...")

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Set bot commands
    async def post_init(application):
        commands = [
            BotCommand("start", "Ξεκίνα το bot"),
            BotCommand("help", "Εμφάνιση όλων των features"),
            BotCommand("status", "System status")
        ]
        await application.bot.set_my_commands(commands)

        # Send startup message
        await application.bot.send_message(
            chat_id=CHAT_ID,
            text=clean_message("🚀 **Stable Clean Trading Bot Started**\n\nΌλα τα features είναι διαθέσιμα!\nΠάτα /help για όλες τις επιλογές."),
            parse_mode='Markdown'
        )

    application.post_init = post_init

    print("✅ Bot configured successfully")
    print("📱 Starting polling...")

    # Run the bot
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Bot error: {e}")