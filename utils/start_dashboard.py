#!/usr/bin/env python3
"""
Startup script για το Freqtrade Strategy Dashboard
"""

import os
import sys
import subprocess
import webbrowser
from time import sleep

def check_dependencies():
    """Ελέγχει αν είναι εγκατεστημένες οι απαραίτητες βιβλιοθήκες."""
    required_packages = ['fastapi', 'uvicorn', 'jinja2']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Λείπουν οι εξής βιβλιοθήκες: {', '.join(missing_packages)}")
        print(f"Εγκαταστήστε τες με: pip install {' '.join(missing_packages)}")
        return False

    return True

def start_dashboard():
    """Εκκινεί το dashboard."""
    if not check_dependencies():
        return

    print("🚀 Εκκίνηση του Freqtrade Strategy Dashboard...")
    print("📍 URL: http://localhost:8000")
    print("⏹️  Για τερματισμό πατήστε Ctrl+C")
    print("-" * 50)

    # Άνοιγμα του browser αυτόματα μετά από 2 δευτερόλεπτα
    try:
        import threading
        def open_browser():
            sleep(2)
            webbrowser.open('http://localhost:8000')

        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
    except Exception:
        pass

    # Εκκίνηση του server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "strategy_dashboard:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Το dashboard τερματίστηκε.")
    except Exception as e:
        print(f"❌ Σφάλμα κατά την εκκίνηση: {e}")

if __name__ == "__main__":
    start_dashboard()