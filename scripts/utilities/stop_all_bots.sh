#!/bin/bash

# 🛑 ULTIMATE TRADING SYSTEM - STOP ALL BOTS
# Γιώργος Γιαϊλόγλου - Safe Bot Shutdown

echo "🛑 Stopping ALL Trading Bots..."
echo "⏰ Stop time: $(date)"
echo "================================"

# Function to stop bots gracefully
stop_bots() {
    echo "🔍 Finding all Freqtrade processes..."

    # Find all freqtrade processes
    FREQTRADE_PIDS=$(ps aux | grep freqtrade | grep -v grep | grep -v tail | awk '{print $2}')

    if [ -z "$FREQTRADE_PIDS" ]; then
        echo "ℹ️  No Freqtrade bots are currently running"
        return 0
    fi

    echo "🤖 Found running bots with PIDs: $FREQTRADE_PIDS"
echo ""

    # Stop each bot gracefully
    for PID in $FREQTRADE_PIDS; do
        # Get bot info
        BOT_INFO=$(ps -p $PID -o args --no-headers 2>/dev/null)

        if [ ! -z "$BOT_INFO" ]; then
            echo "🛑 Stopping bot with PID: $PID"
            echo "📊 Command: $(echo $BOT_INFO | cut -c1-80)..."

            # Send SIGTERM for graceful shutdown
            kill -SIGTERM $PID 2>/dev/null

            # Wait for graceful shutdown
            echo "⏳ Waiting for graceful shutdown..."
            sleep 5

            # Check if process is still running
            if kill -0 $PID 2>/dev/null; then
                echo "⚠️  Process $PID didn't stop gracefully, forcing..."
                kill -SIGKILL $PID 2>/dev/null
                sleep 2
            fi

            # Verify process is stopped
            if kill -0 $PID 2>/dev/null; then
                echo "❌ Failed to stop process $PID"
            else
                echo "✅ Process $PID stopped successfully"
            fi
            echo ""
        fi
    done
}

# Stop all bots
stop_bots

# Wait a moment
sleep 3

# Final verification
echo "🔍 Final verification..."
REMAINING_BOTS=$(ps aux | grep freqtrade | grep -v grep | grep -v tail | wc -l)

if [ $REMAINING_BOTS -eq 0 ]; then
    echo "✅ All bots stopped successfully!"
else
    echo "⚠️  $REMAINING_BOTS bot(s) still running:"
    ps aux | grep freqtrade | grep -v grep | grep -v tail
fi

echo ""
echo "🌐 Checking ports..."
ACTIVE_PORTS=$(netstat -tlnp 2>/dev/null | grep -E "808[0-9]" | wc -l)

if [ $ACTIVE_PORTS -eq 0 ]; then
    echo "✅ All bot ports are now free"
    else
    echo "⚠️  Some ports still active:"
    netstat -tlnp 2>/dev/null | grep -E "808[0-9]"
    fi

echo ""
echo "📊 System Status:"
echo "================"
echo "🤖 Running bots: $(ps aux | grep freqtrade | grep -v grep | grep -v tail | wc -l)"
echo "🌐 Active ports: $(netstat -tlnp 2>/dev/null | grep -E "808[0-9]" | wc -l)"

echo ""
echo "🛠️  Next Steps:"
echo "=============="
echo "🚀 Start bots: ./start_all_bots.sh"
echo "📊 Check status: ./check_bot_status.sh"
echo "📝 View logs: ls -la logs/"

echo ""
echo "✅ Bot shutdown process completed!"
echo "💤 Trading system is now offline."