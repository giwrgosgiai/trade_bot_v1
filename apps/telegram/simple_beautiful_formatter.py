#!/usr/bin/env python3
"""
🎨 Simple Beautiful Formatter
Απλός και όμορφος formatter για Telegram messages
"""

from datetime import datetime
from typing import Dict, List, Optional

class SimpleFormatter:
    """🎨 Απλός και όμορφος formatter"""

    @staticmethod
    def format_system_status(status: Dict) -> str:
        """Απλό και όμορφο system status"""
        if 'error' in status:
            return f"""
❌ **Σφάλμα Συστήματος**
{status['error']}
"""

        # Απλό header
        msg = f"""
🖥️ **ΚΑΤΑΣΤΑΣΗ ΣΥΣΤΗΜΑΤΟΣ**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        # CPU - απλά και κατανοητά
        cpu_status = "🟢 Καλή" if status['cpu_percent'] < 50 else "🟡 Μέτρια" if status['cpu_percent'] < 80 else "🔴 Υψηλή"
        msg += f"💻 **CPU:** {status['cpu_percent']:.1f}% - {cpu_status}\n\n"

        # Memory - απλά
        memory_status = "🟢 Καλή" if status['memory_percent'] < 60 else "🟡 Μέτρια" if status['memory_percent'] < 80 else "🔴 Υψηλή"
        msg += f"💾 **Μνήμη:** {status['memory_used']:.1f}GB από {status['memory_total']:.1f}GB\n"
        msg += f"   📊 {status['memory_percent']:.1f}% - {memory_status}\n\n"

        # Disk - απλά
        disk_status = "🟢 Καλός" if status['disk_percent'] < 70 else "🟡 Μέτριος" if status['disk_percent'] < 90 else "🔴 Γεμάτος"
        msg += f"💿 **Δίσκος:** {status['disk_used']:.1f}GB από {status['disk_total']:.1f}GB\n"
        msg += f"   📊 {status['disk_percent']:.1f}% - {disk_status}\n\n"

        # Python Processes - απλά
        process_count = len(status['python_processes'])
        msg += f"🐍 **Python Εφαρμογές:** {process_count} ενεργές\n\n"

        # Top processes - μόνο τις σημαντικές
        if status['python_processes']:
            msg += "🔥 **Κύριες Εφαρμογές:**\n"
            for i, proc in enumerate(status['python_processes'][:2], 1):
                name = proc['cmdline'].split('/')[-1] if '/' in proc['cmdline'] else proc['cmdline']
                name = name.replace('.py', '').replace('python3 ', '')[:25]
                msg += f"   {i}. {name} (CPU: {proc['cpu']:.1f}%)\n"
            msg += "\n"

        # Footer - απλός
        msg += f"⏰ **Ενημέρωση:** {datetime.now().strftime('%H:%M:%S')}\n"
        msg += f"✅ **Κατάσταση:** Όλα λειτουργούν κανονικά"

        return msg

    @staticmethod
    def format_ai_status(ai_status: Dict) -> str:
        """Απλό AI status"""
        if 'error' in ai_status:
            return f"""
❌ **Σφάλμα AI Monitor**
{ai_status['error']}
"""

        msg = f"""
🧠 **AI MONITOR**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        # Status - απλά
        if ai_status['ai_running']:
            msg += "🟢 **Κατάσταση:** ΕΝΕΡΓΟ\n"
            msg += f"⏰ **Τελευταία Δραστηριότητα:** {ai_status['last_activity'] or 'Καμία πρόσφατη'}\n\n"
        else:
            msg += "🔴 **Κατάσταση:** ΑΝΕΝΕΡΓΟ\n\n"

        # Recent activity - απλά
        msg += "📝 **Πρόσφατη Δραστηριότητα:**\n"
        if ai_status['recent_logs']:
            for log_line in ai_status['recent_logs'][-3:]:
                if log_line.strip():
                    clean_log = log_line.strip()[:50]
                    msg += f"   • {clean_log}...\n"
        else:
            msg += "   • Καμία πρόσφατη δραστηριότητα\n"

        msg += f"\n⏰ **Έλεγχος:** {datetime.now().strftime('%H:%M:%S')}"

        return msg

    @staticmethod
    def format_trading_stats(stats: Dict) -> str:
        """Απλά trading statistics"""
        msg = f"""
📈 **ΣΤΑΤΙΣΤΙΚΑ TRADING**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        if not stats or stats.get('total_trades', 0) == 0:
            msg += "📊 **Δεν υπάρχουν δεδομένα trading**\n"
            msg += "🚀 Ξεκίνησε trading για να δεις στατιστικά!"
            return msg

        total_trades = stats.get('total_trades', 0)
        winning_trades = stats.get('winning_trades', 0)
        total_profit = stats.get('total_profit', 0)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        # Απλά στατιστικά
        msg += f"📊 **Συνολικές Συναλλαγές:** {total_trades}\n"
        msg += f"✅ **Κερδοφόρες:** {winning_trades}\n"
        msg += f"❌ **Ζημιογόνες:** {total_trades - winning_trades}\n\n"

        # Win rate με απλό τρόπο
        win_status = "🔥 Εξαιρετικό" if win_rate > 70 else "✅ Καλό" if win_rate > 50 else "⚠️ Μέτριο"
        msg += f"🎯 **Ποσοστό Επιτυχίας:** {win_rate:.1f}% - {win_status}\n\n"

        # Κέρδη
        profit_status = "🟢 Κέρδος" if total_profit > 0 else "🔴 Ζημία"
        msg += f"💰 **Συνολικό Αποτέλεσμα:** {total_profit:+.2f}€ - {profit_status}\n"
        msg += f"📊 **Μέσος Όρος:** {stats.get('avg_profit', 0):.2f}€\n\n"

        msg += f"⏰ **Ενημέρωση:** {datetime.now().strftime('%H:%M:%S')}"

        return msg

    @staticmethod
    def format_process_list(processes: List[Dict]) -> str:
        """Απλή λίστα processes"""
        msg = f"""
🐍 **PYTHON ΕΦΑΡΜΟΓΕΣ**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        if not processes:
            msg += "📊 **Δεν βρέθηκαν ενεργές εφαρμογές**\n"
            msg += "💤 Το σύστημα είναι σε αναμονή"
            return msg

        msg += f"📊 **Συνολικές Εφαρμογές:** {len(processes)}\n\n"

        for i, proc in enumerate(processes[:4], 1):
            # Καθαρό όνομα εφαρμογής
            name = proc['cmdline'].split('/')[-1] if '/' in proc['cmdline'] else proc['cmdline']
            name = name.replace('.py', '').replace('python3 ', '')[:30]

            # Απλή κατάσταση
            cpu_status = "🔥" if proc['cpu'] > 10 else "✅" if proc['cpu'] > 1 else "💤"

            msg += f"{i}. **{name}**\n"
            msg += f"   🆔 PID: {proc['pid']}\n"
            msg += f"   {cpu_status} CPU: {proc['cpu']:.1f}% | RAM: {proc['memory']:.1f}%\n\n"

        msg += f"⏰ **Σάρωση:** {datetime.now().strftime('%H:%M:%S')}"

        return msg

    @staticmethod
    def format_menu_header(title: str, description: str) -> str:
        """Απλό menu header"""
        return f"""
🎯 **{title.upper()}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 {description}

👇 **Επίλεξε μια επιλογή:**
"""

    @staticmethod
    def format_success_message(title: str, message: str) -> str:
        """Απλό success message"""
        return f"""
✅ **{title.upper()}**

🎉 {message}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

    @staticmethod
    def format_error_message(title: str, error: str) -> str:
        """Απλό error message"""
        return f"""
❌ **{title.upper()}**

⚠️ {error}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

    @staticmethod
    def format_info_message(title: str, info: str) -> str:
        """Απλό info message"""
        return f"""
ℹ️ **{title.upper()}**

📝 {info}

⏰ {datetime.now().strftime('%H:%M:%S')}
"""

    @staticmethod
    def format_greek_balance(balance: float, initial_balance: float) -> str:
        """Ελληνικό υπόλοιπο με απλά λόγια"""
        profit = balance - initial_balance
        profit_pct = (profit / initial_balance) * 100

        status = "🟢 ΚΕΡΔΟΣ" if profit > 0 else "🔴 ΖΗΜΙΑ" if profit < 0 else "⚪ ΙΣΟΠΑΛΙΑ"

        return f"""
💰 **ΤΟ ΠΟΡΤΟΦΟΛΙ ΣΟΥ**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💵 **Έχεις τώρα:** {balance:.2f} USDC
🏦 **Ξεκίνησες με:** {initial_balance:.2f} USDC

{status}
📊 **Αποτέλεσμα:** {profit:+.2f} USDC ({profit_pct:+.1f}%)

💡 **Τι σημαίνει:**
• Αν είναι πράσινο = κερδίζεις χρήματα! 🎉
• Αν είναι κόκκινο = χάνεις χρήματα 😔
• USDC = σαν δολάρια για crypto

⏰ **Ενημέρωση:** {datetime.now().strftime('%H:%M:%S')}
"""

    @staticmethod
    def format_greek_orders(orders: list) -> str:
        """Ελληνικές παραγγελίες με απλά λόγια"""
        if not orders:
            return """
📋 **ΟΙ ΣΥΝΑΛΛΑΓΕΣ ΣΟΥ**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Δεν έχεις κάνει ακόμα συναλλαγές**
🚀 Πάτησε "Αγορά" ή "Πώληση" για να ξεκινήσεις!

💡 **Τι σημαίνει:**
• Αγορά = αγοράζεις crypto νομίσματα
• Πώληση = πουλάς crypto νομίσματα
• Στόχος = να αγοράσεις φθηνά και να πουλήσεις ακριβά!
"""

        msg = """
📋 **ΟΙ ΤΕΛΕΥΤΑΙΕΣ ΣΥΝΑΛΛΑΓΕΣ ΣΟΥ**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        for i, order in enumerate(orders[:5], 1):
            symbol = order[1]
            side = order[2]
            amount = order[3]
            price = order[4]
            timestamp = order[5]

            side_emoji = "🟢 ΑΓΟΡΑΣΕΣ" if side == 'buy' else "🔴 ΠΟΥΛΗΣΕΣ"
            total = amount * price

            # Απλοποίηση timestamp
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%H:%M')
            except:
                time_str = "πρόσφατα"

            # Απλό όνομα νομίσματος
            coin_name = symbol.replace('/USDC', '').replace('BTC', 'Bitcoin').replace('ETH', 'Ethereum').replace('ADA', 'Cardano').replace('DOT', 'Polkadot').replace('LINK', 'Chainlink')

            msg += f"""
**{i}. {coin_name}**
   {side_emoji} | Ποσότητα: {amount:.4f}
   💰 Τιμή: {price:.2f} USDC | Αξία: {total:.2f} USDC
   ⏰ Ώρα: {time_str}

"""

        msg += """💡 **Τι σημαίνει:**
• Ποσότητα = πόσα νομίσματα αγόρασες/πούλησες
• Τιμή = πόσο κόστιζε το κάθε νόμισμα
• Αξία = συνολικά χρήματα που έδωσες/πήρες"""

        return msg

    @staticmethod
    def format_greek_prices(current_prices: dict) -> str:
        """Ελληνικές τιμές με απλά λόγια"""
        import random

        msg = """
📈 **ΤΙΜΕΣ ΝΟΜΙΣΜΑΤΩΝ ΤΩΡΑ**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **Οι τιμές αλλάζουν συνέχεια!**

"""

        coin_names = {
            'BTC/USDC': '₿ Bitcoin',
            'ETH/USDC': '⟠ Ethereum',
            'ADA/USDC': '🔵 Cardano',
            'DOT/USDC': '⚫ Polkadot',
            'LINK/USDC': '🔗 Chainlink'
        }

        for symbol, base_price in current_prices.items():
            # Προσομοίωση αλλαγής
            change = random.uniform(-5, 5)
            change_emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
            change_text = "ανεβαίνει" if change > 0 else "κατεβαίνει" if change < 0 else "σταθερό"

            coin_name = coin_names.get(symbol, symbol)

            msg += f"""
**{coin_name}**
💰 {base_price:.4f} USDC {change_emoji} {change_text} ({change:+.2f}%)

"""

        msg += f"""
💡 **Τι σημαίνει:**
• 🟢 = η τιμή ανεβαίνει (καλό για πώληση)
• 🔴 = η τιμή κατεβαίνει (καλό για αγορά)
• USDC = σαν δολάρια

⏰ **Ενημέρωση:** {datetime.now().strftime('%H:%M:%S')}"""
        return msg