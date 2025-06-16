#!/usr/bin/env python3
"""
📱 Telegram Message Formatter - Compact & Clean Messages
🎯 Features:
- Concise formatting
- Essential information only
- Greek language support
"""

from datetime import datetime
from typing import Dict, List, Optional, Union
import json


class TelegramMessageFormatter:
    """📱 Compact Telegram Message Formatter"""

    def __init__(self):
        # Essential emojis only
        self.emojis = {
            'success': '✅', 'warning': '⚠️', 'error': '❌', 'info': 'ℹ️',
            'money': '💰', 'chart': '📊', 'rocket': '🚀', 'fire': '🔥',
            'shield': '🛡️', 'bell': '🔔', 'target': '🎯', 'trend_up': '📈',
            'trend_down': '📉', 'time': '⏰', 'coin': '🪙'
        }

    def format_currency(self, amount: float, currency: str = "€") -> str:
        """Format currency with proper styling"""
        if amount >= 0:
            return f"+{amount:.2f}{currency}"
        else:
            return f"{amount:.2f}{currency}"

    def format_percentage(self, percentage: float) -> str:
        """Format percentage with proper styling"""
        if percentage >= 0:
            return f"+{percentage:.2f}%"
        else:
            return f"{percentage:.2f}%"

    def format_duration(self, minutes: int) -> str:
        """Format duration in a readable way"""
        if minutes < 60:
            return f"{minutes}λ"
        elif minutes < 1440:  # Less than 24 hours
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours}ω {mins}λ"
        else:
            days = minutes // 1440
            hours = (minutes % 1440) // 60
            return f"{days}μ {hours}ω"

    def format_trade_opened(self, trade_data: Dict) -> str:
        """Format trade opened message - COMPACT"""
        pair = trade_data.get('pair', 'N/A')
        strategy = trade_data.get('strategy', 'N/A')
        entry_price = trade_data.get('entry_price', 0)
        amount = trade_data.get('amount', 0)

        message = f"""
{self.emojis['rocket']} <b>ΝΕΟΣ TRADE</b>
{self.emojis['coin']} <code>{pair}</code> | {strategy}
{self.emojis['money']} Είσοδος: <code>{entry_price:.6f}</code>
{self.emojis['target']} Ποσό: <code>{amount:.4f}</code>
"""
        return message.strip()

    def format_trade_closed(self, trade_data: Dict) -> str:
        """Format trade closed message - COMPACT"""
        pair = trade_data.get('pair', 'N/A')
        strategy = trade_data.get('strategy', 'N/A')
        entry_price = trade_data.get('entry_price', 0)
        exit_price = trade_data.get('exit_price', 0)
        profit_abs = trade_data.get('profit_abs', 0)
        profit_ratio = trade_data.get('profit_ratio', 0) * 100
        duration_minutes = trade_data.get('duration_minutes', 0)
        exit_reason = trade_data.get('exit_reason', 'N/A')

        # Determine if profit or loss
        is_profit = profit_abs > 0
        emoji_result = self.emojis['trend_up'] if is_profit else self.emojis['trend_down']
        result_text = "ΚΕΡΔΟΣ" if is_profit else "ΖΗΜΙΑ"

        message = f"""
{emoji_result} <b>{result_text}</b> | <code>{pair}</code>
{self.emojis['money']} <code>{self.format_currency(profit_abs)}</code> ({self.format_percentage(profit_ratio)})
{self.emojis['time']} {self.format_duration(duration_minutes)} | {exit_reason}
"""
        return message.strip()

    def format_daily_summary(self, summary_data: Dict) -> str:
        """Format daily summary message - COMPACT"""
        total_trades = summary_data.get('total_trades', 0)
        winning_trades = summary_data.get('winning_trades', 0)
        daily_pnl = summary_data.get('daily_pnl', 0)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        current_balance = summary_data.get('current_balance', 0)

        is_positive_day = daily_pnl > 0
        day_emoji = self.emojis['fire'] if is_positive_day else self.emojis['shield']

        message = f"""
{day_emoji} <b>ΗΜΕΡΗΣΙΑ ΑΝΑΦΟΡΑ</b>
{self.emojis['chart']} {total_trades} trades | {winning_trades} wins ({win_rate:.1f}%)
{self.emojis['money']} Ημέρα: <code>{self.format_currency(daily_pnl)}</code>
{self.emojis['coin']} Σύνολο: <code>{self.format_currency(current_balance)}</code>
"""
        return message.strip()

    def format_risk_alert(self, alert_data: Dict) -> str:
        """Format risk alert message - COMPACT"""
        alert_type = alert_data.get('type', 'general')
        message_text = alert_data.get('message', 'Ειδοποίηση κινδύνου')
        severity = alert_data.get('severity', 'medium')

        # Choose emoji based on severity
        if severity == 'high':
            emoji = self.emojis['error']
        elif severity == 'medium':
            emoji = self.emojis['warning']
        else:
            emoji = self.emojis['info']

        message = f"""
{emoji} <b>{alert_type}</b>
{message_text}
"""
        return message.strip()

    def format_system_status(self, status_data: Dict) -> str:
        """Format system status message - COMPACT"""
        freqtrade_running = status_data.get('freqtrade_running', False)
        open_trades = status_data.get('open_trades', 0)
        current_balance = status_data.get('current_balance', 0)

        # System health emoji
        health_emoji = self.emojis['success'] if freqtrade_running else self.emojis['warning']

        message = f"""
{health_emoji} <b>ΣΥΣΤΗΜΑ</b>
{self.emojis['rocket']} FreqTrade: {'✅' if freqtrade_running else '❌'}
{self.emojis['chart']} Ανοιχτά: {open_trades} | Υπόλοιπο: <code>{self.format_currency(current_balance)}</code>
"""
        return message.strip()


def main():
    """Example usage of the formatter"""
    formatter = TelegramMessageFormatter()

    # Example trade closed
    trade_closed_data = {
        'pair': 'ETH/USDC',
        'strategy': 'UltraFastScalpingStrategy',
        'entry_price': 3245.67,
        'exit_price': 3267.89,
        'profit_abs': 12.45,
        'profit_ratio': 0.0234,
        'duration_minutes': 127,
        'exit_reason': 'ROI'
    }

    print("=== COMPACT TRADE CLOSED ===")
    print(formatter.format_trade_closed(trade_closed_data))


if __name__ == "__main__":
    main()