#!/bin/bash

echo "🌐 Raspberry Pi Network Status"
echo "================================"

# Get current IP
CURRENT_IP=$(ip addr show wlan0 | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
GATEWAY=$(ip route | grep default | awk '{print $3}')

echo "📍 Current IP: $CURRENT_IP"
echo "🚪 Gateway: $GATEWAY"
echo "🔗 FreqTrade UI: http://$CURRENT_IP:8081"
echo "👤 Username: freqtrade"
echo "🔑 Password: ruriu7AY"

# Test connectivity
echo ""
echo "🔍 Testing connectivity..."
if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
    echo "✅ Internet connection: OK"
else
    echo "❌ Internet connection: FAILED"
fi

if curl -s http://localhost:8081/api/v1/ping >/dev/null 2>&1; then
    echo "✅ FreqTrade API: OK"
else
    echo "❌ FreqTrade API: Not running"
fi

echo ""
echo "📋 To access from other devices:"
echo "   http://$CURRENT_IP:8081"