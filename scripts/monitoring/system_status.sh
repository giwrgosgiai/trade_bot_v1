#!/bin/bash

# FreqTrade System Status Script
# Εμφανίζει την κατάσταση όλου του συστήματος

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🤖 FreqTrade System Status Dashboard${NC}"
echo "=============================================="
echo ""

# 1. Bot Status
echo -e "${CYAN}📊 Bot Status${NC}"
echo "----------------------------------------"

if pgrep -f "freqtrade.*trade" > /dev/null; then
    BOT_PID=$(pgrep -f "freqtrade.*trade")
    BOT_UPTIME=$(ps -o etime= -p "$BOT_PID" 2>/dev/null | tr -d ' ')
    echo -e "• Status: ${GREEN}✅ RUNNING${NC} (PID: $BOT_PID)"
    echo -e "• Uptime: ${GREEN}$BOT_UPTIME${NC}"

    # Check API
    if curl -s -u "freqtrade:ruriu7AY" "http://localhost:8081/api/v1/ping" > /dev/null 2>&1; then
        echo -e "• API: ${GREEN}✅ RESPONSIVE${NC}"

        # Get balance
        BALANCE_RESPONSE=$(curl -s -u "freqtrade:ruriu7AY" "http://localhost:8081/api/v1/balance" 2>/dev/null)
        if [ $? -eq 0 ]; then
            USDC_BALANCE=$(echo "$BALANCE_RESPONSE" | jq -r '.currencies[] | select(.currency=="USDC") | .free' 2>/dev/null)
            TOTAL_BALANCE=$(echo "$BALANCE_RESPONSE" | jq -r '.total' 2>/dev/null)
            echo -e "• Balance: ${GREEN}$USDC_BALANCE USDC${NC} (Total: $TOTAL_BALANCE)"
        fi

        # Get open trades
        TRADES_RESPONSE=$(curl -s -u "freqtrade:ruriu7AY" "http://localhost:8081/api/v1/status" 2>/dev/null)
        if [ $? -eq 0 ]; then
            OPEN_TRADES=$(echo "$TRADES_RESPONSE" | jq '. | length' 2>/dev/null)
            echo -e "• Open Trades: ${GREEN}$OPEN_TRADES${NC}"
        fi
    else
        echo -e "• API: ${RED}❌ NOT RESPONDING${NC}"
    fi
else
    echo -e "• Status: ${RED}❌ NOT RUNNING${NC}"
fi

echo ""

# 2. Monitor Status
echo -e "${CYAN}🔄 Monitor Status${NC}"
echo "----------------------------------------"

if pgrep -f "bot_monitor.sh" > /dev/null; then
    MONITOR_PID=$(pgrep -f "bot_monitor.sh")
    MONITOR_UPTIME=$(ps -o etime= -p "$MONITOR_PID" 2>/dev/null | tr -d ' ')
    echo -e "• Monitor: ${GREEN}✅ RUNNING${NC} (PID: $MONITOR_PID)"
    echo -e "• Uptime: ${GREEN}$MONITOR_UPTIME${NC}"
else
    echo -e "• Monitor: ${RED}❌ NOT RUNNING${NC}"
fi

# Check systemd service
if systemctl is-enabled freqtrade-monitor.service > /dev/null 2>&1; then
    if systemctl is-active freqtrade-monitor.service > /dev/null 2>&1; then
        echo -e "• Systemd Service: ${GREEN}✅ ACTIVE${NC}"
    else
        echo -e "• Systemd Service: ${YELLOW}⚠️ ENABLED BUT INACTIVE${NC}"
    fi
else
    echo -e "• Systemd Service: ${RED}❌ NOT ENABLED${NC}"
fi

echo ""

# 3. Security Status
echo -e "${CYAN}🔒 Security Status${NC}"
echo "----------------------------------------"

# Check emergency stop
if [ -f "/home/giwrgosgiai/.emergency_stop" ]; then
    echo -e "• Emergency Stop: ${RED}🚨 ACTIVE${NC}"
else
    echo -e "• Emergency Stop: ${GREEN}✅ INACTIVE${NC}"
fi

# Check config integrity
if jq empty "/home/giwrgosgiai/user_data/config.json" 2>/dev/null; then
    echo -e "• Config File: ${GREEN}✅ VALID${NC}"

    DRY_RUN=$(jq -r '.dry_run' "/home/giwrgosgiai/user_data/config.json")
    STAKE_AMOUNT=$(jq -r '.stake_amount' "/home/giwrgosgiai/user_data/config.json")
    MAX_TRADES=$(jq -r '.max_open_trades' "/home/giwrgosgiai/user_data/config.json")

    if [ "$DRY_RUN" = "false" ]; then
        echo -e "• Trading Mode: ${YELLOW}⚠️ LIVE TRADING${NC}"
    else
        echo -e "• Trading Mode: ${GREEN}✅ DRY RUN${NC}"
    fi

    echo -e "• Stake Amount: ${GREEN}$STAKE_AMOUNT USDC${NC}"
    echo -e "• Max Trades: ${GREEN}$MAX_TRADES${NC}"
else
    echo -e "• Config File: ${RED}❌ INVALID${NC}"
fi

# Check file permissions
CONFIG_PERMS=$(stat -c "%a" "/home/giwrgosgiai/user_data/config.json" 2>/dev/null)
if [ "$CONFIG_PERMS" = "600" ]; then
    echo -e "• File Permissions: ${GREEN}✅ SECURE${NC}"
else
    echo -e "• File Permissions: ${YELLOW}⚠️ $CONFIG_PERMS${NC}"
fi

echo ""

# 4. System Resources
echo -e "${CYAN}📊 System Resources${NC}"
echo "----------------------------------------"

CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
DISK_USAGE=$(df -h / | awk 'NR==2{print $5}' | cut -d'%' -f1)
LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | sed 's/^[ \t]*//')

# Color code based on usage
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    CPU_COLOR=$RED
elif (( $(echo "$CPU_USAGE > 60" | bc -l) )); then
    CPU_COLOR=$YELLOW
else
    CPU_COLOR=$GREEN
fi

if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
    MEM_COLOR=$RED
elif (( $(echo "$MEMORY_USAGE > 60" | bc -l) )); then
    MEM_COLOR=$YELLOW
else
    MEM_COLOR=$GREEN
fi

if [ "$DISK_USAGE" -gt 80 ]; then
    DISK_COLOR=$RED
elif [ "$DISK_USAGE" -gt 60 ]; then
    DISK_COLOR=$YELLOW
else
    DISK_COLOR=$GREEN
fi

echo -e "• CPU Usage: ${CPU_COLOR}${CPU_USAGE}%${NC}"
echo -e "• Memory Usage: ${MEM_COLOR}${MEMORY_USAGE}%${NC}"
echo -e "• Disk Usage: ${DISK_COLOR}${DISK_USAGE}%${NC}"
echo -e "• Load Average: ${GREEN}$LOAD_AVG${NC}"

echo ""

# 5. Network Status
echo -e "${CYAN}🌐 Network Status${NC}"
echo "----------------------------------------"

if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    echo -e "• Internet: ${GREEN}✅ CONNECTED${NC}"
else
    echo -e "• Internet: ${RED}❌ DISCONNECTED${NC}"
fi

if curl -s https://api.binance.com/api/v3/ping > /dev/null 2>&1; then
    echo -e "• Binance API: ${GREEN}✅ REACHABLE${NC}"
else
    echo -e "• Binance API: ${RED}❌ UNREACHABLE${NC}"
fi

# Check API connections
API_CONNECTIONS=$(netstat -an 2>/dev/null | grep :8081 | wc -l)
echo -e "• API Connections: ${GREEN}$API_CONNECTIONS${NC}"

echo ""

# 6. Recent Activity
echo -e "${CYAN}📝 Recent Activity${NC}"
echo "----------------------------------------"

# Check recent logs
if [ -f "/home/giwrgosgiai/logs/freqtrade_secure.log" ]; then
    LAST_LOG=$(tail -1 "/home/giwrgosgiai/logs/freqtrade_secure.log" 2>/dev/null | cut -d' ' -f1-2)
    echo -e "• Last Log Entry: ${GREEN}$LAST_LOG${NC}"
fi

# Check recent backups
LATEST_BACKUP=$(ls -t /home/giwrgosgiai/backups/startup/pre_startup_*.tar.gz 2>/dev/null | head -1)
if [ -n "$LATEST_BACKUP" ]; then
    BACKUP_DATE=$(basename "$LATEST_BACKUP" | sed 's/pre_startup_\(.*\)\.tar\.gz/\1/')
    echo -e "• Latest Backup: ${GREEN}$BACKUP_DATE${NC}"
fi

# Check cron jobs
CRON_JOBS=$(crontab -l 2>/dev/null | grep -v "^#" | wc -l)
echo -e "• Scheduled Jobs: ${GREEN}$CRON_JOBS${NC}"

echo ""

# 7. Quick Actions
echo -e "${PURPLE}⚡ Quick Actions${NC}"
echo "----------------------------------------"
echo "• View logs: tail -f logs/freqtrade_secure.log"
echo "• Emergency stop: scripts/emergency_stop.sh"
echo "• Manual backup: scripts/backup_system.sh"
echo "• Restart monitor: scripts/bot_monitor.sh stop && scripts/bot_monitor.sh start"
echo "• Check balance: curl -u 'freqtrade:ruriu7AY' http://localhost:8081/api/v1/balance"

echo ""
echo -e "${BLUE}=============================================="
echo -e "System Status Check Completed at $(date)"
echo -e "===============================================${NC}"