#!/usr/bin/env python3
"""
Dashboard Status Checker
Δείχνει όλα τα διαθέσιμα dashboards και την κατάστασή τους
"""

import requests
import webbrowser
from datetime import datetime

def check_dashboard(port, name, description=""):
    """Ελέγχει αν ένα dashboard τρέχει"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=3)
        if response.status_code == 200:
            status = "🟢 ONLINE"
            url = f"http://localhost:{port}"
        else:
            status = f"🔴 ERROR ({response.status_code})"
            url = f"http://localhost:{port}"
    except requests.exceptions.ConnectionError:
        status = "🔴 OFFLINE"
        url = f"http://localhost:{port}"
    except Exception as e:
        status = f"🔴 ERROR"
        url = f"http://localhost:{port}"

    return {
        'name': name,
        'description': description,
        'port': port,
        'status': status,
        'url': url
    }

def main():
    """Main function"""
    print("=" * 80)
    print("🌐 FREQTRADE DASHBOARDS STATUS CHECK")
    print("=" * 80)
    print(f"⏰ Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Define all dashboards
    dashboards = [
        (8080, "FreqTrade Bot API", "NFI5MOHO_WIP Bot Control"),
        (8503, "System Status Dashboard", "Overall system monitoring"),
        (8504, "NFI5MOHO Strategy Monitor", "Real-time strategy conditions"),
        (8507, "NFI5MOHO Conditions Monitor", "Detailed conditions analysis"),
        (5001, "Enhanced Trading UI", "Advanced trading interface"),
        (8000, "Strategy Dashboard", "Strategy analysis (may have errors)"),
        (8001, "Advanced Trading UI", "Professional trading interface"),
        (8501, "Master Control Dashboard", "Streamlit control panel"),
    ]

    # Check each dashboard
    results = []
    for port, name, description in dashboards:
        result = check_dashboard(port, name, description)
        results.append(result)

    # Display results
    online_count = 0
    print("📊 DASHBOARD STATUS:")
    print("-" * 80)

    for result in results:
        print(f"{result['status']} {result['name']}")
        print(f"   📝 {result['description']}")
        print(f"   🌐 {result['url']}")
        print()

        if "ONLINE" in result['status']:
            online_count += 1

    print("=" * 80)
    print(f"✅ ONLINE: {online_count}/{len(results)} dashboards")
    print("=" * 80)

    # Show working dashboards
    if online_count > 0:
        print("\n🚀 WORKING DASHBOARDS - Click to open:")
        print("-" * 50)

        for result in results:
            if "ONLINE" in result['status']:
                print(f"• {result['name']}: {result['url']}")

        print("\n💡 Copy and paste any URL above into your browser!")

        # Ask if user wants to open all working dashboards
        try:
            choice = input("\n❓ Open all working dashboards in browser? (y/n): ").lower()
            if choice in ['y', 'yes', 'ναι', 'ν']:
                print("\n🌐 Opening dashboards in browser...")
                for result in results:
                    if "ONLINE" in result['status']:
                        try:
                            webbrowser.open(result['url'])
                            print(f"   ✅ Opened: {result['name']}")
                        except Exception as e:
                            print(f"   ❌ Failed to open: {result['name']}")
        except KeyboardInterrupt:
            print("\n👋 Cancelled by user")

    else:
        print("\n❌ No dashboards are currently running!")
        print("💡 Start them with:")
        print("   python3 start_nfi5moho_dashboard.py")

if __name__ == "__main__":
    main()