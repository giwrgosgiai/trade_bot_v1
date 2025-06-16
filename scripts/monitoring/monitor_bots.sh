#!/bin/bash

# 📊 ULTIMATE TRADING SYSTEM - MONITOR ALL BOTS
# This script monitors all trading bots and shows their performance

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}📊 ULTIMATE TRADING SYSTEM - BOT MONITOR${NC}"
echo "=========================================="
echo ""

# Function to check bot status
check_bot_status() {
    local name=$1
    local port=$2
    local pid_file="logs/${name,,}_bot.pid"

    echo -e "${BLUE}$name Bot Status:${NC}"

    # Check if PID file exists
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")

        # Check if process is running
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "  Status: ${GREEN}RUNNING${NC} (PID: $pid)"

            # Check API if port is specified
            if [ ! -z "$port" ]; then
                if curl -s -u freqtrade:ruriu7AY "http://localhost:$port/api/v1/status" > /dev/null 2>&1; then
                    echo -e "  API:    ${GREEN}ACCESSIBLE${NC} (http://localhost:$port)"

                    # Get bot status
                    local status=$(curl -s -u freqtrade:ruriu7AY "http://localhost:$port/api/v1/status" | python3 -c "import json, sys; data = json.load(sys.stdin); print(f'State: {data[\"state\"]}, Open Trades: {len(data.get(\"open_trades\", []))}')" 2>/dev/null)
                    echo -e "  Info:   ${CYAN}$status${NC}"

                    # Get profit info
                    local profit=$(curl -s -u freqtrade:ruriu7AY "http://localhost:$port/api/v1/profit" | python3 -c "import json, sys; data = json.load(sys.stdin); print(f'Profit: {data.get(\"profit_closed_coin\", 0):.4f} USDT, Trades: {data.get(\"trade_count\", 0)}')" 2>/dev/null)
                    echo -e "  Profit: ${YELLOW}$profit${NC}"
                else
                    echo -e "  API:    ${RED}NOT ACCESSIBLE${NC}"
                fi
            fi
        else
            echo -e "  Status: ${RED}NOT RUNNING${NC}"
        fi
    else
        echo -e "  Status: ${RED}NO PID FILE${NC}"
    fi

    # Show recent log entries
    local log_file="logs/${name,,}_bot.log"
    if [ -f "$log_file" ]; then
        echo -e "  Recent: ${CYAN}$(tail -1 "$log_file" 2>/dev/null | cut -c1-80)...${NC}"
    fi

    echo ""
}

# Check all bots
check_bot_status "MainCoins" "8080"
check_bot_status "Altcoin" "8081"
check_bot_status "Scalping" "8082"
check_bot_status "AILearning" ""

# Overall system status
echo -e "${YELLOW}System Overview:${NC}"
echo "================"

# Count running bots
running_bots=0
total_bots=4

for bot in maincoins altcoin scalping ailearning; do
    if [ -f "logs/${bot}_bot.pid" ]; then
        pid=$(cat "logs/${bot}_bot.pid")
        if ps -p $pid > /dev/null 2>&1; then
            ((running_bots++))
        fi
    fi
done

echo -e "Running Bots: ${GREEN}$running_bots${NC}/$total_bots"

# Show total profit (if APIs are accessible)
total_profit=0
total_trades=0

for port in 8080 8081 8082; do
    if curl -s -u freqtrade:ruriu7AY "http://localhost:$port/api/v1/profit" > /dev/null 2>&1; then
        profit=$(curl -s -u freqtrade:ruriu7AY "http://localhost:$port/api/v1/profit" | python3 -c "import json, sys; data = json.load(sys.stdin); print(data.get('profit_closed_coin', 0))" 2>/dev/null)
        trades=$(curl -s -u freqtrade:ruriu7AY "http://localhost:$port/api/v1/profit" | python3 -c "import json, sys; data = json.load(sys.stdin); print(data.get('trade_count', 0))" 2>/dev/null)

        if [[ "$profit" =~ ^-?[0-9]+\.?[0-9]*$ ]]; then
            total_profit=$(python3 -c "print($total_profit + $profit)")
        fi

        if [[ "$trades" =~ ^[0-9]+$ ]]; then
            total_trades=$((total_trades + trades))
        fi
    fi
done

echo -e "Total Profit: ${YELLOW}$total_profit USDT${NC}"
echo -e "Total Trades: ${CYAN}$total_trades${NC}"

# System resources
echo ""
echo -e "${YELLOW}System Resources:${NC}"
echo "=================="
echo -e "CPU Usage: ${CYAN}$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%${NC}"
echo -e "Memory:    ${CYAN}$(free -h | awk 'NR==2{printf "%.1f%%", $3*100/$2}')${NC}"
echo -e "Disk:      ${CYAN}$(df -h . | awk 'NR==2{print $5}')${NC}"

echo ""
echo -e "${YELLOW}Quick Commands:${NC}"
echo "==============="
echo "- Restart all bots:    ./start_all_bots.sh"
echo "- Stop all bots:       ./stop_all_bots.sh"
echo "- View live logs:      tail -f logs/*_bot.log"
echo "- Main Coins Web UI:   http://localhost:8080"
echo "- Altcoin Web UI:      http://localhost:8081"
echo "- Scalping Web UI:     http://localhost:8082"
echo ""
echo -e "${GREEN}Monitor completed! 📊${NC}"