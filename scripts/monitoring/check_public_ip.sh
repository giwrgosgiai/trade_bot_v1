#!/bin/bash
CURRENT_IP=$(curl -4 -s ifconfig.me)
echo "🌐 Δημόσια IP: $CURRENT_IP"
echo "🔗 FreqTrade: http://$CURRENT_IP:8081"
echo "📱 Local: http://192.168.2.7:8081"
