#!/usr/bin/env python3
"""
NFI5MOHO_WIP Dashboard Launcher
Ξεκινάει το dashboard και το ανοίγει στον browser
"""

import os
import sys
import subprocess
import time
import webbrowser
import requests
from pathlib import Path

def check_dashboard_status(port=8506):
    """Ελέγχει αν το dashboard τρέχει"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_dashboard():
    """Ξεκινάει το NFI5MOHO_WIP dashboard"""
    print("🚀 Starting NFI5MOHO_WIP Strategy Dashboard...")

    # Start the dashboard
    dashboard_script = Path.cwd() / "apps" / "monitoring" / "strategy_monitor.py"

    if not dashboard_script.exists():
        print(f"❌ Dashboard script not found: {dashboard_script}")
        return False

    # Modify the script to run on port 8506
    cmd = [
        "python3", str(dashboard_script)
    ]

    print(f"📝 Starting dashboard...")
    print(f"📁 Working directory: {Path.cwd()}")

    # Start the process in background
    process = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             text=True)

    print(f"🔄 Dashboard started with PID: {process.pid}")

    # Wait for dashboard to start
    print("⏳ Waiting for dashboard to start...")
    for i in range(10):
        time.sleep(2)
        if check_dashboard_status(8505):  # Default port from strategy_monitor.py
            print("✅ Dashboard is running!")
            return True
        print(f"   Checking... ({i+1}/10)")

    print("❌ Dashboard failed to start")
    return False

def create_simple_html():
    """Δημιουργεί ένα απλό HTML αρχείο για το dashboard"""
    html_content = """<!DOCTYPE html>
<html lang="el">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NFI5MOHO_WIP Strategy Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            text-align: center;
        }
        .header {
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .status-card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            backdrop-filter: blur(10px);
        }
        .hyperopt-results {
            background: rgba(76, 175, 80, 0.2);
            border: 2px solid #4CAF50;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
        }
        .links {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .link-card {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 20px;
            text-decoration: none;
            color: white;
            transition: transform 0.3s ease;
        }
        .link-card:hover {
            transform: translateY(-5px);
            background: rgba(255,255,255,0.2);
        }
        .refresh-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            margin: 20px;
        }
        .refresh-btn:hover {
            background: #45a049;
        }
    </style>
    <script>
        function refreshPage() {
            location.reload();
        }

        function checkDashboard() {
            fetch('http://localhost:8505')
                .then(response => {
                    if (response.ok) {
                        document.getElementById('dashboard-status').innerHTML = '🟢 Dashboard Online';
                        document.getElementById('dashboard-link').style.display = 'block';
                    } else {
                        document.getElementById('dashboard-status').innerHTML = '🔴 Dashboard Offline';
                    }
                })
                .catch(() => {
                    document.getElementById('dashboard-status').innerHTML = '🔴 Dashboard Offline';
                });
        }

        setInterval(checkDashboard, 5000);
        window.onload = checkDashboard;
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 NFI5MOHO_WIP Strategy</h1>
            <h2>Trading Dashboard Control Panel</h2>
        </div>

        <div class="status-card">
            <h3 id="dashboard-status">🔄 Checking Dashboard Status...</h3>
            <p>Strategy: <strong>NFI5MOHO_WIP</strong></p>
            <p>Mode: <strong>Dry Run</strong></p>
        </div>

        <div class="hyperopt-results">
            <h3>📊 Hyperopt Results Summary</h3>
            <p><strong>Best Epoch:</strong> 32/139</p>
            <p><strong>Win Rate:</strong> 85.7% (12 wins, 2 losses)</p>
            <p><strong>Total Profit:</strong> 14.38 USDC (2.88%)</p>
            <p><strong>Avg Profit per Trade:</strong> 0.62%</p>
            <p><strong>Max Drawdown:</strong> 0.89%</p>
        </div>

        <div class="status-card">
            <h3>🎯 Optimized Parameters</h3>
            <p>RSI Fast < <strong>35</strong></p>
            <p>RSI > <strong>24</strong></p>
            <p>Price < SMA15 × <strong>0.98</strong></p>
            <p>CTI < <strong>0.75</strong></p>
            <p>RSI Slow <strong>Declining</strong></p>
        </div>

        <button class="refresh-btn" onclick="refreshPage()">🔄 Refresh Status</button>

        <div class="links">
            <a href="http://localhost:8505" class="link-card" id="dashboard-link" style="display:none;">
                <h3>📊 Strategy Monitor</h3>
                <p>Real-time conditions monitoring</p>
                <p>Port: 8505</p>
            </a>

            <a href="http://localhost:8507" class="link-card">
                <h3>🎯 Conditions Monitor</h3>
                <p>Detailed conditions analysis</p>
                <p>Port: 8507</p>
            </a>

            <a href="http://localhost:8080" class="link-card">
                <h3>🤖 FreqTrade API</h3>
                <p>Bot control interface</p>
                <p>Port: 8080</p>
            </a>
        </div>

        <div class="status-card">
            <h3>🚀 Quick Start</h3>
            <p>1. Run: <code>python3 scripts/core/start_nfi5moho_bot.py</code></p>
            <p>2. Run: <code>python3 apps/monitoring/strategy_monitor.py</code></p>
            <p>3. Access dashboards above</p>
        </div>
    </div>
</body>
</html>"""

    # Save to file
    html_file = Path.cwd() / "nfi5moho_dashboard.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return html_file

def main():
    """Main function"""
    print("=" * 60)
    print("🎯 NFI5MOHO_WIP Strategy Dashboard Launcher")
    print("=" * 60)

    # Create simple HTML dashboard
    html_file = create_simple_html()
    print(f"✅ Created dashboard file: {html_file}")

    # Try to start the Python dashboard
    print("\n🔄 Attempting to start Python dashboard...")
    dashboard_started = start_dashboard()

    # Open the HTML file in browser
    print(f"\n🌐 Opening dashboard in browser...")
    try:
        webbrowser.open(f"file://{html_file}")
        print("✅ Dashboard opened in browser!")
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print(f"📂 Manually open: {html_file}")

    if dashboard_started:
        print("\n🎉 Dashboard is running!")
        print("📊 Python Dashboard: http://localhost:8504")
    else:
        print("\n⚠️  Python dashboard not started - using HTML version")

    print(f"📄 HTML Dashboard: file://{html_file}")
    print("\n💡 The HTML dashboard will auto-refresh and show status")

if __name__ == "__main__":
    main()