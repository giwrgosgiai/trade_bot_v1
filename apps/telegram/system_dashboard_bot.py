#!/usr/bin/env python3
"""
Telegram Bot για έλεγχο System Status Dashboard
Επιτρέπει έλεγχο και restart του dashboard από το Telegram
"""

import asyncio
import json
import requests
import subprocess
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Telegram Bot Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Αντικαταστήστε με το δικό σας token
ALLOWED_USERS = [123456789]  # Αντικαταστήστε με τα δικά σας Telegram user IDs

# Dashboard Configuration
DASHBOARD_URL = "http://localhost:8503"

class SystemDashboardBot:
    def __init__(self):
        self.dashboard_running = False

    def is_user_authorized(self, user_id: int) -> bool:
        """Έλεγχος αν ο χρήστης είναι εξουσιοδοτημένος"""
        return user_id in ALLOWED_USERS

    def check_dashboard_status(self) -> dict:
        """Έλεγχος κατάστασης dashboard"""
        try:
            response = requests.get(f"{DASHBOARD_URL}/api/status", timeout=5)
            if response.status_code == 200:
                return {
                    'running': True,
                    'data': response.json()
                }
            else:
                return {
                    'running': False,
                    'error': f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                'running': False,
                'error': str(e)
            }

    def start_dashboard(self) -> dict:
        """Εκκίνηση dashboard"""
        try:
            # Έλεγχος αν τρέχει ήδη
            result = subprocess.run(['lsof', '-i', ':8503'], capture_output=True, text=True)
            if result.returncode == 0:
                return {
                    'success': False,
                    'message': 'Το dashboard τρέχει ήδη'
                }

            # Εκκίνηση dashboard
            subprocess.Popen([
                'python3', 'apps/monitoring/system_status_dashboard.py'
            ], cwd='/home/giwrgosgiai')

            return {
                'success': True,
                'message': 'Το dashboard ξεκίνησε επιτυχώς'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Σφάλμα εκκίνησης: {str(e)}'
            }

    def stop_dashboard(self) -> dict:
        """Τερματισμός dashboard"""
        try:
            # Εύρεση και τερματισμός της διεργασίας
            result = subprocess.run([
                'pkill', '-f', 'system_status_dashboard.py'
            ], capture_output=True, text=True)

            return {
                'success': True,
                'message': 'Το dashboard σταμάτησε επιτυχώς'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Σφάλμα τερματισμού: {str(e)}'
            }

    def restart_dashboard(self) -> dict:
        """Επανεκκίνηση dashboard"""
        try:
            # Σταμάτημα
            self.stop_dashboard()

            # Περιμένουμε λίγο
            import time
            time.sleep(3)

            # Εκκίνηση
            return self.start_dashboard()
        except Exception as e:
            return {
                'success': False,
                'message': f'Σφάλμα επανεκκίνησης: {str(e)}'
            }

    def trigger_system_check(self) -> dict:
        """Εκκίνηση ελέγχου συστημάτων"""
        try:
            response = requests.post(f"{DASHBOARD_URL}/api/check", timeout=10)
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Ο έλεγχος συστημάτων ξεκίνησε'
                }
            else:
                return {
                    'success': False,
                    'message': f'Σφάλμα API: {response.status_code}'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Σφάλμα σύνδεσης: {str(e)}'
            }

# Global instance
dashboard_bot = SystemDashboardBot()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Εντολή /start"""
    user_id = update.effective_user.id

    if not dashboard_bot.is_user_authorized(user_id):
        await update.message.reply_text("❌ Δεν έχετε δικαίωμα χρήσης αυτού του bot.")
        return

    keyboard = [
        [
            InlineKeyboardButton("📊 Κατάσταση Dashboard", callback_data="status"),
            InlineKeyboardButton("🔍 Έλεγχος Συστημάτων", callback_data="check")
        ],
        [
            InlineKeyboardButton("🚀 Εκκίνηση Dashboard", callback_data="start"),
            InlineKeyboardButton("🛑 Τερματισμός Dashboard", callback_data="stop")
        ],
        [
            InlineKeyboardButton("🔄 Επανεκκίνηση Dashboard", callback_data="restart")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = """
🤖 **System Dashboard Control Bot**

Καλώς ήρθατε! Μπορείτε να ελέγχετε το System Status Dashboard από εδώ.

**Διαθέσιμες λειτουργίες:**
• 📊 Έλεγχος κατάστασης dashboard
• 🔍 Εκκίνηση ελέγχου συστημάτων
• 🚀 Εκκίνηση/Τερματισμός dashboard
• 🔄 Επανεκκίνηση dashboard

Πατήστε ένα από τα κουμπιά παρακάτω:
    """

    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Χειρισμός κουμπιών"""
    query = update.callback_query
    user_id = query.from_user.id

    if not dashboard_bot.is_user_authorized(user_id):
        await query.answer("❌ Δεν έχετε δικαίωμα χρήσης.")
        return

    await query.answer()

    action = query.data

    if action == "status":
        await handle_status_check(query)
    elif action == "check":
        await handle_system_check(query)
    elif action == "start":
        await handle_dashboard_start(query)
    elif action == "stop":
        await handle_dashboard_stop(query)
    elif action == "restart":
        await handle_dashboard_restart(query)

async def handle_status_check(query):
    """Χειρισμός ελέγχου κατάστασης"""
    await query.edit_message_text("🔍 Ελέγχω την κατάσταση του dashboard...")

    status = dashboard_bot.check_dashboard_status()

    if status['running']:
        data = status['data']

        # Δημιουργία μηνύματος κατάστασης
        if data.get('overall_status') == 'healthy':
            status_emoji = "✅"
            status_text = "Όλα τα συστήματα λειτουργούν κανονικά"
        elif data.get('overall_status') == 'warning':
            status_emoji = "⚠️"
            issues = data.get('issues', [])
            status_text = f"Βρέθηκαν {len(issues)} προβλήματα"
        else:
            status_emoji = "❌"
            status_text = "Υπάρχουν σοβαρά προβλήματα"

        # Στατιστικά bots
        bots_info = ""
        if 'bots' in data:
            running_bots = sum(1 for bot in data['bots'].values() if bot.get('status') == 'running')
            total_bots = len(data['bots'])
            bots_info = f"🤖 Bots: {running_bots}/{total_bots} τρέχουν\n"

        # Στατιστικά strategies
        strategies_info = ""
        if 'strategies' in data:
            total_strategies = sum(info.get('count', 0) for info in data['strategies'].values())
            strategies_info = f"🎯 Strategies: {total_strategies} αρχεία\n"

        # System resources
        system_info = ""
        if 'system' in data and 'memory' in data['system']:
            memory_usage = data['system']['memory'].get('usage_percent', 0)
            cpu_usage = data['system'].get('cpu_usage', 0)
            system_info = f"⚙️ CPU: {cpu_usage:.1f}%, Memory: {memory_usage}%\n"

        timestamp = ""
        if 'timestamp' in data:
            dt = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            timestamp = f"🕐 Τελευταίος έλεγχος: {dt.strftime('%H:%M:%S')}"

        message = f"""
{status_emoji} **Dashboard Status**

**Συνολική κατάσταση:** {status_text}

{bots_info}{strategies_info}{system_info}
{timestamp}

🌐 Dashboard: http://localhost:8503
        """

    else:
        message = f"""
❌ **Dashboard Offline**

Το dashboard δεν τρέχει ή δεν απαντά.

**Σφάλμα:** {status.get('error', 'Άγνωστο σφάλμα')}

Χρησιμοποιήστε το κουμπί "🚀 Εκκίνηση" για να το ξεκινήσετε.
        """

    # Κουμπιά
    keyboard = [
        [
            InlineKeyboardButton("🔄 Ανανέωση", callback_data="status"),
            InlineKeyboardButton("🔍 Έλεγχος Συστημάτων", callback_data="check")
        ],
        [
            InlineKeyboardButton("🏠 Αρχική", callback_data="home")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_system_check(query):
    """Χειρισμός ελέγχου συστημάτων"""
    await query.edit_message_text("🔍 Εκκινώ έλεγχο συστημάτων...")

    result = dashboard_bot.trigger_system_check()

    if result['success']:
        message = """
✅ **Έλεγχος Συστημάτων**

Ο έλεγχος ξεκίνησε επιτυχώς!

Περιμένετε 10-15 δευτερόλεπτα και ελέγξτε την κατάσταση για να δείτε τα αποτελέσματα.
        """
    else:
        message = f"""
❌ **Σφάλμα Ελέγχου**

{result['message']}

Βεβαιωθείτε ότι το dashboard τρέχει.
        """

    keyboard = [
        [
            InlineKeyboardButton("📊 Κατάσταση", callback_data="status"),
            InlineKeyboardButton("🏠 Αρχική", callback_data="home")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_dashboard_start(query):
    """Χειρισμός εκκίνησης dashboard"""
    await query.edit_message_text("🚀 Εκκινώ το dashboard...")

    result = dashboard_bot.start_dashboard()

    if result['success']:
        message = """
✅ **Dashboard Εκκίνηση**

Το dashboard ξεκίνησε επιτυχώς!

🌐 Διαθέσιμο στο: http://localhost:8503

Περιμένετε λίγα δευτερόλεπτα για πλήρη φόρτωση.
        """
    else:
        message = f"""
❌ **Σφάλμα Εκκίνησης**

{result['message']}
        """

    keyboard = [
        [
            InlineKeyboardButton("📊 Κατάσταση", callback_data="status"),
            InlineKeyboardButton("🏠 Αρχική", callback_data="home")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_dashboard_stop(query):
    """Χειρισμός τερματισμού dashboard"""
    await query.edit_message_text("🛑 Τερματίζω το dashboard...")

    result = dashboard_bot.stop_dashboard()

    if result['success']:
        message = """
✅ **Dashboard Τερματισμός**

Το dashboard σταμάτησε επιτυχώς.
        """
    else:
        message = f"""
❌ **Σφάλμα Τερματισμού**

{result['message']}
        """

    keyboard = [
        [
            InlineKeyboardButton("🚀 Εκκίνηση", callback_data="start"),
            InlineKeyboardButton("🏠 Αρχική", callback_data="home")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_dashboard_restart(query):
    """Χειρισμός επανεκκίνησης dashboard"""
    await query.edit_message_text("🔄 Κάνω επανεκκίνηση του dashboard...")

    result = dashboard_bot.restart_dashboard()

    if result['success']:
        message = """
✅ **Dashboard Επανεκκίνηση**

Το dashboard έκανε επανεκκίνηση επιτυχώς!

🌐 Διαθέσιμο στο: http://localhost:8503
        """
    else:
        message = f"""
❌ **Σφάλμα Επανεκκίνησης**

{result['message']}
        """

    keyboard = [
        [
            InlineKeyboardButton("📊 Κατάσταση", callback_data="status"),
            InlineKeyboardButton("🏠 Αρχική", callback_data="home")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Εντολή /status"""
    user_id = update.effective_user.id

    if not dashboard_bot.is_user_authorized(user_id):
        await update.message.reply_text("❌ Δεν έχετε δικαίωμα χρήσης αυτού του bot.")
        return

    # Προσομοίωση callback query για επαναχρησιμοποίηση κώδικα
    class MockQuery:
        def __init__(self, message):
            self.message = message

        async def edit_message_text(self, text, reply_markup=None, parse_mode=None):
            await self.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)

    mock_query = MockQuery(update.message)
    await handle_status_check(mock_query)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Εντολή /help"""
    help_text = """
🤖 **System Dashboard Control Bot**

**Διαθέσιμες εντολές:**
• `/start` - Εμφάνιση κύριου μενού
• `/status` - Έλεγχος κατάστασης dashboard
• `/help` - Εμφάνιση αυτής της βοήθειας

**Λειτουργίες:**
• 📊 Έλεγχος κατάστασης dashboard και συστημάτων
• 🔍 Εκκίνηση ελέγχου όλων των συστημάτων
• 🚀 Εκκίνηση dashboard
• 🛑 Τερματισμός dashboard
• 🔄 Επανεκκίνηση dashboard

**Τι είναι το System Status Dashboard:**
Είναι ένα web-based εργαλείο που ελέγχει:
• Trading Bots (Freqtrade)
• Databases (SQLite, JSON)
• Strategies (Python αρχεία)
• System Resources (CPU, Memory, Disk)
• Monitoring Services

🌐 Dashboard URL: http://localhost:8503
    """

    await update.message.reply_text(help_text, parse_mode='Markdown')

def main():
    """Κύρια συνάρτηση"""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Παρακαλώ ορίστε το BOT_TOKEN στο αρχείο")
        print("📝 Πάρτε token από: https://t.me/BotFather")
        return

    if ALLOWED_USERS == [123456789]:
        print("⚠️ Παρακαλώ ορίστε τα ALLOWED_USERS με τα δικά σας Telegram user IDs")
        print("💡 Στείλτε /start στο @userinfobot για να μάθετε το user ID σας")

    # Δημιουργία application
    application = Application.builder().token(BOT_TOKEN).build()

    # Προσθήκη handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 System Dashboard Telegram Bot ξεκινάει...")
    print("📱 Στείλτε /start στο bot για να ξεκινήσετε")

    # Εκκίνηση bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()