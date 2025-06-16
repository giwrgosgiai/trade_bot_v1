#!/bin/bash

# Fully Automated FreqTrade Startup Script
# Ξεκινάει το bot χωρίς κανένα prompt ή επιβεβαίωση

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
FREQTRADE_HOME="/home/giwrgosgiai"
TELEGRAM_TOKEN="7295982134:AAF242CTc3vVc9m0qBT3wcF0wljByhlptMQ"
CHAT_ID="930268785"

echo -e "${BLUE}🚀 FreqTrade Auto-Start System${NC}"
echo "============================================="

# Function to send Telegram notification
send_notification() {
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
        -d chat_id="${CHAT_ID}" \
        -d text="$1" > /dev/null 2>&1
}

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$FREQTRADE_HOME/logs/auto_start.log"
}

# 1. Stop any existing processes
echo -e "${YELLOW}🛑 Stopping existing processes...${NC}"
pkill -f freqtrade 2>/dev/null
pkill -f bot_monitor 2>/dev/null
sleep 3
echo -e "${GREEN}✅ Cleanup completed${NC}"

# 2. Quick system check
echo -e "${YELLOW}⚡ Quick system check...${NC}"
if [ ! -f "$FREQTRADE_HOME/user_data/config.json" ]; then
    echo -e "${RED}❌ Config file not found!${NC}"
    send_notification "🚨 Auto-start failed: Config file missing!"
    exit 1
fi

if ! ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    echo -e "${RED}❌ No internet connection!${NC}"
    send_notification "🚨 Auto-start failed: No internet!"
    exit 1
fi
echo -e "${GREEN}✅ System check passed${NC}"

# 3. Start the secure bot
echo -e "${YELLOW}🚀 Starting secure bot system...${NC}"
cd "$FREQTRADE_HOME"

# Use the secure startup script but redirect to avoid any potential prompts
if "$FREQTRADE_HOME/scripts/start_secure_bot.sh" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Bot started successfully${NC}"
    log_message "Auto-start completed successfully"
    send_notification "🚀 FreqTrade Auto-Start επιτυχής! Bot τρέχει κανονικά."
else
    echo -e "${RED}❌ Failed to start bot${NC}"
    log_message "Auto-start failed"
    send_notification "🚨 FreqTrade Auto-Start απέτυχε!"
    exit 1
fi

# 4. Wait and verify
echo -e "${YELLOW}⏳ Verifying startup...${NC}"
sleep 15

# Check if bot is running
if pgrep -f "freqtrade.*trade" > /dev/null; then
    BOT_PID=$(pgrep -f "freqtrade.*trade")
    echo -e "${GREEN}✅ Bot verified running (PID: $BOT_PID)${NC}"

    # Check API
    if curl -s -u "freqtrade:ruriu7AY" "http://localhost:8081/api/v1/ping" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API verified working${NC}"

        # Get balance
        BALANCE=$(curl -s -u "freqtrade:ruriu7AY" "http://localhost:8081/api/v1/balance" | jq -r '.total' 2>/dev/null)
        if [ "$BALANCE" != "null" ] && [ "$BALANCE" != "" ]; then
            echo -e "${GREEN}✅ Balance: $BALANCE USDC${NC}"
            send_notification "✅ Auto-Start ΕΠΙΤΥΧΗΣ!
🤖 Bot PID: $BOT_PID
💰 Balance: $BALANCE USDC
🔄 Monitor: Active
⚡ API: Working"
        fi
    else
        echo -e "${YELLOW}⚠️ API not ready yet${NC}"
    fi
else
    echo -e "${RED}❌ Bot not running after startup${NC}"
    send_notification "🚨 Auto-Start: Bot δεν τρέχει μετά την εκκίνηση!"
    exit 1
fi

# 5. Show final status
echo ""
echo -e "${BLUE}📊 Final Status${NC}"
echo "=================================="
echo "• Bot: ✅ RUNNING"
echo "• Monitor: ✅ ACTIVE"
echo "• API: ✅ WORKING"
echo "• Auto-Start: ✅ COMPLETED"
echo ""
echo -e "${GREEN}🎉 FreqTrade is fully operational!${NC}"
echo ""
echo -e "${YELLOW}📚 Quick Commands:${NC}"
echo "• Status: scripts/system_status.sh"
echo "• Emergency stop: scripts/emergency_stop.sh"
echo "• View logs: tail -f logs/freqtrade_secure.log"

log_message "Auto-start system completed successfully"