#!/usr/bin/env python3
"""
🤖 Enhanced Bot NFI5MOHO_WIP Controller
Telegram bot για έλεγχο του Enhanced Bot NFI5MOHO_WIP
"""

import asyncio
import logging
import os
import subprocess
import psutil
import requests
from datetime import datetime
from pathlib import Path

from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# Configuration
BOT_TOKEN = "7295982134:AAF242CTc3vVc9m0qBT3wcF0wljByhlptMQ"
AUTHORIZED_CHAT_ID = 930268785
FREQTRADE_API_URL = "http://localhost:8082/api/v1"
FREQTRADE_AUTH = ('freqtrade', 'ruriu7AY')
UNIFIED_DASHBOARD_URL = "http://localhost:8500"

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs', 'enhanced_bot_controller.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedBotController:
    """Controller για το Enhanced Bot NFI5MOHO_WIP"""

    @staticmethod
    def is_bot_running():
        """Ελέγχει αν το Enhanced Bot τρέχει"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'freqtrade' in cmdline and 'trade' in cmdline and 'NFI5MOHO_WIP' in cmdline:
                        return True, proc.info['pid']
            return False, None
        except Exception as e:
            logger.error(f"Error checking bot status: {e}")
            return False, None

    @staticmethod
    def get_bot_status():
        """Παίρνει detailed status του bot"""
        try:
            is_running, pid = EnhancedBotController.is_bot_running()

            # API status
            api_accessible = False
            open_trades = 0
            balance = 0

            if is_running:
                try:
                    response = requests.get(f"{FREQTRADE_API_URL}/status",
                                          auth=FREQTRADE_AUTH, timeout=5)
                    if response.status_code == 200:
                        api_accessible = True
                        trades_data = response.json()
                        open_trades = len(trades_data)

                        # Get balance
                        balance_response = requests.get(f"{FREQTRADE_API_URL}/balance",
                                                      auth=FREQTRADE_AUTH, timeout=5)
                        if balance_response.status_code == 200:
                            balance_data = balance_response.json()
                            balance = balance_data.get('total', 0)
                except:
                    pass

            # Monitoring status
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            monitor_enabled = Path(os.path.join(project_root, '.bot_monitor_enabled')).exists()

            # Dashboard status
            dashboard_accessible = False
            try:
                response = requests.get(f"{UNIFIED_DASHBOARD_URL}/api/system-status",
                                      timeout=5)
                if response.status_code == 200:
                    dashboard_accessible = True
            except:
                pass

            return {
                'is_running': is_running,
                'pid': pid,
                'api_accessible': api_accessible,
                'dashboard_accessible': dashboard_accessible,
                'open_trades': open_trades,
                'balance': balance,
                'monitor_enabled': monitor_enabled,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
            return {'error': str(e)}

    @staticmethod
    def start_bot():
        """Ξεκινάει το Enhanced Bot"""
        try:
            # Use direct path to avoid shell issues
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            cmd = [
                'python3', '-m', 'freqtrade', 'trade',
                '--config', os.path.join(project_root, 'user_data', 'config.json'),
                '--strategy', 'NFI5MOHO_WIP',
                '--logfile', os.path.join(project_root, 'logs', 'freqtrade.log')
            ]

            # Start process in background
            result = subprocess.Popen(
                cmd,
                cwd=project_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            # Wait a bit and check if it started
            import time
            time.sleep(5)
            is_running, pid = EnhancedBotController.is_bot_running()

            if is_running:
                return True, f"Enhanced Bot ξεκίνησε επιτυχώς! PID: {pid}"
            else:
                return False, f"Αποτυχία εκκίνησης. Process PID: {result.pid}"

        except Exception as e:
            return False, f"Σφάλμα εκκίνησης: {str(e)}"

    @staticmethod
    def stop_bot():
        """Σταματάει το Enhanced Bot"""
        try:
            is_running, pid = EnhancedBotController.is_bot_running()

            if not is_running:
                return True, "Το Enhanced Bot δεν τρέχει"

            # Graceful shutdown
            os.kill(pid, 15)  # SIGTERM

            # Wait and check
            import time
            time.sleep(3)

            # Force kill if still running
            try:
                os.kill(pid, 9)  # SIGKILL
            except:
                pass

            return True, f"Enhanced Bot σταμάτησε (PID: {pid})"

        except Exception as e:
            return False, f"Σφάλμα στο σταμάτημα: {str(e)}"

    @staticmethod
    def restart_bot():
        """Επανεκκινεί το Enhanced Bot"""
        try:
            # Stop first
            stop_success, stop_msg = EnhancedBotController.stop_bot()

            # Wait a bit
            import time
            time.sleep(2)

            # Start again
            start_success, start_msg = EnhancedBotController.start_bot()

            if start_success:
                return True, f"Enhanced Bot επανεκκινήθηκε επιτυχώς!\n{start_msg}"
            else:
                return False, f"Αποτυχία επανεκκίνησης:\nStop: {stop_msg}\nStart: {start_msg}"

        except Exception as e:
            return False, f"Σφάλμα επανεκκίνησης: {str(e)}"

    @staticmethod
    def get_recent_trades():
        """Παίρνει τις πρόσφατες συναλλαγές"""
        try:
            response = requests.get(f"{FREQTRADE_API_URL}/trades",
                                  auth=FREQTRADE_AUTH, timeout=10)
            if response.status_code == 200:
                trades = response.json()
                return trades[-5:]  # Last 5 trades
            return []
        except Exception as e:
            logger.error(f"Error getting trades: {e}")
            return []

    @staticmethod
    def get_profit_summary():
        """Παίρνει σύνοψη κερδών"""
        try:
            response = requests.get(f"{FREQTRADE_API_URL}/profit",
                                  auth=FREQTRADE_AUTH, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"Error getting profit: {e}")
            return {}

def check_authorization(update: Update) -> bool:
    """Ελέγχει αν ο χρήστης είναι εξουσιοδοτημένος"""
    return update.effective_chat.id == AUTHORIZED_CHAT_ID

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Εντολή /start"""
    if not check_authorization(update):
        await update.message.reply_text("❌ Δεν έχεις δικαίωμα χρήσης αυτού του bot!")
        return

    welcome_msg = """
🤖 **Enhanced Bot NFI5MOHO_WIP Controller**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Καλώς ήρθες! Αυτό το bot σου επιτρέπει να ελέγχεις το Enhanced Bot NFI5MOHO_WIP απευθείας από το Telegram.

🎯 **Διαθέσιμες Εντολές:**
• /help - Εμφάνιση μενού
• /status - Κατάσταση bot
• /start_bot - Εκκίνηση bot
• /stop_bot - Σταμάτημα bot
• /restart_bot - Επανεκκίνηση bot
• /trades - Πρόσφατες συναλλαγές
• /profit - Σύνοψη κερδών
• /monitor - Έλεγχος monitoring

Χρησιμοποίησε /help για το πλήρες μενού! 🚀
    """

    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Εντολή /help με interactive menu"""
    if not check_authorization(update):
        await update.message.reply_text("❌ Δεν έχεις δικαίωμα χρήσης αυτού του bot!")
        return

    keyboard = [
        [
            InlineKeyboardButton("📊 Status Bot", callback_data="status"),
            InlineKeyboardButton("🚀 Εκκίνηση", callback_data="start_bot")
        ],
        [
            InlineKeyboardButton("🛑 Σταμάτημα", callback_data="stop_bot"),
            InlineKeyboardButton("🔄 Επανεκκίνηση", callback_data="restart_bot")
        ],
        [
            InlineKeyboardButton("📈 Συναλλαγές", callback_data="trades"),
            InlineKeyboardButton("💰 Κέρδη", callback_data="profit")
        ],
        [
            InlineKeyboardButton("🔔 Monitoring", callback_data="monitoring"),
            InlineKeyboardButton("⚙️ Ρυθμίσεις", callback_data="settings")
        ],
        [
            InlineKeyboardButton("🔄 Ανανέωση", callback_data="refresh")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    help_msg = """
🤖 **Enhanced Bot NFI5MOHO_WIP Control Panel**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Επίλεξε μια ενέργεια από το παρακάτω μενού:

🎯 **Γρήγορες Ενέργειες:**
• 📊 **Status** - Δες την κατάσταση του bot
• 🚀 **Εκκίνηση** - Ξεκίνα το Enhanced Bot
• 🛑 **Σταμάτημα** - Σταμάτα το bot
• 🔄 **Επανεκκίνηση** - Restart το bot

📊 **Πληροφορίες:**
• 📈 **Συναλλαγές** - Δες τις πρόσφατες συναλλαγές
• 💰 **Κέρδη** - Σύνοψη κερδών/ζημιών

⚙️ **Διαχείριση:**
• 🔔 **Monitoring** - Έλεγχος alerts
• ⚙️ **Ρυθμίσεις** - Προχωρημένες ρυθμίσεις

Πάτησε ένα κουμπί για να ξεκινήσεις! 👇
    """

    await update.message.reply_text(help_msg, reply_markup=reply_markup, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Εντολή /status"""
    if not check_authorization(update):
        await update.message.reply_text("❌ Δεν έχεις δικαίωμα χρήσης αυτού του bot!")
        return

    status = EnhancedBotController.get_bot_status()

    if 'error' in status:
        await update.message.reply_text(f"❌ Σφάλμα: {status['error']}")
        return

    # Status icons
    bot_icon = "🟢" if status['is_running'] else "🔴"
    api_icon = "🟢" if status['api_accessible'] else "🔴"
    dashboard_icon = "🟢" if status.get('dashboard_accessible', False) else "🔴"
    monitor_icon = "🔔" if status['monitor_enabled'] else "🔕"

    status_msg = f"""
📊 *Enhanced Bot NFI5MOHO_WIP Status*

{bot_icon} *Bot Status*: {'RUNNING' if status['is_running'] else 'STOPPED'}
{api_icon} *API Status*: {'CONNECTED' if status['api_accessible'] else 'DISCONNECTED'}
{dashboard_icon} *Dashboard*: {'ONLINE' if status.get('dashboard_accessible', False) else 'OFFLINE'}
{monitor_icon} *Monitoring*: {'ENABLED' if status['monitor_enabled'] else 'DISABLED'}

📊 *Trading Info:*
• Open Trades: {status['open_trades']}
• Balance: {status['balance']:.2f} USDC
• PID: {status['pid'] if status['pid'] else 'N/A'}

⏰ Last Check: {datetime.now().strftime('%H:%M:%S')}

💡 Tip: Χρησιμοποίησε /help για περισσότερες επιλογές!
    """

    await update.message.reply_text(status_msg, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()

    if not check_authorization(update):
        await query.edit_message_text("❌ Δεν έχεις δικαίωμα χρήσης!")
        return

    data = query.data

    if data == "status":
        status = EnhancedBotController.get_bot_status()

        if 'error' in status:
            text = f"❌ **Σφάλμα Status**\n\n{status['error']}"
        else:
            bot_icon = "🟢" if status['is_running'] else "🔴"
            api_icon = "🟢" if status['api_accessible'] else "🔴"
            dashboard_icon = "🟢" if status.get('dashboard_accessible', False) else "🔴"
            monitor_icon = "🔔" if status['monitor_enabled'] else "🔕"

            text = f"""
📊 *Enhanced Bot NFI5MOHO_WIP Status*

{bot_icon} *Bot*: {'RUNNING' if status['is_running'] else 'STOPPED'}
{api_icon} *API*: {'CONNECTED' if status['api_accessible'] else 'OFFLINE'}
{dashboard_icon} *Dashboard*: {'ONLINE' if status.get('dashboard_accessible', False) else 'OFFLINE'}
{monitor_icon} *Alerts*: {'ON' if status['monitor_enabled'] else 'OFF'}

📊 *Trading:*
• Open Trades: {status['open_trades']}
• Balance: {status['balance']:.2f} USDC
• PID: {status['pid'] if status['pid'] else 'N/A'}

⏰ {datetime.now().strftime('%H:%M:%S')}
            """

        keyboard = [[InlineKeyboardButton("🔙 Πίσω στο Μενού", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "start_bot":
        await query.edit_message_text("🚀 **Ξεκινάω το Enhanced Bot...**\nΠεριμένετε...", parse_mode='Markdown')

        success, message = EnhancedBotController.start_bot()

        if success:
            text = f"✅ **Bot Ξεκίνησε Επιτυχώς!**\n\n{message}\n\n🎉 Το Enhanced Bot NFI5MOHO_WIP είναι τώρα ενεργό!"
        else:
            text = f"❌ **Αποτυχία Εκκίνησης**\n\n{message}\n\n💡 Δοκίμασε ξανά ή έλεγξε τα logs."

        keyboard = [
            [InlineKeyboardButton("📊 Έλεγχος Status", callback_data="status")],
            [InlineKeyboardButton("🔙 Πίσω στο Μενού", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "stop_bot":
        await query.edit_message_text("🛑 **Σταματάω το Enhanced Bot...**\nΠεριμένετε...", parse_mode='Markdown')

        success, message = EnhancedBotController.stop_bot()

        if success:
            text = f"✅ **Bot Σταμάτησε Επιτυχώς!**\n\n{message}\n\n🔕 Το Enhanced Bot NFI5MOHO_WIP είναι τώρα ανενεργό."
        else:
            text = f"❌ **Αποτυχία Σταματήματος**\n\n{message}\n\n💡 Δοκίμασε ξανά ή έλεγξε τα processes."

        keyboard = [
            [InlineKeyboardButton("📊 Έλεγχος Status", callback_data="status")],
            [InlineKeyboardButton("🔙 Πίσω στο Μενού", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "restart_bot":
        await query.edit_message_text("🔄 **Επανεκκινώ το Enhanced Bot...**\nΠεριμένετε...", parse_mode='Markdown')

        success, message = EnhancedBotController.restart_bot()

        if success:
            text = f"✅ **Bot Επανεκκινήθηκε Επιτυχώς!**\n\n{message}\n\n🔄 Το Enhanced Bot NFI5MOHO_WIP είναι ξανά ενεργό!"
        else:
            text = f"❌ **Αποτυχία Επανεκκίνησης**\n\n{message}\n\n💡 Δοκίμασε manual start/stop."

        keyboard = [
            [InlineKeyboardButton("📊 Έλεγχος Status", callback_data="status")],
            [InlineKeyboardButton("🔙 Πίσω στο Μενού", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "trades":
        trades = EnhancedBotController.get_recent_trades()

        if not trades:
            text = "📈 **Πρόσφατες Συναλλαγές**\n\n❌ Δεν βρέθηκαν συναλλαγές ή το API δεν είναι διαθέσιμο."
        else:
            text = "📈 **Πρόσφατες Συναλλαγές**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

            for i, trade in enumerate(trades, 1):
                pair = trade.get('pair', 'N/A')
                profit = trade.get('profit_abs', 0)
                profit_pct = trade.get('profit_ratio', 0) * 100 if trade.get('profit_ratio') else 0
                close_date = trade.get('close_date', 'Open')

                profit_icon = "🟢" if profit > 0 else "🔴" if profit < 0 else "⚪"

                if close_date != 'Open' and close_date:
                    try:
                        close_time = datetime.fromisoformat(close_date.replace('Z', '')).strftime('%H:%M')
                    except:
                        close_time = 'N/A'
                else:
                    close_time = 'Open'

                text += f"{i}. {profit_icon} **{pair}**\n"
                text += f"   💰 {profit:.2f} USDC ({profit_pct:+.2f}%)\n"
                text += f"   ⏰ {close_time}\n\n"

        keyboard = [[InlineKeyboardButton("🔙 Πίσω στο Μενού", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "profit":
        profit_data = EnhancedBotController.get_profit_summary()

        if not profit_data:
            text = "💰 **Σύνοψη Κερδών**\n\n❌ Δεν βρέθηκαν δεδομένα κερδών ή το API δεν είναι διαθέσιμο."
        else:
            total_profit = profit_data.get('profit_closed_coin', 0)
            profit_factor = profit_data.get('profit_factor', 0)
            winning_trades = profit_data.get('winning_trades', 0)
            losing_trades = profit_data.get('losing_trades', 0)
            total_trades = winning_trades + losing_trades
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

            profit_icon = "🟢" if total_profit > 0 else "🔴" if total_profit < 0 else "⚪"

            text = f"""
💰 **Σύνοψη Κερδών Enhanced Bot NFI5MOHO_WIP**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{profit_icon} **Συνολικό Κέρδος**: {total_profit:.2f} USDC

📊 **Στατιστικά:**
• **Συνολικές Συναλλαγές**: {total_trades}
• **Κερδοφόρες**: {winning_trades} 🟢
• **Ζημιογόνες**: {losing_trades} 🔴
• **Ποσοστό Επιτυχίας**: {win_rate:.1f}%
• **Profit Factor**: {profit_factor:.2f}

⏰ **Ενημέρωση**: {datetime.now().strftime('%H:%M:%S')}
            """

        keyboard = [[InlineKeyboardButton("🔙 Πίσω στο Μενού", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "monitoring":
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        monitor_enabled = Path(os.path.join(project_root, '.bot_monitor_enabled')).exists()

        text = f"""
🔔 **Monitoring & Alerts**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 **Telegram Alerts**: {'🔔 ENABLED' if monitor_enabled else '🔕 DISABLED'}

💡 **Τι κάνουν τα alerts:**
• Ειδοποιήσεις όταν το bot σταματάει
• Αυτόματη επανεκκίνηση
• Ειδοποιήσεις για προβλήματα
• Heartbeat messages

⚙️ **Έλεγχος Alerts:**
        """

        keyboard = [
            [
                InlineKeyboardButton("🔔 Ενεργοποίηση Alerts" if not monitor_enabled else "🔕 Απενεργοποίηση Alerts",
                                   callback_data="toggle_monitoring")
            ],
            [
                InlineKeyboardButton("🔙 Πίσω στο Μενού", callback_data="back_to_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "toggle_monitoring":
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        monitor_enabled = Path(os.path.join(project_root, '.bot_monitor_enabled')).exists()

        if monitor_enabled:
            # Disable monitoring
            try:
                os.remove(os.path.join(project_root, '.bot_monitor_enabled'))
                text = "🔕 **Alerts Απενεργοποιήθηκαν**\n\nΤα Telegram alerts είναι τώρα ανενεργά. Δεν θα λαμβάνεις ειδοποιήσεις."
            except:
                text = "❌ **Σφάλμα**\n\nΔεν μπόρεσα να απενεργοποιήσω τα alerts."
        else:
            # Enable monitoring
            try:
                Path(os.path.join(project_root, '.bot_monitor_enabled')).touch()
                text = "🔔 **Alerts Ενεργοποιήθηκαν**\n\nΤα Telegram alerts είναι τώρα ενεργά. Θα λαμβάνεις ειδοποιήσεις για το bot."
            except:
                text = "❌ **Σφάλμα**\n\nΔεν μπόρεσα να ενεργοποιήσω τα alerts."

        keyboard = [
            [InlineKeyboardButton("🔔 Monitoring Menu", callback_data="monitoring")],
            [InlineKeyboardButton("🔙 Πίσω στο Μενού", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "settings":
        text = """
⚙️ **Ρυθμίσεις Enhanced Bot**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Bot Configuration:**
• Strategy: NFI5MOHO_WIP_Enhanced
• Exchange: Binance
• Base Currency: USDC
• API Port: 8082

📊 **Dashboard:**
• 🎛️ Unified Dashboard: http://localhost:8500
• FreqTrade UI: http://localhost:8080

🔧 **Προχωρημένες Ρυθμίσεις:**
        """

        keyboard = [
            [
                InlineKeyboardButton("🎛️ Open Dashboard", url="http://localhost:8500"),
                InlineKeyboardButton("📊 FreqTrade UI", url="http://localhost:8080")
            ],
            [InlineKeyboardButton("🔙 Πίσω στο Μενού", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "refresh":
        await query.edit_message_text("🔄 **Ανανεώνω τα δεδομένα...**", parse_mode='Markdown')

        # Wait a moment then show the menu
        import asyncio
        await asyncio.sleep(1)

        # Recreate the help menu for callback queries
        keyboard = [
            [
                InlineKeyboardButton("📊 Status Bot", callback_data="status"),
                InlineKeyboardButton("🚀 Εκκίνηση", callback_data="start_bot")
            ],
            [
                InlineKeyboardButton("🛑 Σταμάτημα", callback_data="stop_bot"),
                InlineKeyboardButton("🔄 Επανεκκίνηση", callback_data="restart_bot")
            ],
            [
                InlineKeyboardButton("📈 Συναλλαγές", callback_data="trades"),
                InlineKeyboardButton("💰 Κέρδη", callback_data="profit")
            ],
            [
                InlineKeyboardButton("🔔 Monitoring", callback_data="monitoring"),
                InlineKeyboardButton("⚙️ Ρυθμίσεις", callback_data="settings")
            ],
            [
                InlineKeyboardButton("🔄 Ανανέωση", callback_data="refresh")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        help_msg = """
🤖 **Enhanced Bot NFI5MOHO_WIP Control Panel**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Επίλεξε μια ενέργεια από το παρακάτω μενού:

🎯 **Γρήγορες Ενέργειες:**
• 📊 **Status** - Δες την κατάσταση του bot
• 🚀 **Εκκίνηση** - Ξεκίνα το Enhanced Bot
• 🛑 **Σταμάτημα** - Σταμάτα το bot
• 🔄 **Επανεκκίνηση** - Restart το bot

📊 **Πληροφορίες:**
• 📈 **Συναλλαγές** - Δες τις πρόσφατες συναλλαγές
• 💰 **Κέρδη** - Σύνοψη κερδών/ζημιών

⚙️ **Διαχείριση:**
• 🔔 **Monitoring** - Έλεγχος alerts
• ⚙️ **Ρυθμίσεις** - Προχωρημένες ρυθμίσεις

Πάτησε ένα κουμπί για να ξεκινήσεις! 👇
        """

        await query.edit_message_text(help_msg, reply_markup=reply_markup, parse_mode='Markdown')

    elif data == "back_to_menu":
        # Recreate the help menu for callback queries
        keyboard = [
            [
                InlineKeyboardButton("📊 Status Bot", callback_data="status"),
                InlineKeyboardButton("🚀 Εκκίνηση", callback_data="start_bot")
            ],
            [
                InlineKeyboardButton("🛑 Σταμάτημα", callback_data="stop_bot"),
                InlineKeyboardButton("🔄 Επανεκκίνηση", callback_data="restart_bot")
            ],
            [
                InlineKeyboardButton("📈 Συναλλαγές", callback_data="trades"),
                InlineKeyboardButton("💰 Κέρδη", callback_data="profit")
            ],
            [
                InlineKeyboardButton("🔔 Monitoring", callback_data="monitoring"),
                InlineKeyboardButton("⚙️ Ρυθμίσεις", callback_data="settings")
            ],
            [
                InlineKeyboardButton("🔄 Ανανέωση", callback_data="refresh")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        help_msg = """
🤖 **Enhanced Bot NFI5MOHO_WIP Control Panel**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Επίλεξε μια ενέργεια από το παρακάτω μενού:

🎯 **Γρήγορες Ενέργειες:**
• 📊 **Status** - Δες την κατάσταση του bot
• 🚀 **Εκκίνηση** - Ξεκίνα το Enhanced Bot
• 🛑 **Σταμάτημα** - Σταμάτα το bot
• 🔄 **Επανεκκίνηση** - Restart το bot

📊 **Πληροφορίες:**
• 📈 **Συναλλαγές** - Δες τις πρόσφατες συναλλαγές
• 💰 **Κέρδη** - Σύνοψη κερδών/ζημιών

⚙️ **Διαχείριση:**
• 🔔 **Monitoring** - Έλεγχος alerts
• ⚙️ **Ρυθμίσεις** - Προχωρημένες ρυθμίσεις

Πάτησε ένα κουμπί για να ξεκινήσεις! 👇
        """

        await query.edit_message_text(help_msg, reply_markup=reply_markup, parse_mode='Markdown')

async def start_bot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Εντολή /start_bot"""
    if not check_authorization(update):
        await update.message.reply_text("❌ Δεν έχεις δικαίωμα χρήσης αυτού του bot!")
        return

    await update.message.reply_text("🚀 **Ξεκινάω το Enhanced Bot...**\nΠεριμένετε...", parse_mode='Markdown')

    success, message = EnhancedBotController.start_bot()

    if success:
        text = f"✅ **Bot Ξεκίνησε Επιτυχώς!**\n\n{message}\n\n🎉 Το Enhanced Bot NFI5MOHO_WIP είναι τώρα ενεργό!"
    else:
        text = f"❌ **Αποτυχία Εκκίνησης**\n\n{message}\n\n💡 Δοκίμασε ξανά ή έλεγξε τα logs."

    await update.message.reply_text(text, parse_mode='Markdown')

async def stop_bot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Εντολή /stop_bot"""
    if not check_authorization(update):
        await update.message.reply_text("❌ Δεν έχεις δικαίωμα χρήσης αυτού του bot!")
        return

    await update.message.reply_text("🛑 **Σταματάω το Enhanced Bot...**\nΠεριμένετε...", parse_mode='Markdown')

    success, message = EnhancedBotController.stop_bot()

    if success:
        text = f"✅ **Bot Σταμάτησε Επιτυχώς!**\n\n{message}\n\n🔕 Το Enhanced Bot NFI5MOHO_WIP είναι τώρα ανενεργό."
    else:
        text = f"❌ **Αποτυχία Σταματήματος**\n\n{message}\n\n💡 Δοκίμασε ξανά ή έλεγξε τα processes."

    await update.message.reply_text(text, parse_mode='Markdown')

async def restart_bot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Εντολή /restart_bot"""
    if not check_authorization(update):
        await update.message.reply_text("❌ Δεν έχεις δικαίωμα χρήσης αυτού του bot!")
        return

    await update.message.reply_text("🔄 **Επανεκκινώ το Enhanced Bot...**\nΠεριμένετε...", parse_mode='Markdown')

    success, message = EnhancedBotController.restart_bot()

    if success:
        text = f"✅ **Bot Επανεκκινήθηκε Επιτυχώς!**\n\n{message}\n\n🔄 Το Enhanced Bot NFI5MOHO_WIP είναι ξανά ενεργό!"
    else:
        text = f"❌ **Αποτυχία Επανεκκίνησης**\n\n{message}\n\n💡 Δοκίμασε manual start/stop."

    await update.message.reply_text(text, parse_mode='Markdown')

async def trades_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Εντολή /trades"""
    if not check_authorization(update):
        await update.message.reply_text("❌ Δεν έχεις δικαίωμα χρήσης αυτού του bot!")
        return

    trades = EnhancedBotController.get_recent_trades()

    if not trades:
        text = "📈 **Πρόσφατες Συναλλαγές**\n\n❌ Δεν βρέθηκαν συναλλαγές ή το API δεν είναι διαθέσιμο."
    else:
        text = "📈 **Πρόσφατες Συναλλαγές**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        for i, trade in enumerate(trades, 1):
            pair = trade.get('pair', 'N/A')
            profit = trade.get('profit_abs', 0)
            profit_pct = trade.get('profit_ratio', 0) * 100 if trade.get('profit_ratio') else 0
            close_date = trade.get('close_date', 'Open')

            profit_icon = "🟢" if profit > 0 else "🔴" if profit < 0 else "⚪"

            if close_date != 'Open' and close_date:
                try:
                    close_time = datetime.fromisoformat(close_date.replace('Z', '')).strftime('%H:%M')
                except:
                    close_time = 'N/A'
            else:
                close_time = 'Open'

            text += f"{i}. {profit_icon} **{pair}**\n"
            text += f"   💰 {profit:.2f} USDC ({profit_pct:+.2f}%)\n"
            text += f"   ⏰ {close_time}\n\n"

    await update.message.reply_text(text, parse_mode='Markdown')

async def profit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Εντολή /profit"""
    if not check_authorization(update):
        await update.message.reply_text("❌ Δεν έχεις δικαίωμα χρήσης αυτού του bot!")
        return

    profit_data = EnhancedBotController.get_profit_summary()

    if not profit_data:
        text = "💰 **Σύνοψη Κερδών**\n\n❌ Δεν βρέθηκαν δεδομένα κερδών ή το API δεν είναι διαθέσιμο."
    else:
        total_profit = profit_data.get('profit_closed_coin', 0)
        profit_factor = profit_data.get('profit_factor', 0)
        winning_trades = profit_data.get('winning_trades', 0)
        losing_trades = profit_data.get('losing_trades', 0)
        total_trades = winning_trades + losing_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        profit_icon = "🟢" if total_profit > 0 else "🔴" if total_profit < 0 else "⚪"

        text = f"""
💰 **Σύνοψη Κερδών Enhanced Bot NFI5MOHO_WIP**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{profit_icon} **Συνολικό Κέρδος**: {total_profit:.2f} USDC

📊 **Στατιστικά:**
• **Συνολικές Συναλλαγές**: {total_trades}
• **Κερδοφόρες**: {winning_trades} 🟢
• **Ζημιογόνες**: {losing_trades} 🔴
• **Ποσοστό Επιτυχίας**: {win_rate:.1f}%
• **Profit Factor**: {profit_factor:.2f}

⏰ **Ενημέρωση**: {datetime.now().strftime('%H:%M:%S')}
        """

    await update.message.reply_text(text, parse_mode='Markdown')

async def monitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Εντολή /monitor"""
    if not check_authorization(update):
        await update.message.reply_text("❌ Δεν έχεις δικαίωμα χρήσης αυτού του bot!")
        return

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    monitor_enabled = Path(os.path.join(project_root, '.bot_monitor_enabled')).exists()

    text = f"""
🔔 **Monitoring & Alerts**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 **Telegram Alerts**: {'🔔 ENABLED' if monitor_enabled else '🔕 DISABLED'}

💡 **Τι κάνουν τα alerts:**
• Ειδοποιήσεις όταν το bot σταματάει
• Αυτόματη επανεκκίνηση
• Ειδοποιήσεις για προβλήματα
• Heartbeat messages

⚙️ **Έλεγχος:**
• Για να ενεργοποιήσεις: touch ~/.bot_monitor_enabled
• Για να απενεργοποιήσεις: rm ~/.bot_monitor_enabled
    """

    await update.message.reply_text(text, parse_mode='Markdown')

async def setup_bot_commands(application):
    """Ρύθμιση των εντολών του bot"""
    commands = [
        BotCommand("start", "Ξεκίνημα bot controller"),
        BotCommand("help", "Εμφάνιση μενού"),
        BotCommand("status", "Κατάσταση Enhanced Bot"),
        BotCommand("start_bot", "Εκκίνηση Enhanced Bot"),
        BotCommand("stop_bot", "Σταμάτημα Enhanced Bot"),
        BotCommand("restart_bot", "Επανεκκίνηση Enhanced Bot"),
        BotCommand("trades", "Πρόσφατες συναλλαγές"),
        BotCommand("profit", "Σύνοψη κερδών"),
        BotCommand("monitor", "Έλεγχος monitoring")
    ]

    await application.bot.set_my_commands(commands)

def main():
    """Main function"""
    try:
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()

        # Add error handler
        async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
            """Log the error and send a telegram message to notify the developer."""
            logger.error(f"Exception while handling an update: {context.error}")

        application.add_error_handler(error_handler)

        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("start_bot", start_bot_command))
        application.add_handler(CommandHandler("stop_bot", stop_bot_command))
        application.add_handler(CommandHandler("restart_bot", restart_bot_command))
        application.add_handler(CommandHandler("trades", trades_command))
        application.add_handler(CommandHandler("profit", profit_command))
        application.add_handler(CommandHandler("monitor", monitor_command))
        application.add_handler(CallbackQueryHandler(button_callback))

        # Setup commands
        application.job_queue.run_once(
            lambda context: asyncio.create_task(setup_bot_commands(application)),
            when=1
        )

        # Start the bot
        logger.info("🚀 Enhanced Bot NFI5MOHO_WIP Controller ξεκινάει...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.error(f"Critical error starting bot: {e}")
        raise

if __name__ == "__main__":
    main()