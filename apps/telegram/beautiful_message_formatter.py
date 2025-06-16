#!/usr/bin/env python3
"""
🎨 Beautiful Message Formatter
Designer-style message formatting για Telegram bot
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

class BeautifulFormatter:
    """🎨 Designer-style message formatter"""

    # Emojis και symbols για styling
    ICONS = {
        'cpu': '🖥️',
        'memory': '💾',
        'disk': '💿',
        'process': '🔹',
        'active': '🟢',
        'inactive': '🔴',
        'warning': '🟡',
        'time': '⏰',
        'update': '🔄',
        'stats': '📊',
        'ai': '🧠',
        'system': '📈',
        'python': '🐍',
        'performance': '⚡',
        'separator': '━━━━━━━━━━━━━━━━━━━━',
        'line': '─────────────────────',
        'bullet': '▪️',
        'arrow': '▶️',
        'diamond': '💎',
        'star': '⭐',
        'fire': '🔥',
        'rocket': '🚀'
    }

    @staticmethod
    def create_header(title: str, icon: str = "📊") -> str:
        """Δημιουργεί όμορφο header"""
        return f"""
╭─────────────────────────╮
│  {icon} **{title}**  │
╰─────────────────────────╯
"""

    @staticmethod
    def create_section(title: str, content: str, icon: str = "▪️") -> str:
        """Δημιουργεί section με styling"""
        return f"""
{icon} **{title}**
{BeautifulFormatter.ICONS['line']}
{content}
"""

    @staticmethod
    def create_metric_bar(label: str, value: float, max_value: float = 100, width: int = 10) -> str:
        """Δημιουργεί visual progress bar"""
        percentage = (value / max_value) * 100
        filled = int((percentage / 100) * width)
        empty = width - filled

        # Χρώματα based on percentage
        if percentage < 30:
            bar_color = "🟢"
        elif percentage < 70:
            bar_color = "🟡"
        else:
            bar_color = "🔴"

        bar = bar_color * filled + "⚪" * empty
        return f"{label}: {bar} {percentage:.1f}%"

    @staticmethod
    def format_system_status(status: Dict) -> str:
        """Όμορφο system status με designer styling"""
        if 'error' in status:
            return f"""
╭─────────────────────────╮
│  ❌ **System Error**     │
╰─────────────────────────╯

🚨 **Error Details:**
{status['error']}
"""

        # Header
        msg = BeautifulFormatter.create_header("System Status", "🖥️")

        # CPU Section
        cpu_bar = BeautifulFormatter.create_metric_bar("CPU", status['cpu_percent'])
        cpu_section = f"""
{BeautifulFormatter.ICONS['cpu']} **CPU Performance**
{cpu_bar}
Current Load: **{status['cpu_percent']:.1f}%**
"""

        # Memory Section
        memory_bar = BeautifulFormatter.create_metric_bar("Memory", status['memory_percent'])
        memory_section = f"""
{BeautifulFormatter.ICONS['memory']} **Memory Usage**
{memory_bar}
Used: **{status['memory_used']:.1f}GB** / {status['memory_total']:.1f}GB
Available: **{status['memory_total'] - status['memory_used']:.1f}GB**
"""

        # Disk Section
        disk_bar = BeautifulFormatter.create_metric_bar("Disk", status['disk_percent'])
        disk_section = f"""
{BeautifulFormatter.ICONS['disk']} **Storage Space**
{disk_bar}
Used: **{status['disk_used']:.1f}GB** / {status['disk_total']:.1f}GB
Free: **{status['disk_total'] - status['disk_used']:.1f}GB**
"""

        # Python Processes
        process_count = len(status['python_processes'])
        process_icon = BeautifulFormatter.ICONS['active'] if process_count > 0 else BeautifulFormatter.ICONS['inactive']

        process_section = f"""
{BeautifulFormatter.ICONS['python']} **Active Python Processes**
{process_icon} **{process_count}** processes running
"""

        # Top processes
        if status['python_processes']:
            process_section += f"\n{BeautifulFormatter.ICONS['fire']} **Top Processes:**\n"
            for i, proc in enumerate(status['python_processes'][:3], 1):
                process_section += f"""
{BeautifulFormatter.ICONS['diamond']} **Process #{i}**
   PID: `{proc['pid']}` | CPU: **{proc['cpu']:.1f}%** | RAM: **{proc['memory']:.1f}%**
   {proc['cmdline'][:50]}...
"""

        # Footer
        footer = f"""
{BeautifulFormatter.ICONS['separator']}
{BeautifulFormatter.ICONS['time']} **Last Update:** {datetime.now().strftime('%H:%M:%S')}
{BeautifulFormatter.ICONS['update']} **Status:** All systems operational
"""

        return msg + cpu_section + memory_section + disk_section + process_section + footer

    @staticmethod
    def format_ai_status(ai_status: Dict) -> str:
        """Όμορφο AI status με designer styling"""
        if 'error' in ai_status:
            return f"""
╭─────────────────────────╮
│  ❌ **AI Monitor Error** │
╰─────────────────────────╯

🚨 **Error Details:**
{ai_status['error']}
"""

        # Header
        msg = BeautifulFormatter.create_header("AI Monitor Status", "🧠")

        # Status Section
        status_icon = BeautifulFormatter.ICONS['active'] if ai_status['ai_running'] else BeautifulFormatter.ICONS['inactive']
        status_text = "**ONLINE**" if ai_status['ai_running'] else "**OFFLINE**"

        status_section = f"""
{BeautifulFormatter.ICONS['ai']} **AI Monitor Status**
{status_icon} Status: {status_text}
{BeautifulFormatter.ICONS['time']} Last Activity: **{ai_status['last_activity'] or 'No recent activity'}**
"""

        # Activity Section
        activity_section = f"""
{BeautifulFormatter.ICONS['stats']} **Recent Activity**
{BeautifulFormatter.ICONS['line']}
"""

        if ai_status['recent_logs']:
            for i, log_line in enumerate(ai_status['recent_logs'][-5:], 1):
                if log_line.strip():
                    activity_section += f"{BeautifulFormatter.ICONS['arrow']} {log_line.strip()[:60]}...\n"
        else:
            activity_section += f"{BeautifulFormatter.ICONS['bullet']} No recent activity detected\n"

        # Footer
        footer = f"""
{BeautifulFormatter.ICONS['separator']}
{BeautifulFormatter.ICONS['time']} **Last Check:** {datetime.now().strftime('%H:%M:%S')}
{BeautifulFormatter.ICONS['rocket']} **AI System:** Ready for commands
"""

        return msg + status_section + activity_section + footer

    @staticmethod
    def format_trading_stats(stats: Dict) -> str:
        """Όμορφα trading statistics"""
        msg = BeautifulFormatter.create_header("Trading Statistics", "📈")

        if not stats or stats.get('total_trades', 0) == 0:
            return msg + f"""
{BeautifulFormatter.ICONS['bullet']} **No trading data available**
{BeautifulFormatter.ICONS['rocket']} Start trading to see statistics here!
"""

        total_trades = stats.get('total_trades', 0)
        winning_trades = stats.get('winning_trades', 0)
        total_profit = stats.get('total_profit', 0)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        # Performance indicators
        profit_icon = BeautifulFormatter.ICONS['active'] if total_profit > 0 else BeautifulFormatter.ICONS['inactive']
        performance_icon = BeautifulFormatter.ICONS['fire'] if win_rate > 60 else BeautifulFormatter.ICONS['star']

        # Win rate bar
        win_rate_bar = BeautifulFormatter.create_metric_bar("Win Rate", win_rate)

        stats_section = f"""
{BeautifulFormatter.ICONS['stats']} **Performance Overview**
{BeautifulFormatter.ICONS['line']}
{performance_icon} Total Trades: **{total_trades}**
{BeautifulFormatter.ICONS['active']} Winning: **{winning_trades}** trades
{BeautifulFormatter.ICONS['inactive']} Losing: **{total_trades - winning_trades}** trades

{win_rate_bar}

{profit_icon} **Total P&L:** **{total_profit:+.2f}€**
{BeautifulFormatter.ICONS['diamond']} Average: **{stats.get('avg_profit', 0):.2f}€**
{BeautifulFormatter.ICONS['rocket']} Best Trade: **{stats.get('best_trade', 0):.2f}€**
{BeautifulFormatter.ICONS['bullet']} Worst Trade: **{stats.get('worst_trade', 0):.2f}€**
"""

        footer = f"""
{BeautifulFormatter.ICONS['separator']}
{BeautifulFormatter.ICONS['time']} **Updated:** {datetime.now().strftime('%H:%M:%S')}
{BeautifulFormatter.ICONS['fire']} **Status:** Trading system active
"""

        return msg + stats_section + footer

    @staticmethod
    def format_process_list(processes: List[Dict]) -> str:
        """Όμορφη λίστα processes"""
        msg = BeautifulFormatter.create_header("Active Processes", "🐍")

        if not processes:
            return msg + f"""
{BeautifulFormatter.ICONS['bullet']} **No active processes found**
{BeautifulFormatter.ICONS['rocket']} System is idle
"""

        process_section = f"""
{BeautifulFormatter.ICONS['python']} **Python Processes**
{BeautifulFormatter.ICONS['line']}
"""

        for i, proc in enumerate(processes[:5], 1):
            # Performance indicators
            cpu_icon = BeautifulFormatter.ICONS['fire'] if proc['cpu'] > 10 else BeautifulFormatter.ICONS['active']
            memory_icon = BeautifulFormatter.ICONS['fire'] if proc['memory'] > 5 else BeautifulFormatter.ICONS['active']

            process_section += f"""
{BeautifulFormatter.ICONS['diamond']} **Process #{i}**
   {cpu_icon} PID: `{proc['pid']}` | CPU: **{proc['cpu']:.1f}%**
   {memory_icon} Memory: **{proc['memory']:.1f}%**
   {BeautifulFormatter.ICONS['arrow']} {proc['cmdline'][:50]}...

"""

        footer = f"""
{BeautifulFormatter.ICONS['separator']}
{BeautifulFormatter.ICONS['time']} **Scan Time:** {datetime.now().strftime('%H:%M:%S')}
{BeautifulFormatter.ICONS['stats']} **Total Processes:** {len(processes)}
"""

        return msg + process_section + footer

    @staticmethod
    def format_menu_header(title: str, description: str, icon: str = "🚀") -> str:
        """Όμορφο menu header"""
        return f"""
╔═══════════════════════════╗
║  {icon} **{title}**  ║
╚═══════════════════════════╝

{BeautifulFormatter.ICONS['bullet']} {description}

{BeautifulFormatter.ICONS['line']}
"""

    @staticmethod
    def format_success_message(title: str, message: str) -> str:
        """Success message με styling"""
        return f"""
╭─────────────────────────╮
│  ✅ **{title}**  │
╰─────────────────────────╯

{BeautifulFormatter.ICONS['rocket']} **Success!**
{message}

{BeautifulFormatter.ICONS['time']} {datetime.now().strftime('%H:%M:%S')}
"""

    @staticmethod
    def format_error_message(title: str, error: str) -> str:
        """Error message με styling"""
        return f"""
╭─────────────────────────╮
│  ❌ **{title}**  │
╰─────────────────────────╯

🚨 **Error Details:**
{error}

{BeautifulFormatter.ICONS['time']} {datetime.now().strftime('%H:%M:%S')}
"""

    @staticmethod
    def format_info_message(title: str, info: str, icon: str = "ℹ️") -> str:
        """Info message με styling"""
        return f"""
╭─────────────────────────╮
│  {icon} **{title}**  │
╰─────────────────────────╯

{BeautifulFormatter.ICONS['bullet']} {info}

{BeautifulFormatter.ICONS['time']} {datetime.now().strftime('%H:%M:%S')}
"""