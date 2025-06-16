#!/bin/bash

# Automated backup system for FreqTrade
BACKUP_DIR="/home/giwrgosgiai/backups/security"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/freqtrade_backup_$DATE.tar.gz"

# Create backup
tar -czf "$BACKUP_FILE" \
    /home/giwrgosgiai/user_data/config.json \
    /home/giwrgosgiai/user_data/strategies/ \
    /home/giwrgosgiai/user_data/*.sqlite \
    /home/giwrgosgiai/logs/ \
    2>/dev/null

# Keep only last 10 backups
cd "$BACKUP_DIR"
ls -t freqtrade_backup_*.tar.gz | tail -n +11 | xargs -r rm

# Send notification
curl -s -X POST "https://api.telegram.org/bot7295982134:AAF242CTc3vVc9m0qBT3wcF0wljByhlptMQ/sendMessage" \
    -d chat_id="930268785" \
    -d text="💾 Backup completed: $BACKUP_FILE" > /dev/null 2>&1

echo "Backup completed: $BACKUP_FILE"
