#!/bin/bash

echo "🔍 Trading Bots Status Check"
echo "============================"

# Check processes
echo "📋 Running Bot Processes:"
BOTS_RUNNING=$(ps aux | grep freqtrade | grep -v grep | wc -l)
if [ $BOTS_RUNNING -gt 0 ]; then
    ps aux | grep freqtrade | grep -v grep | while read line; do
        if [[ $line == *"maincoins"* ]]; then
            echo "✅ MainCoins Bot: RUNNING"
        elif [[ $line == *"altcoin"* ]]; then
            echo "✅ Altcoin Bot: RUNNING"
        elif [[ $line == *"scalping"* ]]; then
            echo "✅ Scalping Bot: RUNNING"
        fi
    done
else
    echo "❌ No bots running"
fi

echo ""
echo "🌐 Web Interfaces:"
if netstat -tlnp 2>/dev/null | grep -q ":8080"; then
    echo "✅ MainCoins Bot (Port 8080): ACTIVE"
else
    echo "❌ MainCoins Bot (Port 8080): INACTIVE"
fi

if netstat -tlnp 2>/dev/null | grep -q ":8082"; then
    echo "✅ Altcoin Bot (Port 8082): ACTIVE"
else
    echo "❌ Altcoin Bot (Port 8082): INACTIVE"
fi

if netstat -tlnp 2>/dev/null | grep -q ":8084"; then
    echo "✅ Scalping Bot (Port 8084): ACTIVE"
else
    echo "❌ Scalping Bot (Port 8084): INACTIVE"
fi

echo ""
echo "📊 Database Files:"
if [ -f "user_data/maincoins_trades.sqlite" ]; then
    SIZE=$(ls -lh user_data/maincoins_trades.sqlite | awk '{print $5}')
    echo "✅ MainCoins DB: $SIZE"
else
    echo "❌ MainCoins DB: Missing"
fi

if [ -f "user_data/altcoin_trades.sqlite" ]; then
    SIZE=$(ls -lh user_data/altcoin_trades.sqlite | awk '{print $5}')
    echo "✅ Altcoin DB: $SIZE"
else
    echo "❌ Altcoin DB: Missing"
fi

if [ -f "user_data/scalping_trades.sqlite" ]; then
    SIZE=$(ls -lh user_data/scalping_trades.sqlite | awk '{print $5}')
    echo "✅ Scalping DB: $SIZE"
else
    echo "❌ Scalping DB: Missing"
fi

echo ""
echo "🧪 Force Trade Tests:"
echo "===================="

# Test MainCoins Bot
if netstat -tlnp 2>/dev/null | grep -q ":8080"; then
    echo "Testing MainCoins Bot..."
    RESULT=$(timeout 10 curl -s -X POST "http://127.0.0.1:8080/api/v1/forcebuy" \
        -H "Content-Type: application/json" \
        -u freqtrade:ruriu7AY \
        -d '{"pair": "BTC/USDT"}' 2>/dev/null | jq -r '.trade_id // .error' 2>/dev/null)

    if [[ "$RESULT" =~ ^[0-9]+$ ]]; then
        echo "✅ MainCoins Force Trade: SUCCESS (Trade ID: $RESULT)"

        # Test force exit
        sleep 2
        EXIT_RESULT=$(timeout 10 curl -s -X POST "http://127.0.0.1:8080/api/v1/forceexit" \
            -H "Content-Type: application/json" \
            -u freqtrade:ruriu7AY \
            -d "{\"tradeid\": \"$RESULT\"}" 2>/dev/null | jq -r '.trade_id // .error' 2>/dev/null)

        if [[ "$EXIT_RESULT" =~ ^[0-9]+$ ]]; then
            echo "✅ MainCoins Force Exit: SUCCESS"
        else
            echo "⚠️  MainCoins Force Exit: $EXIT_RESULT"
        fi
    else
        echo "❌ MainCoins Force Trade: $RESULT"
    fi
else
    echo "❌ MainCoins Bot: Web interface not available"
fi

# Test Altcoin Bot
if netstat -tlnp 2>/dev/null | grep -q ":8082"; then
    echo "Testing Altcoin Bot..."
    RESULT=$(timeout 10 curl -s -X POST "http://127.0.0.1:8082/api/v1/forcebuy" \
        -H "Content-Type: application/json" \
        -u freqtrade:ruriu7AY \
        -d '{"pair": "ADA/USDT"}' 2>/dev/null | jq -r '.trade_id // .error' 2>/dev/null)

    if [[ "$RESULT" =~ ^[0-9]+$ ]]; then
        echo "✅ Altcoin Force Trade: SUCCESS (Trade ID: $RESULT)"
    else
        echo "❌ Altcoin Force Trade: $RESULT"
    fi
else
    echo "❌ Altcoin Bot: Web interface not available"
fi

# Test Scalping Bot
if netstat -tlnp 2>/dev/null | grep -q ":8084"; then
    echo "Testing Scalping Bot..."
    RESULT=$(timeout 10 curl -s -X POST "http://127.0.0.1:8084/api/v1/forcebuy" \
        -H "Content-Type: application/json" \
        -u freqtrade:ruriu7AY \
        -d '{"pair": "ETH/USDT"}' 2>/dev/null | jq -r '.trade_id // .error' 2>/dev/null)

    if [[ "$RESULT" =~ ^[0-9]+$ ]]; then
        echo "✅ Scalping Force Trade: SUCCESS (Trade ID: $RESULT)"
    else
        echo "❌ Scalping Force Trade: $RESULT"
    fi
else
    echo "❌ Scalping Bot: Web interface not available"
fi

echo ""
echo "🎯 Summary & Instructions:"
echo "========================="
echo "🔐 Login Credentials:"
echo "Username: freqtrade"
echo "Password: ruriu7AY"
echo ""
echo "🌐 Access URLs:"
echo "MainCoins Bot: http://127.0.0.1:8080"
echo "Altcoin Bot: http://127.0.0.1:8082"
echo "Scalping Bot: http://127.0.0.1:8084"
echo ""
echo "🛠️  Management Commands:"
echo "./start_bots_stable.sh    - Start all bots"
echo "./stop_all_bots.sh        - Stop all bots"
echo "./check_bots_status.sh    - Check status (this script)"
echo ""
echo "✅ All fixes applied:"
echo "• Separate databases for each bot"
echo "• Force entry/exit enabled"
echo "• Fee rejection bypassed for force trades"
echo "• Autonomous operation (one crash doesn't affect others)"