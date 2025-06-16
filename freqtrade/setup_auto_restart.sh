#!/bin/bash

# 🔧 FreqTrade Auto-Restart System Setup
# Εγκαθιστά το σύστημα αυτόματης επανεκκίνησης των bots

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="freqtrade-monitor"

echo "🚀 Setting up FreqTrade Auto-Restart System..."

# Make scripts executable
chmod +x "$SCRIPT_DIR/bot_monitor.sh"

# Create necessary directories
mkdir -p "$SCRIPT_DIR/logs" "$SCRIPT_DIR/pids"

# Stop any existing freqtrade processes
echo "🛑 Stopping existing FreqTrade processes..."
pkill -f "freqtrade trade" 2>/dev/null || true

# Install systemd service (requires sudo)
if command -v systemctl >/dev/null 2>&1; then
    echo "📦 Installing systemd service..."

    # Copy service file to systemd directory
    sudo cp "$SCRIPT_DIR/freqtrade-monitor.service" "/etc/systemd/system/"

    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME

    echo "✅ Systemd service installed and enabled"
    echo "🔄 Starting service..."

    sudo systemctl start $SERVICE_NAME

    echo "📊 Service status:"
    sudo systemctl status $SERVICE_NAME --no-pager -l

else
    echo "⚠️  Systemd not available. Starting monitor manually..."
    nohup "$SCRIPT_DIR/bot_monitor.sh" monitor > "$SCRIPT_DIR/logs/monitor_startup.log" 2>&1 &
    echo "✅ Monitor started in background"
fi

echo ""
echo "🎉 Setup Complete!"
echo "==================="
echo ""
echo "📊 Check status: ./bot_monitor.sh status"
echo "🔍 View logs: tail -f logs/monitor.log"
echo "🛑 Stop all: ./bot_monitor.sh stop"
echo "🚀 Start all: ./bot_monitor.sh start"
echo ""
echo "🌐 Web Interfaces:"
echo "   Bot 1: http://localhost:8080"
echo "   Bot 2: http://localhost:8081"
echo "   Bot 3: http://localhost:8082"
echo "   Credentials: freqtrade / ruriu7AY"
echo ""

if command -v systemctl >/dev/null 2>&1; then
    echo "🔧 Systemd Commands:"
    echo "   sudo systemctl status $SERVICE_NAME"
    echo "   sudo systemctl stop $SERVICE_NAME"
    echo "   sudo systemctl start $SERVICE_NAME"
    echo "   sudo systemctl restart $SERVICE_NAME"
    echo "   sudo journalctl -u $SERVICE_NAME -f"
fi

echo ""
echo "✅ Your bots will now automatically restart if they crash!"