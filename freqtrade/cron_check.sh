#!/bin/bash

# 🕐 FreqTrade Cron Check Script
# Τρέχει κάθε 5 λεπτά για να ελέγχει αν τα bots είναι ζωντανά

FREQTRADE_DIR="/home/giwrgosgiai/freqtrade"
LOG_FILE="$FREQTRADE_DIR/logs/cron_check.log"

# Function to log with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Check if monitor script is running
if ! pgrep -f "bot_monitor.sh monitor" > /dev/null; then
    log_message "⚠️ Monitor script not running! Starting it..."
    cd "$FREQTRADE_DIR"
    nohup ./bot_monitor.sh monitor > /dev/null 2>&1 &
    log_message "✅ Monitor script started"
fi

# Check individual bots
declare -A EXPECTED_PORTS=(
    ["8080"]="AI Learning Bot"
    ["8081"]="Altcoin Bot"
    ["8082"]="Scalping Bot"
)

for port in "${!EXPECTED_PORTS[@]}"; do
    if ! curl -s -u "freqtrade:ruriu7AY" "http://localhost:$port/api/v1/ping" > /dev/null 2>&1; then
        log_message "❌ ${EXPECTED_PORTS[$port]} (port $port) not responding"

        # Try to restart via monitor script
        cd "$FREQTRADE_DIR"
        ./bot_monitor.sh restart > /dev/null 2>&1
        log_message "🔄 Triggered bot restart"
        break
    fi
done

# Clean old logs (keep last 1000 lines)
if [ -f "$LOG_FILE" ] && [ $(wc -l < "$LOG_FILE") -gt 1000 ]; then
    tail -1000 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
fi