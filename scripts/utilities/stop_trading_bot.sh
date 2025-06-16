#!/bin/bash

# 🛑 Bot Stopper Script
# Γιώργος Γιαϊλόγλου - Trading System

echo "🛑 Stopping Trading Bots..."
echo "⏰ Stop time: $(date)"
echo "=================================="

# Find freqtrade processes
FREQTRADE_PIDS=$(ps aux | grep freqtrade | grep -v grep | grep -v tail | awk '{print $2}')

if [ -z "$FREQTRADE_PIDS" ]; then
    echo "ℹ️  No Freqtrade bots are currently running"
else
    echo "🔍 Found running bots with PIDs: $FREQTRADE_PIDS"

    for PID in $FREQTRADE_PIDS; do
        echo "🛑 Stopping bot with PID: $PID"
        kill -SIGTERM $PID

        # Wait a bit for graceful shutdown
        sleep 3

        # Check if process is still running
        if kill -0 $PID 2>/dev/null; then
            echo "⚠️  Process $PID didn't stop gracefully, forcing..."
            kill -SIGKILL $PID
        fi
    done

    echo "✅ All bots stopped successfully"
fi

echo ""
echo "📊 Final Status Check:"
REMAINING_PROCESSES=$(ps aux | grep freqtrade | grep -v grep | grep -v tail)
if [ -z "$REMAINING_PROCESSES" ]; then
    echo "✅ No freqtrade processes remaining"
else
    echo "⚠️  Some processes may still be running:"
    echo "$REMAINING_PROCESSES"
fi

echo ""
echo "💡 To start bots again, run: ./start_trading_bot.sh"