#!/bin/bash

# 🚀 FreqTrade Monitor Installation Script
# Εγκαθιστά το σύστημα παρακολούθησης και auto-restart

FREQTRADE_DIR="/home/giwrgosgiai/freqtrade"
SERVICE_FILE="freqtrade-monitor.service"

echo "🚀 Installing FreqTrade Bot Monitor System..."
echo "=============================================="

# Make scripts executable
chmod +x "$FREQTRADE_DIR/bot_monitor.sh"
echo "✅ Made bot_monitor.sh executable"

# Create log directories
mkdir -p "$FREQTRADE_DIR/logs"
mkdir -p "$FREQTRADE_DIR/pids"
echo "✅ Created log and pid directories"

# Install systemd service (optional)
if command -v systemctl &> /dev/null; then
    echo ""
    echo "🔧 Do you want to install as a systemd service? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        sudo cp "$FREQTRADE_DIR/$SERVICE_FILE" /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable freqtrade-monitor.service
        echo "✅ Systemd service installed and enabled"
        echo "   Use: sudo systemctl start freqtrade-monitor"
        echo "   Use: sudo systemctl status freqtrade-monitor"
    fi
fi

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "📋 Available Commands:"
echo "  ./bot_monitor.sh start    - Start all bots"
echo "  ./bot_monitor.sh stop     - Stop all bots"
echo "  ./bot_monitor.sh restart  - Restart all bots"
echo "  ./bot_monitor.sh status   - Show bot status"
echo "  ./bot_monitor.sh monitor  - Start monitoring (keeps bots alive)"
echo ""
echo "🚀 To start monitoring now:"
echo "  cd $FREQTRADE_DIR"
echo "  ./bot_monitor.sh monitor"
echo ""
echo "📊 Web Interfaces will be available at:"
echo "  Bot 1: http://localhost:8080"
echo "  Bot 2: http://localhost:8081"
echo "  Bot 3: http://localhost:8082"
echo "  Username: freqtrade | Password: ruriu7AY"