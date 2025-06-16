#!/bin/bash

# Install systemd service for FreqTrade monitoring
# Αυτό το script δημιουργεί systemd service για αυτόματη εκκίνηση

echo "🔧 Installing FreqTrade systemd service..."

# Create systemd service file
sudo tee /etc/systemd/system/freqtrade-monitor.service > /dev/null << 'EOF'
[Unit]
Description=FreqTrade Bot Monitor
After=network.target
Wants=network.target

[Service]
Type=simple
User=giwrgosgiai
Group=giwrgosgiai
WorkingDirectory=/home/giwrgosgiai
Environment=PATH=/home/giwrgosgiai/myenv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/giwrgosgiai/scripts/bot_monitor.sh daemon
ExecStop=/bin/kill -TERM $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=freqtrade-monitor

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/giwrgosgiai

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable freqtrade-monitor.service

echo "✅ Systemd service installed and enabled"
echo ""
echo "📚 Service commands:"
echo "• Start: sudo systemctl start freqtrade-monitor"
echo "• Stop: sudo systemctl stop freqtrade-monitor"
echo "• Status: sudo systemctl status freqtrade-monitor"
echo "• Logs: sudo journalctl -u freqtrade-monitor -f"
echo "• Restart: sudo systemctl restart freqtrade-monitor"

# Create startup script for boot
sudo tee /etc/rc.local > /dev/null << 'EOF'
#!/bin/bash
# Auto-start FreqTrade on boot

# Wait for network
sleep 30

# Start FreqTrade monitor service
systemctl start freqtrade-monitor

exit 0
EOF

sudo chmod +x /etc/rc.local

echo "✅ Boot startup configured"