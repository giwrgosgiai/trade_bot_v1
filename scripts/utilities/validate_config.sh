#!/bin/bash

# Config file validator
CONFIG_FILE="/home/giwrgosgiai/user_data/config.json"
TELEGRAM_TOKEN="7295982134:AAF242CTc3vVc9m0qBT3wcF0wljByhlptMQ"
CHAT_ID="930268785"

# Check if config is valid JSON
if ! jq empty "$CONFIG_FILE" 2>/dev/null; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
        -d chat_id="${CHAT_ID}" \
        -d text="🚨 CONFIG ERROR: Invalid JSON in config file!" > /dev/null 2>&1
    exit 1
fi

# Check critical settings
DRY_RUN=$(jq -r '.dry_run' "$CONFIG_FILE")
STAKE_AMOUNT=$(jq -r '.stake_amount' "$CONFIG_FILE")
MAX_TRADES=$(jq -r '.max_open_trades' "$CONFIG_FILE")

# Validate settings
ALERTS=""

if [ "$DRY_RUN" = "false" ]; then
    if (( $(echo "$STAKE_AMOUNT > 50" | bc -l) )); then
        ALERTS="$ALERTS⚠️ High stake amount: $STAKE_AMOUNT\n"
    fi

    if [ "$MAX_TRADES" -gt 5 ]; then
        ALERTS="$ALERTS⚠️ High max trades: $MAX_TRADES\n"
    fi
fi

# Send alerts if any
if [ -n "$ALERTS" ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
        -d chat_id="${CHAT_ID}" \
        -d text="⚠️ CONFIG WARNINGS:
$ALERTS
Dry Run: $DRY_RUN
Stake Amount: $STAKE_AMOUNT
Max Trades: $MAX_TRADES" > /dev/null 2>&1
fi

echo "Config validation completed"
