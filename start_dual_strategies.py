#!/usr/bin/env python3
"""
Dual Strategy Launcher for trade_bot_v1
Εκκίνηση NFI5MOHO και NeverMissATrend παράλληλα
"""

import subprocess
import time
import sys
import os
from datetime import datetime

def print_banner():
    """Εκτύπωση banner"""
    print("=" * 60)
    print("🤖 DUAL STRATEGY LAUNCHER - trade_bot_v1")
    print("=" * 60)
    print("📈 NFI5MOHO (15m) + NeverMissATrend (1d)")
    print("🚀 Παράλληλη εκτέλεση στρατηγικών")
    print("=" * 60)

def check_dependencies():
    """Έλεγχος dependencies"""
    print("🔍 Έλεγχος dependencies...")

    # Έλεγχος αν υπάρχει το freqtrade
    if not os.path.exists("freqtrade"):
        print("❌ Δεν βρέθηκε ο φάκελος freqtrade!")
        return False

    # Έλεγχος στρατηγικών
    if not os.path.exists("user_data/strategies/NFI5MOHO_WIP.py"):
        print("❌ Δεν βρέθηκε η στρατηγική NFI5MOHO_WIP.py!")
        return False

    if not os.path.exists("user_data/strategies/NeverMissATrend.py"):
        print("❌ Δεν βρέθηκε η στρατηγική NeverMissATrend.py!")
        return False

    # Έλεγχος config αρχείων
    if not os.path.exists("user_data/config.json"):
        print("❌ Δεν βρέθηκε το config.json!")
        return False

    if not os.path.exists("user_data/nevermissatrend_config.json"):
        print("❌ Δεν βρέθηκε το nevermissatrend_config.json!")
        return False

    print("✅ Όλες οι dependencies βρέθηκαν!")
    return True

def start_strategy(strategy_name, config_file, port):
    """Εκκίνηση μιας στρατηγικής"""
    print(f"🚀 Εκκίνηση {strategy_name}...")

    cmd = [
        "python3", "-m", "freqtrade", "trade",
        "-c", config_file,
        "--logfile", f"logs/{strategy_name.lower()}.log"
    ]

    try:
        # Αλλαγή στον φάκελο freqtrade
        os.chdir("freqtrade")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Επιστροφή στον αρχικό φάκελο
        os.chdir("..")

        print(f"✅ {strategy_name} εκκινήθηκε με PID: {process.pid}")
        print(f"📊 API Port: {port}")
        return process

    except Exception as e:
        print(f"❌ Σφάλμα εκκίνησης {strategy_name}: {e}")
        return None

def main():
    """Κύρια συνάρτηση"""
    print_banner()

    if not check_dependencies():
        print("❌ Αποτυχία έλεγχου dependencies!")
        sys.exit(1)

    print("\n🎯 Εκκίνηση στρατηγικών...")

    # Δημιουργία φακέλου logs αν δεν υπάρχει
    os.makedirs("logs", exist_ok=True)

    processes = []

    # Εκκίνηση NFI5MOHO
    nfi5_process = start_strategy("NFI5MOHO", "../user_data/config.json", 8080)
    if nfi5_process:
        processes.append(("NFI5MOHO", nfi5_process))

    time.sleep(5)  # Αναμονή 5 δευτερολέπτων

    # Εκκίνηση NeverMissATrend
    nevermiss_process = start_strategy("NeverMissATrend", "../user_data/nevermissatrend_config.json", 8081)
    if nevermiss_process:
        processes.append(("NeverMissATrend", nevermiss_process))

    if not processes:
        print("❌ Δεν εκκινήθηκε καμία στρατηγική!")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("🎉 ΕΠΙΤΥΧΗΣ ΕΚΚΙΝΗΣΗ!")
    print("=" * 60)
    print("📊 Ενεργές στρατηγικές:")
    for name, process in processes:
        print(f"   • {name} (PID: {process.pid})")

    print("\n🌐 API Endpoints:")
    print("   • NFI5MOHO: http://localhost:8080")
    print("   • NeverMissATrend: http://localhost:8081")

    print("\n📱 Telegram Bot: Ενεργό")
    print("📈 Dashboard: http://localhost:8500")

    print("\n⏹️  Για τερματισμό: Ctrl+C")
    print("=" * 60)

    try:
        # Αναμονή για Ctrl+C
        while True:
            time.sleep(1)
            # Έλεγχος αν οι διεργασίες τρέχουν ακόμα
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️  Η στρατηγική {name} τερματίστηκε!")

    except KeyboardInterrupt:
        print("\n🛑 Τερματισμός στρατηγικών...")
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=10)
                print(f"✅ {name} τερματίστηκε")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔪 {name} αναγκαστικός τερματισμός")
            except Exception as e:
                print(f"❌ Σφάλμα τερματισμού {name}: {e}")

        print("👋 Αντίο!")

if __name__ == "__main__":
    main()