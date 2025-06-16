#!/bin/bash

# Freqtrade Trading Bot Startup Script
echo "🚀 Starting Freqtrade Trading Bot with NFI5MOHO_WIP strategy..."

# Check if we're in the correct directory
if [ ! -f "configs/custom_config.json" ]; then
    echo "❌ Config file not found. Please run from the project root directory."
    exit 1
fi

# Kill any existing freqtrade processes
pkill -f freqtrade 2>/dev/null

# Clear old logs
mkdir -p logs
echo "📝 Starting new session..." > logs/freqtrade.log

# Start the bot
echo "🤖 Launching NFI5MOHO_WIP strategy in dry-run mode with 500 USDC..."
nohup freqtrade trade \
    --config configs/custom_config.json \
    --strategy NFI5MOHO_WIP \
    --dry-run \
    --logfile logs/freqtrade.log \
    > /dev/null 2>&1 &

BOT_PID=$!
echo "✅ Bot started with PID: $BOT_PID"

# Wait a moment for startup
sleep 5

# Check if bot is running
if ps -p $BOT_PID > /dev/null; then
    echo "🟢 Bot is running successfully!"
    echo "📊 UI available at: http://127.0.0.1:8080"
    echo "👤 Username: freqtrade"
    echo "🔑 Password: ruriu7AY"
    echo "📋 View logs: tail -f logs/freqtrade.log"
    echo "💰 Dry run wallet: 500 USDC"
    echo "📈 Strategy: NFI5MOHO_WIP"
    echo "⏰ Timeframe: 5m"
else
    echo "❌ Bot failed to start. Check logs:"
    tail -10 logs/freqtrade.log
fi