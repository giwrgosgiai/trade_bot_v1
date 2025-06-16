#!/bin/bash

# System monitoring script
TELEGRAM_TOKEN="7295982134:AAF242CTc3vVc9m0qBT3wcF0wljByhlptMQ"
CHAT_ID="930268785"

# Check system health
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
DISK_USAGE=$(df -h / | awk 'NR==2{print $5}' | cut -d'%' -f1)
LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}')

# Check for suspicious processes
SUSPICIOUS_PROCS=$(ps aux | grep -E "(bitcoin|mining|crypto)" | grep -v grep | wc -l)

# Check network connections
NETWORK_CONNECTIONS=$(netstat -an | grep :8081 | wc -l)

# Alert conditions
ALERT=""

if (( $(echo "$CPU_USAGE > 90" | bc -l) )); then
    ALERT="$ALERT🔥 High CPU: ${CPU_USAGE}%\n"
fi

if (( $(echo "$MEMORY_USAGE > 90" | bc -l) )); then
    ALERT="$ALERT🧠 High Memory: ${MEMORY_USAGE}%\n"
fi

if [ "$DISK_USAGE" -gt 95 ]; then
    ALERT="$ALERT💾 High Disk: ${DISK_USAGE}%\n"
fi

if [ "$SUSPICIOUS_PROCS" -gt 0 ]; then
    ALERT="$ALERT⚠️ Suspicious processes detected: $SUSPICIOUS_PROCS\n"
fi

if [ "$NETWORK_CONNECTIONS" -gt 10 ]; then
    ALERT="$ALERT🌐 Many API connections: $NETWORK_CONNECTIONS\n"
fi

# Send alert if needed
if [ -n "$ALERT" ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
        -d chat_id="${CHAT_ID}" \
        -d text="🚨 SYSTEM ALERT:
$ALERT
CPU: ${CPU_USAGE}%
Memory: ${MEMORY_USAGE}%
Disk: ${DISK_USAGE}%
Load: ${LOAD_AVG}" > /dev/null 2>&1
fi
