#!/usr/bin/env python3
"""
Simple Beautiful Formatter για Telegram Bot
Παρέχει όμορφη μορφοποίηση για μηνύματα
"""

from datetime import datetime
from typing import Dict, List, Any
import random

class SimpleFormatter:
    """Κλάση για όμορφη μορφοποίηση μηνυμάτων"""

    @staticmethod
    def format_menu_header(title: str, description: str) -> str:
        """Μορφοποίηση header για μενού"""
        return f"""
🚀 **{title}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{description}

⏰ **Ώρα**: {datetime.now().strftime('%H:%M:%S')}
        """

    @staticmethod
    def format_system_status(status: Dict[str, Any]) -> str:
        """Μορφοποίηση system status"""
        cpu_icon = "🟢" if status['cpu_percent'] < 70 else "🟡" if status['cpu_percent'] < 90 else "🔴"
        memory_icon = "🟢" if status['memory_percent'] < 70 else "🟡" if status['memory_percent'] < 90 else "🔴"

        return f"""
📊 **System Status Report**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖥️ **CPU Usage**: {cpu_icon} {status['cpu_percent']:.1f}%
💾 **Memory Usage**: {memory_icon} {status['memory_percent']:.1f}%
🐍 **Python Processes**: {len(status['python_processes'])}

⏰ **Last Check**: {datetime.now().strftime('%H:%M:%S')}
🎯 **Status**: {'🟢 Healthy' if status['cpu_percent'] < 80 and status['memory_percent'] < 80 else '⚠️ High Usage'}
        """

    @staticmethod
    def format_ai_status(ai_status: Dict[str, Any]) -> str:
        """Μορφοποίηση AI status"""
        status_icon = "🟢" if ai_status['ai_running'] else "🔴"

        return f"""
🤖 **AI Monitor Status**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 **AI Monitor**: {status_icon} {'Running' if ai_status['ai_running'] else 'Stopped'}
📊 **Monitoring**: {'Active' if ai_status['ai_running'] else 'Inactive'}

⏰ **Last Check**: {datetime.now().strftime('%H:%M:%S')}
        """

    @staticmethod
    def format_greek_balance(balance: float, initial_balance: float) -> str:
        """Μορφοποίηση ελληνικού balance"""
        profit = balance - initial_balance
        profit_percent = (profit / initial_balance) * 100 if initial_balance > 0 else 0
        profit_icon = "🟢" if profit >= 0 else "🔴"

        return f"""
💰 **ΤΟ ΠΟΡΤΟΦΟΛΙ ΣΟΥ**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💵 **Συνολικό Υπόλοιπο**: {balance:.2f} USDC
🎯 **Αρχικό Κεφάλαιο**: {initial_balance:.2f} USDC

{profit_icon} **Κέρδος/Ζημιά**: {profit:+.2f} USDC ({profit_percent:+.1f}%)

⏰ **Ενημέρωση**: {datetime.now().strftime('%H:%M:%S')}

💡 **Tip**: {'Συνέχισε έτσι!' if profit >= 0 else 'Μην ανησυχείς, είναι φυσιολογικό!'}
        """

    @staticmethod
    def format_greek_prices(prices: Dict[str, float]) -> str:
        """Μορφοποίηση ελληνικών τιμών"""
        text = """
📈 **ΤΙΜΕΣ CRYPTO ΝΟΜΙΣΜΑΤΩΝ**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 **Τρέχουσες Τιμές σε USDC:**

"""

        coin_names = {
            'BTC/USDC': '₿ Bitcoin',
            'ETH/USDC': '⟠ Ethereum',
            'ADA/USDC': '🔵 Cardano',
            'DOT/USDC': '⚫ Polkadot',
            'LINK/USDC': '🔗 Chainlink'
        }

        for symbol, price in prices.items():
            name = coin_names.get(symbol, symbol)
            # Προσθήκη τυχαίας αλλαγής για demo
            change = random.uniform(-5, 5)
            change_icon = "🟢" if change >= 0 else "🔴"
            text += f"{name}: {price:.4f} USDC {change_icon} {change:+.1f}%\n"

        text += f"\n⏰ **Ενημέρωση**: {datetime.now().strftime('%H:%M:%S')}"
        text += "\n💡 **Tip**: Οι τιμές αλλάζουν συνεχώς!"

        return text

    @staticmethod
    def format_greek_orders(orders: List[Dict[str, Any]]) -> str:
        """Μορφοποίηση ελληνικών παραγγελιών"""
        if not orders:
            return """
📋 **ΟΙ ΣΥΝΑΛΛΑΓΕΣ ΣΟΥ**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ **Δεν έχεις κάνει ακόμα συναλλαγές**

💡 **Tip**: Ξεκίνα με μια μικρή αγορά Bitcoin!
            """

        text = """
📋 **ΟΙ ΣΥΝΑΛΛΑΓΕΣ ΣΟΥ**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Πρόσφατες Συναλλαγές:**

"""

        for i, order in enumerate(orders[:5], 1):
            action_text = "🟢 ΑΓΟΡΑ" if order['side'] == 'buy' else "🔴 ΠΩΛΗΣΗ"
            coin = order['symbol'].replace('/USDC', '')
            text += f"{i}. {action_text} {coin}\n"
            text += f"   💰 Ποσό: {order['amount']:.4f}\n"
            text += f"   💵 Τιμή: {order['price']:.4f} USDC\n"
            text += f"   ⏰ {order['timestamp']}\n\n"

        text += f"📊 **Σύνολο Συναλλαγών**: {len(orders)}"
        text += f"\n⏰ **Ενημέρωση**: {datetime.now().strftime('%H:%M:%S')}"

        return text

    @staticmethod
    def format_success_message(title: str, message: str) -> str:
        """Μορφοποίηση μηνύματος επιτυχίας"""
        return f"""
✅ **{title}**

{message}

⏰ **Ώρα**: {datetime.now().strftime('%H:%M:%S')}
        """

    @staticmethod
    def format_error_message(title: str, error: str) -> str:
        """Μορφοποίηση μηνύματος σφάλματος"""
        return f"""
❌ **{title}**

⚠️ **Σφάλμα**: {error}

⏰ **Ώρα**: {datetime.now().strftime('%H:%M:%S')}
💡 **Tip**: Δοκίμασε ξανά σε λίγο
        """