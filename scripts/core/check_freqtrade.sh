#!/bin/bash

# FreqTrade Status Check Script
# Comprehensive status check for FreqTrade

echo "📊 FreqTrade Status Check"
echo "========================"

# Check if FreqTrade process is running
if pgrep -f freqtrade > /dev/null; then
    echo "✅ FreqTrade Process: RUNNING"
    echo "   PID: $(pgrep -f freqtrade)"
else
    echo "❌ FreqTrade Process: NOT RUNNING"
    exit 1
fi

# Check API connectivity
echo ""
echo "🌐 API Status:"
if curl -s http://127.0.0.1:8080/api/v1/ping > /dev/null 2>&1; then
    echo "✅ API Server: RESPONDING"
    echo "   URL: http://127.0.0.1:8080"
else
    echo "❌ API Server: NOT RESPONDING"
fi

# Check authentication
echo ""
echo "🔐 Authentication Test:"
AUTH_TEST=$(curl -s -u freqtrade:ruriu7AY http://127.0.0.1:8080/api/v1/balance 2>/dev/null)
if [[ $AUTH_TEST == *"currencies"* ]]; then
    echo "✅ Authentication: WORKING"
    echo "   Username: freqtrade"
    echo "   Password: ruriu7AY"
else
    echo "❌ Authentication: FAILED"
fi

# Get balance info
echo ""
echo "💰 Balance Information:"
BALANCE=$(curl -s -u freqtrade:ruriu7AY http://127.0.0.1:8080/api/v1/balance 2>/dev/null)
if [[ $BALANCE == *"total"* ]]; then
    TOTAL=$(echo $BALANCE | grep -o '"total":[0-9.]*' | cut -d':' -f2)
    echo "   Total Balance: $TOTAL USDT"
else
    echo "   Balance: Unable to retrieve"
fi

# Get trades info
echo ""
echo "📈 Trading Status:"
TRADES=$(curl -s -u freqtrade:ruriu7AY http://127.0.0.1:8080/api/v1/trades 2>/dev/null)
if [[ $TRADES == *"trades_count"* ]]; then
    TRADES_COUNT=$(echo $TRADES | grep -o '"trades_count":[0-9]*' | cut -d':' -f2)
    echo "   Active Trades: $TRADES_COUNT"
else
    echo "   Trades: Unable to retrieve"
fi

# Get bot status
echo ""
echo "🤖 Bot Status:"
STATUS=$(curl -s -u freqtrade:ruriu7AY http://127.0.0.1:8080/api/v1/status 2>/dev/null)
if [[ $STATUS == *"state"* ]]; then
    echo "   Status: Bot is active"
else
    echo "   Status: Unable to retrieve bot status"
fi

echo ""
echo "🌐 Web UI Access:"
echo "   URL: http://127.0.0.1:8080"
echo "   Username: freqtrade"
echo "   Password: ruriu7AY"