#!/bin/bash
"""
🤖 FreqTrade Bot Management Script
Εύκολη διαχείριση των trading bots
"""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="freqtrade-keeper"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}🤖 FreqTrade Bot Manager${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_status() {
    echo -e "\n${YELLOW}📊 Current Status:${NC}"

    # Check if service is installed
    if systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
        echo -e "Service installed: ${GREEN}✅${NC}"

        # Check if service is running
        if systemctl is-active --quiet "$SERVICE_NAME"; then
            echo -e "Service running: ${GREEN}✅${NC}"
        else
            echo -e "Service running: ${RED}❌${NC}"
        fi

        # Check if service is enabled
        if systemctl is-enabled --quiet "$SERVICE_NAME"; then
            echo -e "Auto-start enabled: ${GREEN}✅${NC}"
        else
            echo -e "Auto-start enabled: ${RED}❌${NC}"
        fi
    else
        echo -e "Service installed: ${RED}❌${NC}"
    fi

    # Check bot processes
    echo -e "\n${YELLOW}🤖 Bot Processes:${NC}"
    if pgrep -f "freqtrade.*trade" > /dev/null; then
        echo -e "FreqTrade bots running: ${GREEN}✅${NC}"
        pgrep -f "freqtrade.*trade" | wc -l | xargs echo -e "Active bots: ${GREEN}"
    else
        echo -e "FreqTrade bots running: ${RED}❌${NC}"
    fi

    # Check ports
    echo -e "\n${YELLOW}🌐 Port Status:${NC}"
    for port in 8080 8081 8082; do
        if netstat -tuln | grep -q ":$port "; then
            echo -e "Port $port: ${GREEN}✅${NC}"
        else
            echo -e "Port $port: ${RED}❌${NC}"
        fi
    done
}

install_service() {
    echo -e "${YELLOW}📦 Installing systemd service...${NC}"

    # Copy service file
    sudo cp "$SCRIPT_DIR/freqtrade-keeper.service" "$SERVICE_FILE"

    # Reload systemd
    sudo systemctl daemon-reload

    # Enable service
    sudo systemctl enable "$SERVICE_NAME"

    echo -e "${GREEN}✅ Service installed and enabled${NC}"
}

start_service() {
    echo -e "${YELLOW}🚀 Starting FreqTrade Bot Keeper...${NC}"

    # Stop any existing processes first
    stop_manual

    # Start service
    sudo systemctl start "$SERVICE_NAME"

    # Wait a moment
    sleep 3

    # Check status
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ Bot Keeper started successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start Bot Keeper${NC}"
        echo -e "${YELLOW}Checking logs...${NC}"
        sudo journalctl -u "$SERVICE_NAME" --no-pager -n 10
    fi
}

stop_service() {
    echo -e "${YELLOW}🛑 Stopping FreqTrade Bot Keeper...${NC}"
    sudo systemctl stop "$SERVICE_NAME"
    echo -e "${GREEN}✅ Bot Keeper stopped${NC}"
}

restart_service() {
    echo -e "${YELLOW}🔄 Restarting FreqTrade Bot Keeper...${NC}"
    sudo systemctl restart "$SERVICE_NAME"
    sleep 3

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ Bot Keeper restarted successfully${NC}"
    else
        echo -e "${RED}❌ Failed to restart Bot Keeper${NC}"
    fi
}

start_manual() {
    echo -e "${YELLOW}🚀 Starting bots manually...${NC}"

    # Stop service if running
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        sudo systemctl stop "$SERVICE_NAME"
    fi

    # Stop any existing processes
    stop_manual

    # Start bot keeper manually
    cd "$SCRIPT_DIR"
    python3 bot_keeper.py
}

stop_manual() {
    echo -e "${YELLOW}🛑 Stopping all FreqTrade processes...${NC}"

    # Kill bot keeper
    pkill -f "bot_keeper.py" 2>/dev/null || true

    # Kill FreqTrade processes
    pkill -f "freqtrade.*trade" 2>/dev/null || true

    # Wait a moment
    sleep 2

    # Force kill if needed
    pkill -9 -f "freqtrade" 2>/dev/null || true

    echo -e "${GREEN}✅ All processes stopped${NC}"
}

show_logs() {
    echo -e "${YELLOW}📋 Recent logs:${NC}"

    if systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
        echo -e "\n${BLUE}=== Service Logs ===${NC}"
        sudo journalctl -u "$SERVICE_NAME" --no-pager -n 20
    fi

    if [ -f "$SCRIPT_DIR/logs/bot_keeper.log" ]; then
        echo -e "\n${BLUE}=== Bot Keeper Logs ===${NC}"
        tail -20 "$SCRIPT_DIR/logs/bot_keeper.log"
    fi
}

show_help() {
    echo -e "${BLUE}Usage: $0 [command]${NC}"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  status      - Show current status"
    echo "  install     - Install systemd service"
    echo "  start       - Start bot keeper service"
    echo "  stop        - Stop bot keeper service"
    echo "  restart     - Restart bot keeper service"
    echo "  manual      - Start bots manually (foreground)"
    echo "  kill        - Stop all FreqTrade processes"
    echo "  logs        - Show recent logs"
    echo "  help        - Show this help"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 install  # Install and enable auto-start"
    echo "  $0 start    # Start the bot keeper"
    echo "  $0 status   # Check if everything is running"
}

# Main script
case "$1" in
    "status")
        print_header
        print_status
        ;;
    "install")
        print_header
        install_service
        ;;
    "start")
        print_header
        start_service
        ;;
    "stop")
        print_header
        stop_service
        ;;
    "restart")
        print_header
        restart_service
        ;;
    "manual")
        print_header
        start_manual
        ;;
    "kill")
        print_header
        stop_manual
        ;;
    "logs")
        print_header
        show_logs
        ;;
    "help"|"--help"|"-h")
        print_header
        show_help
        ;;
    *)
        print_header
        print_status
        echo ""
        show_help
        ;;
esac