#!/usr/bin/env python3
"""
🚀 Master Trading Command Center Launcher
Ξεκινάει το ενιαίο κέντρο ελέγχου που συνδυάζει όλες τις λειτουργίες
"""

import os
import sys
import subprocess
import time
import webbrowser
import requests
from pathlib import Path

def check_dashboard_status(port=8500):
    """Ελέγχει αν το dashboard τρέχει"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=5)
        return response.status_code == 200
    except:
        return False

def stop_old_dashboards():
    """Σταματάει τα παλιά dashboards"""
    old_ports = [8503, 8504, 8507, 5001, 8000, 8001, 8501]

    print("🛑 Stopping old dashboards...")
    for port in old_ports:
        try:
            # Kill processes using these ports
            subprocess.run(['lsof', '-ti', f':{port}'],
                         capture_output=True, text=True, check=False)
            result = subprocess.run(['lsof', '-ti', f':{port}'],
                                  capture_output=True, text=True, check=False)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        subprocess.run(['kill', '-9', pid], check=False)
                        print(f"   ✅ Stopped process on port {port}")
        except:
            pass

def start_unified_dashboard():
    """Ξεκινάει το unified dashboard"""
    print("🚀 Starting Master Trading Command Center...")
    print("📊 Port: 8500")
    print("🌐 URL: http://localhost:8500")
    print("🎯 Combining all dashboards into one!")
    print("-" * 50)

    # Check if already running
    if check_dashboard_status(8500):
        print("⚠️  Dashboard is already running on port 8500")
        choice = input("Do you want to restart it? (y/n): ").lower()
        if choice not in ['y', 'yes', 'ναι', 'ν']:
            print("👋 Cancelled")
            return

        # Stop existing dashboard
        try:
            result = subprocess.run(['lsof', '-ti', ':8500'],
                                  capture_output=True, text=True, check=False)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        subprocess.run(['kill', '-9', pid], check=False)
                print("🛑 Stopped existing dashboard")
                time.sleep(2)
        except:
            pass

    # Stop old dashboards
    stop_old_dashboards()

    # Start the unified dashboard
    dashboard_script = Path("apps/monitoring/unified_master_dashboard.py")

    if not dashboard_script.exists():
        print(f"❌ Dashboard script not found: {dashboard_script}")
        return False

    print("🚀 Starting unified dashboard...")

    # Start the process
    try:
        process = subprocess.Popen([
            sys.executable, str(dashboard_script)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        print(f"🔄 Dashboard started with PID: {process.pid}")

        # Wait for dashboard to start
        print("⏳ Waiting for dashboard to start...")
        for i in range(15):
            time.sleep(2)
            if check_dashboard_status(8500):
                print("✅ Dashboard is running!")

                # Open browser
                try:
                    print("🌐 Opening browser...")
                    webbrowser.open('http://localhost:8500')
                except:
                    pass

                print("\n" + "="*60)
                print("🚀 MASTER TRADING COMMAND CENTER STARTED!")
                print("="*60)
                print("📊 URL: http://localhost:8500")
                print("🎯 Features:")
                print("   • System Status Monitoring (με Telegram Bot Status)")
                print("   • Strategy Conditions Monitor (22 pairs)")
                print("   • Portfolio Analytics & Performance")
                print("   • Celebrity News Monitoring 🌟")
                print("   • Market Sentiment Analysis 📈")
                print("   • Risk Management Metrics ⚠️")
                print("   • Trading Signals Generator 🚀")
                print("   • Auto Trading Controls 🤖")
                print("   • Emergency Stop & Force Trade")
                print("   • Live Telegram Bot Monitoring 📱")
                print("   • Real-time Updates (10s background)")
                print("="*60)
                print("⏹️  Press Ctrl+C to stop the dashboard")
                print("🔄 Auto-refresh every 30 seconds")
                print("="*60)

                # Keep the process running
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Stopping dashboard...")
                    process.terminate()
                    print("👋 Dashboard stopped")

                return True

            print(f"   Checking... ({i+1}/15)")

        print("❌ Dashboard failed to start")
        process.terminate()
        return False

    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        return False

def main():
    """Main function"""
    print("🚀 MASTER TRADING COMMAND CENTER LAUNCHER")
    print("="*50)
    print("🎯 Συνδυάζει όλα τα dashboards σε ένα!")
    print("📊 Dashboards που αντικαθιστά:")
    print("   • System Status Dashboard (8503) ✅")
    print("   • Strategy Monitor (8504) ✅")
    print("   • Conditions Monitor (8507) ✅")
    print("   • Enhanced Trading UI (5001) ✅")
    print("   • Strategy Dashboard (8000) ✅")
    print("   • Advanced Trading UI (8001) ✅")
    print("   • Master Control Dashboard (8501) ✅")
    print("🆕 Νέα Features:")
    print("   • Celebrity News Monitoring 🌟")
    print("   • Market Sentiment Analysis 📈")
    print("   • Risk Management Metrics ⚠️")
    print("   • Trading Signals Generator 🚀")
    print("   • Auto Trading Controls 🤖")
    print("   • Live Telegram Bot Monitoring 📱")
    print("="*50)
    print()

    try:
        start_unified_dashboard()
    except KeyboardInterrupt:
        print("\n👋 Cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()