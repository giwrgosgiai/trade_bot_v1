#!/usr/bin/env python3
"""
🚀 Master Script Launcher
Εύκολη πρόσβαση σε όλα τα οργανωμένα scripts
Γιώργος Γιαϊλόγλου - FreqTrade Project
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

class MasterLauncher:
    def __init__(self):
        self.base_path = Path("scripts")
        self.scripts_map = self.build_scripts_map()

    def build_scripts_map(self) -> Dict[str, Dict[str, List[str]]]:
        """Χτίζει χάρτη όλων των διαθέσιμων scripts"""
        scripts_map = {}

        for category_dir in self.base_path.iterdir():
            if category_dir.is_dir() and category_dir.name != "__pycache__":
                category = category_dir.name
                scripts_map[category] = {
                    "python": [],
                    "shell": []
                }

                for script_file in category_dir.iterdir():
                    if script_file.is_file() and script_file.name != "README.md":
                        if script_file.suffix == ".py":
                            scripts_map[category]["python"].append(script_file.name)
                        elif script_file.suffix == ".sh":
                            scripts_map[category]["shell"].append(script_file.name)

        return scripts_map

    def display_menu(self):
        """Εμφανίζει το κύριο μενού"""
        print("🚀 MASTER SCRIPT LAUNCHER")
        print("=" * 50)
        print("Επιλέξτε κατηγορία:")
        print()

        categories = {
            "1": ("core", "🔧 Core - Βασικά FreqTrade scripts"),
            "2": ("monitoring", "📊 Monitoring - Παρακολούθηση και έλεγχος"),
            "3": ("telegram", "📱 Telegram - Notifications και alerts"),
            "4": ("management", "⚙️  Management - Διαχείριση bots"),
            "5": ("optimization", "📈 Optimization - Βελτιστοποίηση και backtesting"),
            "6": ("utilities", "🛠️  Utilities - Βοηθητικά scripts"),
            "7": ("security", "🔒 Security - Ασφάλεια"),
            "8": ("network", "🌐 Network - Δικτυακές λειτουργίες"),
            "9": ("", "📋 Εμφάνιση όλων των scripts"),
            "0": ("", "❌ Έξοδος")
        }

        for key, (category, description) in categories.items():
            print(f"{key}. {description}")

        print()
        return input("Επιλογή: ").strip()

    def display_category_scripts(self, category: str):
        """Εμφανίζει τα scripts μιας κατηγορίας"""
        if category not in self.scripts_map:
            print(f"❌ Κατηγορία '{category}' δεν βρέθηκε!")
            return

        print(f"\n📁 {category.upper()} SCRIPTS")
        print("=" * 40)

        all_scripts = []

        # Python scripts
        if self.scripts_map[category]["python"]:
            print("🐍 Python Scripts:")
            for i, script in enumerate(self.scripts_map[category]["python"], 1):
                print(f"  {len(all_scripts) + i}. {script}")
                all_scripts.append((script, "python"))

        # Shell scripts
        if self.scripts_map[category]["shell"]:
            print("🐚 Shell Scripts:")
            start_num = len(all_scripts) + 1
            for i, script in enumerate(self.scripts_map[category]["shell"], start_num):
                print(f"  {i}. {script}")
                all_scripts.append((script, "shell"))

        if not all_scripts:
            print("❌ Δεν βρέθηκαν scripts σε αυτή την κατηγορία")
            return

        print(f"\n0. ← Επιστροφή στο κύριο μενού")
        print()

        choice = input("Επιλέξτε script για εκτέλεση: ").strip()

        if choice == "0":
            return

        try:
            script_index = int(choice) - 1
            if 0 <= script_index < len(all_scripts):
                script_name, script_type = all_scripts[script_index]
                self.execute_script(category, script_name, script_type)
            else:
                print("❌ Μη έγκυρη επιλογή!")
        except ValueError:
            print("❌ Παρακαλώ εισάγετε έναν αριθμό!")

    def display_all_scripts(self):
        """Εμφανίζει όλα τα διαθέσιμα scripts"""
        print("\n📋 ΟΛΟΙ ΟΙ ΔΙΑΘΕΣΙΜΟΙ SCRIPTS")
        print("=" * 50)

        for category, scripts in self.scripts_map.items():
            if scripts["python"] or scripts["shell"]:
                print(f"\n📁 {category.upper()}:")

                for script in scripts["python"]:
                    print(f"  🐍 {script}")

                for script in scripts["shell"]:
                    print(f"  🐚 {script}")

        input("\nΠατήστε Enter για επιστροφή...")

    def execute_script(self, category: str, script_name: str, script_type: str):
        """Εκτελεί ένα script"""
        script_path = self.base_path / category / script_name

        if not script_path.exists():
            print(f"❌ Το script {script_path} δεν βρέθηκε!")
            return

        print(f"\n🚀 Εκτέλεση: {script_name}")
        print("=" * 40)

        # Επιβεβαίωση εκτέλεσης
        confirm = input(f"Θέλετε να εκτελέσετε το {script_name}? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes', 'ναι', 'ν']:
            print("❌ Ακύρωση εκτέλεσης")
            return

        try:
            if script_type == "python":
                # Εκτέλεση Python script
                subprocess.run([sys.executable, str(script_path)], check=True)
            elif script_type == "shell":
                # Εκτέλεση Shell script
                subprocess.run(["bash", str(script_path)], check=True)

            print(f"\n✅ Το {script_name} ολοκληρώθηκε επιτυχώς!")

        except subprocess.CalledProcessError as e:
            print(f"❌ Σφάλμα κατά την εκτέλεση: {e}")
        except KeyboardInterrupt:
            print(f"\n⚠️  Διακοπή εκτέλεσης από τον χρήστη")
        except Exception as e:
            print(f"❌ Απροσδόκητο σφάλμα: {e}")

        input("\nΠατήστε Enter για συνέχεια...")

    def run(self):
        """Κύρια λειτουργία του launcher"""
        while True:
            try:
                choice = self.display_menu()

                if choice == "0":
                    print("👋 Αντίο!")
                    break
                elif choice == "1":
                    self.display_category_scripts("core")
                elif choice == "2":
                    self.display_category_scripts("monitoring")
                elif choice == "3":
                    self.display_category_scripts("telegram")
                elif choice == "4":
                    self.display_category_scripts("management")
                elif choice == "5":
                    self.display_category_scripts("optimization")
                elif choice == "6":
                    self.display_category_scripts("utilities")
                elif choice == "7":
                    self.display_category_scripts("security")
                elif choice == "8":
                    self.display_category_scripts("network")
                elif choice == "9":
                    self.display_all_scripts()
                else:
                    print("❌ Μη έγκυρη επιλογή! Παρακαλώ επιλέξτε 0-9.")

                print()  # Κενή γραμμή για καλύτερη εμφάνιση

            except KeyboardInterrupt:
                print("\n\n👋 Αντίο!")
                break
            except Exception as e:
                print(f"❌ Σφάλμα: {e}")
                input("Πατήστε Enter για συνέχεια...")

def main():
    """Main function"""
    launcher = MasterLauncher()
    launcher.run()

if __name__ == "__main__":
    main()