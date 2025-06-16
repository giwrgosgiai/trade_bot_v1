#!/bin/bash

# 🚀 Complete Trading System Startup Script
# Starts Freqtrade Bot + Enhanced UI Dashboard

echo "🚀 Starting Complete Trading System..."
echo "💰 Budget: €500 | Strategy: UltimateProfitStrategy"
echo "📊 UI Dashboard: http://localhost:5001"
echo "🔧 Freqtrade API: http://localhost:8080"

# Check if we're in the right directory
if [ ! -f "enhanced_trading_ui.py" ]; then
    echo "❌ Error: enhanced_trading_ui.py not found!"
    echo "Please run this script from the freqtrade directory"
    exit 1
fi

# Check if strategy exists
if [ ! -f "user_data/strategies/UltimateProfitStrategy.py" ]; then
    echo "❌ Error: UltimateProfitStrategy.py not found!"
    echo "Please ensure the strategy is in user_data/strategies/"
    exit 1
fi

# Check if config exists
if [ ! -f "user_data/config.json" ]; then
    echo "❌ Error: config.json not found!"
    echo "Please ensure config.json is in user_data/"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down trading system..."

    # Kill background processes
    if [ ! -z "$FREQTRADE_PID" ]; then
        kill $FREQTRADE_PID 2>/dev/null
        echo "✅ Freqtrade bot stopped"
    fi

    if [ ! -z "$UI_PID" ]; then
        kill $UI_PID 2>/dev/null
        echo "✅ UI dashboard stopped"
    fi

    echo "💾 System shutdown complete"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

echo ""
echo "🤖 Starting Freqtrade Bot..."

# Start Freqtrade in background
python -m freqtrade trade --config user_data/config.json --logfile logs/freqtrade.log &
FREQTRADE_PID=$!

# Wait a moment for Freqtrade to start
sleep 3

# Check if Freqtrade started successfully
if ! kill -0 $FREQTRADE_PID 2>/dev/null; then
    echo "❌ Failed to start Freqtrade bot!"
    echo "Check logs/freqtrade.log for details"
    exit 1
fi

echo "✅ Freqtrade bot started (PID: $FREQTRADE_PID)"
echo "📊 API available at: http://localhost:8080"

echo ""
echo "🎨 Starting Enhanced UI Dashboard..."

# Start UI Dashboard in background
python enhanced_trading_ui.py &
UI_PID=$!

# Wait a moment for UI to start
sleep 2

# Check if UI started successfully
if ! kill -0 $UI_PID 2>/dev/null; then
    echo "❌ Failed to start UI dashboard!"
    cleanup
    exit 1
fi

echo "✅ UI Dashboard started (PID: $UI_PID)"
echo "🌐 Dashboard available at: http://localhost:5001"

echo ""
echo "🎯 SYSTEM READY!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📈 Trading Dashboard: http://localhost:5001"
echo "🔧 Freqtrade API:     http://localhost:8080"
echo "📊 Strategy:          UltimateProfitStrategy"
echo "💰 Budget:            €500 (Dry Run)"
echo "⏱️  Timeframe:        5m"
echo "🎯 Target:            15%+ monthly return"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop the system"
echo ""

# Monitor both processes
while true; do
    # Check if Freqtrade is still running
    if ! kill -0 $FREQTRADE_PID 2>/dev/null; then
        echo "❌ Freqtrade bot stopped unexpectedly!"
        echo "Check logs/freqtrade.log for details"
        cleanup
        exit 1
    fi

    # Check if UI is still running
    if ! kill -0 $UI_PID 2>/dev/null; then
        echo "❌ UI dashboard stopped unexpectedly!"
        cleanup
        exit 1
    fi

    # Wait before next check
    sleep 10
done