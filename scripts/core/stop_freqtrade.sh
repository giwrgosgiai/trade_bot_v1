#!/bin/bash

# FreqTrade Stop Script
# Safely stops all FreqTrade processes

echo "🛑 Stopping FreqTrade..."

# Stop FreqTrade processes
pkill -f freqtrade 2>/dev/null || true

# Wait for processes to stop
sleep 3

# Check if any processes are still running
if pgrep -f freqtrade > /dev/null; then
    echo "⚠️  Some processes still running, forcing stop..."
    pkill -9 -f freqtrade 2>/dev/null || true
    sleep 2
fi

# Final check
if pgrep -f freqtrade > /dev/null; then
    echo "❌ Failed to stop all FreqTrade processes"
    echo "Running processes:"
    ps aux | grep freqtrade | grep -v grep
else
    echo "✅ FreqTrade stopped successfully"
fi