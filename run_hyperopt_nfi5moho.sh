#!/bin/bash

# NFI5MOHO Hyperopt Runner
# Runs hyperopt with 1000 epochs and early stopping after 20 consecutive epochs without improvement

echo "🎯 NFI5MOHO Hyperopt Runner"
echo "=========================="
echo "Strategy: NFI5MOHO_WIP"
echo "Max Epochs: 1000"
echo "Early Stop: 20 epochs without improvement"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed or not in PATH"
    exit 1
fi

# Check if freqtrade directory exists
if [ ! -d "freqtrade" ]; then
    echo "❌ Freqtrade directory not found"
    echo "Please make sure you're running this from the trade_bot_v1 directory"
    exit 1
fi

# Check if strategy exists
if [ ! -f "user_data/strategies/NFI5MOHO_WIP.py" ]; then
    echo "❌ Strategy file NFI5MOHO_WIP.py not found"
    exit 1
fi

# Check if config exists
if [ ! -f "configs/hyperopt_config.json" ]; then
    echo "❌ Hyperopt config file not found"
    exit 1
fi

# Create necessary directories
mkdir -p logs
mkdir -p user_data

echo "✅ All checks passed, starting hyperopt..."
echo ""

# Run the hyperopt script
cd /Users/georgegiailoglou/Documents/GitHub/trade_bot_v1 && python3 scripts/run_hyperopt_nfi5moho.py

echo ""
echo "🏁 Hyperopt completed!"
echo "Check the results in user_data/hyperopt_nfi5moho.sqlite"
echo "Logs are available in logs/hyperopt_nfi5moho.log"