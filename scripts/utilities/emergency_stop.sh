#!/bin/bash

# Emergency stop script - stops all trading immediately
TELEGRAM_TOKEN="7295982134:AAF242CTc3vVc9m0qBT3wcF0wljByhlptMQ"
CHAT_ID="930268785"

echo "🚨 EMERGENCY STOP ACTIVATED!"

# Stop all FreqTrade processes
pkill -f freqtrade
pkill -f bot_monitor

# Stop Analytics Dashboard
pkill -f analytics_dashboard.py

# Send emergency notification
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
    -d chat_id="${CHAT_ID}" \
    -d text="🚨 EMERGENCY STOP ACTIVATED! All trading stopped!" > /dev/null 2>&1

# Create emergency flag file
touch /home/giwrgosgiai/.emergency_stop

echo "All trading processes stopped!"
echo "To resume, delete /home/giwrgosgiai/.emergency_stop and restart manually"
