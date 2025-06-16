#!/bin/bash

# FreqTrade Command Reference
# Εμφανίζει όλες τις διαθέσιμες εντολές για το FreqTrade system

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🤖 FreqTrade Command Reference${NC}"
echo "=============================================="
echo ""

echo -e "${CYAN}🚀 STARTUP COMMANDS${NC}"
echo "----------------------------------------------"
echo -e "${GREEN}• scripts/auto_start_bot.sh${NC}          - Πλήρως αυτόματη εκκίνηση (ΧΩΡΙΣ prompts)"
echo -e "${GREEN}• scripts/start_secure_bot.sh${NC}        - Ασφαλής εκκίνηση με ελέγχους"
echo -e "${GREEN}• scripts/bot_monitor.sh start${NC}       - Ξεκίνημα monitoring system"
echo ""

echo -e "${CYAN}🛑 STOP COMMANDS${NC}"
echo "----------------------------------------------"
echo -e "${RED}• scripts/emergency_stop.sh${NC}          - ΕΠΕΙΓΟΝ ΣΤΑΜΑΤΗΜΑ (όλα)"
echo -e "${RED}• pkill -f freqtrade${NC}                 - Σταμάτημα bot μόνο"
echo -e "${RED}• scripts/bot_monitor.sh stop${NC}        - Σταμάτημα monitor μόνο"
echo ""

echo -e "${CYAN}📊 STATUS & MONITORING${NC}"
echo "----------------------------------------------"
echo -e "${YELLOW}• scripts/system_status.sh${NC}          - Πλήρης κατάσταση συστήματος"
echo -e "${YELLOW}• curl -u 'freqtrade:ruriu7AY' http://localhost:8081/api/v1/status${NC}"
echo -e "${YELLOW}• curl -u 'freqtrade:ruriu7AY' http://localhost:8081/api/v1/balance${NC}"
echo -e "${YELLOW}• tail -f logs/freqtrade_secure.log${NC}  - Live logs"
echo ""

echo -e "${CYAN}🔒 SECURITY & BACKUP${NC}"
echo "----------------------------------------------"
echo -e "${PURPLE}• scripts/security_hardening.sh${NC}     - Ενίσχυση ασφάλειας"
echo -e "${PURPLE}• scripts/backup_system.sh${NC}          - Χειροκίνητο backup"
echo -e "${PURPLE}• scripts/validate_config.sh${NC}        - Έλεγχος config"
echo ""

echo -e "${CYAN}⚙️ CONFIGURATION${NC}"
echo "----------------------------------------------"
echo -e "${BLUE}• nano user_data/config.json${NC}         - Επεξεργασία config"
echo -e "${BLUE}• jq . user_data/config.json${NC}         - Προβολή config (formatted)"
echo ""

echo -e "${CYAN}📈 TRADING INFO${NC}"
echo "----------------------------------------------"
echo -e "${GREEN}• curl -u 'freqtrade:ruriu7AY' http://localhost:8081/api/v1/trades${NC}     - Όλα τα trades"
echo -e "${GREEN}• curl -u 'freqtrade:ruriu7AY' http://localhost:8081/api/v1/profit${NC}     - Κέρδη/ζημιές"
echo -e "${GREEN}• curl -u 'freqtrade:ruriu7AY' http://localhost:8081/api/v1/performance${NC} - Performance"
echo ""

echo -e "${CYAN}🔧 MAINTENANCE${NC}"
echo "----------------------------------------------"
echo -e "${YELLOW}• scripts/system_monitor.sh${NC}         - Έλεγχος συστήματος"
echo -e "${YELLOW}• sudo systemctl status freqtrade-monitor${NC} - Systemd status"
echo -e "${YELLOW}• crontab -l${NC}                        - Scheduled jobs"
echo ""

echo -e "${CYAN}📱 TELEGRAM COMMANDS${NC}"
echo "----------------------------------------------"
echo "Στείλε στο Telegram bot:"
echo -e "${GREEN}• /status${NC}     - Κατάσταση bot"
echo -e "${GREEN}• /balance${NC}    - Balance"
echo -e "${GREEN}• /profit${NC}     - Κέρδη"
echo -e "${GREEN}• /trades${NC}     - Ανοιχτά trades"
echo -e "${GREEN}• /stop${NC}       - Σταμάτημα bot"
echo -e "${GREEN}• /start${NC}      - Εκκίνηση bot"
echo ""

echo -e "${CYAN}🆘 EMERGENCY PROCEDURES${NC}"
echo "----------------------------------------------"
echo -e "${RED}1. ΠΑΓΩΜΑ TRADING:${NC} scripts/emergency_stop.sh"
echo -e "${RED}2. ΕΠΑΝΕΚΚΙΝΗΣΗ:${NC} scripts/auto_start_bot.sh"
echo -e "${RED}3. ΕΛΕΓΧΟΣ ΖΗΜΙΩΝ:${NC} curl -u 'freqtrade:ruriu7AY' http://localhost:8081/api/v1/profit"
echo -e "${RED}4. BACKUP:${NC} scripts/backup_system.sh"
echo ""

echo -e "${CYAN}📂 IMPORTANT FILES${NC}"
echo "----------------------------------------------"
echo -e "${BLUE}• user_data/config.json${NC}              - Κύρια διαμόρφωση"
echo -e "${BLUE}• logs/freqtrade_secure.log${NC}          - Bot logs"
echo -e "${BLUE}• logs/bot_monitor.log${NC}               - Monitor logs"
echo -e "${BLUE}• logs/security.log${NC}                  - Security logs"
echo -e "${BLUE}• backups/security/${NC}                  - Αυτόματα backups"
echo ""

echo -e "${CYAN}🌐 WEB INTERFACE${NC}"
echo "----------------------------------------------"
echo -e "${GREEN}• FreqUI:${NC} http://localhost:8080 (αν εγκατεστημένο)"
echo -e "${GREEN}• API Docs:${NC} http://localhost:8081/docs"
echo ""

# Show current status
echo -e "${CYAN}📊 CURRENT STATUS${NC}"
echo "----------------------------------------------"
if pgrep -f "freqtrade.*trade" > /dev/null; then
    BOT_PID=$(pgrep -f "freqtrade.*trade")
    echo -e "${GREEN}• Bot: ✅ RUNNING (PID: $BOT_PID)${NC}"
else
    echo -e "${RED}• Bot: ❌ NOT RUNNING${NC}"
fi

if pgrep -f "bot_monitor" > /dev/null; then
    MONITOR_PID=$(pgrep -f "bot_monitor")
    echo -e "${GREEN}• Monitor: ✅ RUNNING (PID: $MONITOR_PID)${NC}"
else
    echo -e "${RED}• Monitor: ❌ NOT RUNNING${NC}"
fi

if curl -s -u "freqtrade:ruriu7AY" "http://localhost:8081/api/v1/ping" > /dev/null 2>&1; then
    echo -e "${GREEN}• API: ✅ RESPONSIVE${NC}"
else
    echo -e "${RED}• API: ❌ NOT RESPONDING${NC}"
fi

echo ""
echo -e "${BLUE}=============================================="
echo -e "💡 Tip: Χρησιμοποίησε 'scripts/auto_start_bot.sh' για πλήρως αυτόματη εκκίνηση!"
echo -e "=============================================="${NC}