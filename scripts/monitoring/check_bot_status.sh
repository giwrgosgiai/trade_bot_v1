#!/bin/bash

# 📊 Bot Status Checker Script
# Γιώργος Γιαϊλόγλου - Trading System

echo "🔍 Checking Trading Bot Status..."
echo "⏰ Check time: $(date)"
echo "=================================="

# Check if freqtrade processes are running
FREQTRADE_PROCESSES=$(ps aux | grep freqtrade | grep -v grep | grep -v tail)

if [ -z "$FREQTRADE_PROCESSES" ]; then
    echo "❌ No Freqtrade bots are currently running"
    echo ""
    echo "💡 To start the bot, run: ./start_trading_bot.sh"
else
    echo "✅ Freqtrade bots are running:"
    echo "$FREQTRADE_PROCESSES"
    echo ""

    # Count running bots
    BOT_COUNT=$(echo "$FREQTRADE_PROCESSES" | wc -l)
    echo "🤖 Total running bots: $BOT_COUNT"
    echo ""

    # Show active ports and web interfaces
    echo "🌐 Active Web Interfaces:"
    echo "========================"
    netstat -tlnp 2>/dev/null | grep -E "808[0-9]" | while read line; do
        port=$(echo $line | awk '{print $4}' | cut -d: -f2)
        pid=$(echo $line | awk '{print $7}' | cut -d/ -f1)

        # Determine bot type by port
        case $port in
            8080) bot_name="MainCoins Bot" ;;
            8083) bot_name="Altcoin Bot" ;;
            8084) bot_name="Scalping Bot" ;;
            *) bot_name="Unknown Bot" ;;
        esac

        echo "📱 $bot_name: http://127.0.0.1:$port (PID: $pid)"
    done

    echo ""
    echo "🔑 Login Credentials:"
    echo "===================="
    echo "👤 Username: freqtrade"
    echo "🔐 Password: ruriu7AY"

    echo ""
    echo "📝 Recent Activity (Last 3 lines from each bot):"
    echo "==============================================="

    # Show recent logs from each bot
    for logfile in logs/maincoins_bot.log logs/altcoin_bot.log logs/scalping_bot.log logs/altcoin_final.log logs/scalping_final.log; do
        if [ -f "$logfile" ]; then
            echo ""
            echo "📊 $(basename $logfile):"
            tail -3 "$logfile" | grep -E "(INFO|ERROR|WARNING)" | tail -2
        fi
    done
fi

echo ""
echo "📊 System Resources:"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"
echo "Disk Usage: $(df -h / | awk 'NR==2{printf "%s", $5}')"