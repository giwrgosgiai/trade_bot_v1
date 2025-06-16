#!/bin/bash

# 🤖 FreqTrade Bot Monitor & Auto-Restart System
# Κρατάει τα bots πάντα ανοιχτά και τα κάνει restart αν κρασάρουν

# Configuration
FREQTRADE_DIR="/home/giwrgosgiai/freqtrade"
LOG_DIR="$FREQTRADE_DIR/logs"
PID_DIR="$FREQTRADE_DIR/pids"

# Bot configurations
declare -A BOTS=(
    ["bot1"]="user_data/config.json:AILearningDayTradingStrategy:8080"
    ["bot2"]="user_data/altcoin_config.json:UltimateProfitAltcoinStrategy:8081"
    ["bot3"]="user_data/scalping_config.json:UltraFastScalpingStrategy:8082"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR"

log_message() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/monitor.log"
}

check_bot_health() {
    local bot_name=$1
    local port=$2

    # Check if process is running
    if [ -f "$PID_DIR/${bot_name}.pid" ]; then
        local pid=$(cat "$PID_DIR/${bot_name}.pid")
        if ps -p $pid > /dev/null 2>&1; then
            # Process exists, check if API responds
            if curl -s -u "freqtrade:ruriu7AY" "http://localhost:$port/api/v1/ping" > /dev/null 2>&1; then
                return 0  # Bot is healthy
            else
                log_message "${YELLOW}⚠️  Bot $bot_name (PID: $pid) not responding to API calls${NC}"
                return 1  # Bot unhealthy
            fi
        else
            log_message "${RED}❌ Bot $bot_name process (PID: $pid) not found${NC}"
            rm -f "$PID_DIR/${bot_name}.pid"
            return 1  # Process dead
        fi
    else
        return 1  # No PID file
    fi
}

start_bot() {
    local bot_name=$1
    local config_file=$2
    local strategy=$3
    local port=$4

    log_message "${BLUE}🚀 Starting bot $bot_name...${NC}"

    cd "$FREQTRADE_DIR"

    # Start bot in background
    nohup python3 -m freqtrade trade \
        --config "$config_file" \
        --strategy "$strategy" \
        --dry-run \
        > "$LOG_DIR/${bot_name}.log" 2>&1 &

    local pid=$!
    echo $pid > "$PID_DIR/${bot_name}.pid"

    # Wait a bit and check if it started successfully
    sleep 5
    if ps -p $pid > /dev/null 2>&1; then
        log_message "${GREEN}✅ Bot $bot_name started successfully (PID: $pid, Port: $port)${NC}"
        return 0
    else
        log_message "${RED}❌ Failed to start bot $bot_name${NC}"
        rm -f "$PID_DIR/${bot_name}.pid"
        return 1
    fi
}

stop_bot() {
    local bot_name=$1

    if [ -f "$PID_DIR/${bot_name}.pid" ]; then
        local pid=$(cat "$PID_DIR/${bot_name}.pid")
        if ps -p $pid > /dev/null 2>&1; then
            log_message "${YELLOW}🛑 Stopping bot $bot_name (PID: $pid)${NC}"
            kill $pid
            sleep 3
            if ps -p $pid > /dev/null 2>&1; then
                log_message "${RED}🔥 Force killing bot $bot_name${NC}"
                kill -9 $pid
            fi
        fi
        rm -f "$PID_DIR/${bot_name}.pid"
    fi
}

restart_bot() {
    local bot_name=$1
    local config_strategy_port=$2

    IFS=':' read -r config_file strategy port <<< "$config_strategy_port"

    log_message "${YELLOW}🔄 Restarting bot $bot_name${NC}"
    stop_bot "$bot_name"
    sleep 2
    start_bot "$bot_name" "$config_file" "$strategy" "$port"
}

monitor_bots() {
    log_message "${BLUE}🔍 Starting bot monitoring...${NC}"

    while true; do
        for bot_name in "${!BOTS[@]}"; do
            local config_strategy_port="${BOTS[$bot_name]}"
            IFS=':' read -r config_file strategy port <<< "$config_strategy_port"

            if ! check_bot_health "$bot_name" "$port"; then
                log_message "${RED}💀 Bot $bot_name is down! Restarting...${NC}"
                restart_bot "$bot_name" "$config_strategy_port"
            else
                log_message "${GREEN}💚 Bot $bot_name is healthy (Port: $port)${NC}"
            fi
        done

        # Wait before next check
        sleep 30
    done
}

start_all_bots() {
    log_message "${BLUE}🚀 Starting all FreqTrade bots...${NC}"

    for bot_name in "${!BOTS[@]}"; do
        local config_strategy_port="${BOTS[$bot_name]}"
        IFS=':' read -r config_file strategy port <<< "$config_strategy_port"

        if check_bot_health "$bot_name" "$port"; then
            log_message "${GREEN}✅ Bot $bot_name already running${NC}"
        else
            start_bot "$bot_name" "$config_file" "$strategy" "$port"
        fi
    done
}

stop_all_bots() {
    log_message "${YELLOW}🛑 Stopping all FreqTrade bots...${NC}"

    for bot_name in "${!BOTS[@]}"; do
        stop_bot "$bot_name"
    done
}

status_all_bots() {
    echo -e "${BLUE}📊 FreqTrade Bot Status${NC}"
    echo "=================================="

    for bot_name in "${!BOTS[@]}"; do
        local config_strategy_port="${BOTS[$bot_name]}"
        IFS=':' read -r config_file strategy port <<< "$config_strategy_port"

        if check_bot_health "$bot_name" "$port"; then
            local pid=$(cat "$PID_DIR/${bot_name}.pid" 2>/dev/null || echo "Unknown")
            echo -e "${GREEN}✅ $bot_name: RUNNING (PID: $pid, Port: $port)${NC}"
        else
            echo -e "${RED}❌ $bot_name: STOPPED (Port: $port)${NC}"
        fi
    done

    echo ""
    echo -e "${BLUE}🌐 Web Interface URLs:${NC}"
    echo "Bot 1: http://localhost:8080"
    echo "Bot 2: http://localhost:8081"
    echo "Bot 3: http://localhost:8082"
    echo "Username: freqtrade | Password: ruriu7AY"
}

# Handle script termination
cleanup() {
    log_message "${YELLOW}🛑 Monitor script terminated${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Main script logic
case "${1:-monitor}" in
    "start")
        start_all_bots
        ;;
    "stop")
        stop_all_bots
        ;;
    "restart")
        stop_all_bots
        sleep 3
        start_all_bots
        ;;
    "status")
        status_all_bots
        ;;
    "monitor")
        start_all_bots
        monitor_bots
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|monitor}"
        echo ""
        echo "Commands:"
        echo "  start   - Start all bots"
        echo "  stop    - Stop all bots"
        echo "  restart - Restart all bots"
        echo "  status  - Show bot status"
        echo "  monitor - Start monitoring (default, keeps bots alive)"
        exit 1
        ;;
esac