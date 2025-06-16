#!/usr/bin/env python3
"""
Cleanup Unused Files Script
Εντοπίζει και οργανώνει αχρήστα αρχεία στο trading system workspace
"""

import os
import shutil
import glob
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging

# Ρύθμιση logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup_report.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FileCleanupManager:
    """Διαχειριστής καθαρισμού αρχείων"""

    def __init__(self, workspace_path="."):
        self.workspace_path = Path(workspace_path)
        self.cleanup_report = {
            "timestamp": datetime.now().isoformat(),
            "actions": [],
            "statistics": {}
        }

        # Φάκελοι για οργάνωση
        self.organize_folders = {
            "logs": "logs_archive",
            "backups": "backups_archive",
            "temp": "temp_files",
            "cache": "cache_files",
            "old_configs": "old_configs"
        }

    def create_organization_folders(self):
        """Δημιουργεί φακέλους οργάνωσης"""
        for folder in self.organize_folders.values():
            folder_path = self.workspace_path / folder
            folder_path.mkdir(exist_ok=True)
            logger.info(f"📁 Δημιουργήθηκε φάκελος: {folder}")

    def find_unused_log_files(self):
        """Βρίσκει παλιά log αρχεία"""
        log_files = []
        cutoff_date = datetime.now() - timedelta(days=7)

        # Βρες όλα τα .log αρχεία
        for log_file in self.workspace_path.rglob("*.log"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                log_files.append(log_file)

        return log_files

    def find_pid_files(self):
        """Βρίσκει PID αρχεία"""
        pid_files = []

        # .pid αρχεία
        pid_files.extend(list(self.workspace_path.rglob("*.pid")))

        # *_pid.txt αρχεία
        for txt_file in self.workspace_path.rglob("*_pid.txt"):
            pid_files.append(txt_file)

        return pid_files

    def find_cache_files(self):
        """Βρίσκει cache αρχεία"""
        cache_files = []

        # __pycache__ φάκελοι
        for pycache in self.workspace_path.rglob("__pycache__"):
            cache_files.append(pycache)

        # .pyc αρχεία
        cache_files.extend(list(self.workspace_path.rglob("*.pyc")))

        return cache_files

    def find_temporary_files(self):
        """Βρίσκει προσωρινά αρχεία"""
        temp_files = []

        # Marker αρχεία
        temp_files.extend(list(self.workspace_path.rglob("*marker*.txt")))
        temp_files.extend(list(self.workspace_path.rglob("*offset*.txt")))

        # Backup αρχεία παλιότερα από 30 ημέρες
        cutoff_date = datetime.now() - timedelta(days=30)
        for backup_file in self.workspace_path.rglob("*.tar.gz"):
            if backup_file.stat().st_mtime < cutoff_date.timestamp():
                temp_files.append(backup_file)

        return temp_files

    def find_duplicate_configs(self):
        """Βρίσκει διπλότυπα config αρχεία"""
        config_files = []

        # Βρες config αρχεία με timestamps
        for config_file in self.workspace_path.rglob("*config*.json"):
            if any(date_pattern in config_file.name for date_pattern in ["20250614", "_backup", "_old"]):
                config_files.append(config_file)

        return config_files

    def analyze_file_usage(self):
        """Αναλύει τη χρήση αρχείων"""
        analysis = {
            "unused_logs": self.find_unused_log_files(),
            "pid_files": self.find_pid_files(),
            "cache_files": self.find_cache_files(),
            "temp_files": self.find_temporary_files(),
            "duplicate_configs": self.find_duplicate_configs()
        }

        return analysis

    def safe_move_file(self, source, destination_folder):
        """Μετακινεί αρχείο με ασφάλεια"""
        try:
            dest_path = self.workspace_path / destination_folder
            dest_path.mkdir(exist_ok=True)

            dest_file = dest_path / source.name

            # Αν υπάρχει ήδη, πρόσθεσε timestamp
            if dest_file.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                stem = dest_file.stem
                suffix = dest_file.suffix
                dest_file = dest_path / f"{stem}_{timestamp}{suffix}"

            shutil.move(str(source), str(dest_file))

            action = {
                "action": "moved",
                "source": str(source),
                "destination": str(dest_file),
                "timestamp": datetime.now().isoformat()
            }
            self.cleanup_report["actions"].append(action)

            logger.info(f"✅ Μετακινήθηκε: {source} -> {dest_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Σφάλμα μετακίνησης {source}: {e}")
            return False

    def safe_remove_cache(self, cache_path):
        """Διαγράφει cache με ασφάλεια"""
        try:
            if cache_path.is_dir():
                shutil.rmtree(cache_path)
            else:
                cache_path.unlink()

            action = {
                "action": "removed",
                "path": str(cache_path),
                "type": "cache",
                "timestamp": datetime.now().isoformat()
            }
            self.cleanup_report["actions"].append(action)

            logger.info(f"🗑️ Διαγράφηκε cache: {cache_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Σφάλμα διαγραφής cache {cache_path}: {e}")
            return False

    def organize_files(self, dry_run=True):
        """Οργανώνει τα αρχεία"""
        logger.info("🔍 Ανάλυση αρχείων...")

        analysis = self.analyze_file_usage()

        # Στατιστικά
        stats = {}
        for category, files in analysis.items():
            stats[category] = len(files)

        self.cleanup_report["statistics"] = stats

        logger.info("📊 Στατιστικά αρχείων:")
        for category, count in stats.items():
            logger.info(f"  {category}: {count} αρχεία")

        if dry_run:
            logger.info("🔍 DRY RUN - Δεν θα γίνουν αλλαγές")
            return self.cleanup_report

        # Δημιουργία φακέλων οργάνωσης
        self.create_organization_folders()

        # Μετακίνηση αρχείων
        logger.info("📦 Οργάνωση αρχείων...")

        # Logs
        for log_file in analysis["unused_logs"]:
            self.safe_move_file(log_file, "logs_archive")

        # PID files
        for pid_file in analysis["pid_files"]:
            self.safe_move_file(pid_file, "temp_files")

        # Temp files
        for temp_file in analysis["temp_files"]:
            self.safe_move_file(temp_file, "temp_files")

        # Duplicate configs
        for config_file in analysis["duplicate_configs"]:
            self.safe_move_file(config_file, "old_configs")

        # Cache files (διαγραφή)
        logger.info("🗑️ Καθαρισμός cache...")
        for cache_file in analysis["cache_files"]:
            self.safe_remove_cache(cache_file)

        return self.cleanup_report

    def generate_report(self):
        """Δημιουργεί αναφορά καθαρισμού"""
        report_file = self.workspace_path / "cleanup_report.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.cleanup_report, f, indent=2, ensure_ascii=False)

        logger.info(f"📄 Αναφορά αποθηκεύτηκε: {report_file}")

        # Σύνοψη
        total_actions = len(self.cleanup_report["actions"])
        moved_files = len([a for a in self.cleanup_report["actions"] if a["action"] == "moved"])
        removed_files = len([a for a in self.cleanup_report["actions"] if a["action"] == "removed"])

        logger.info("📋 Σύνοψη καθαρισμού:")
        logger.info(f"  Συνολικές ενέργειες: {total_actions}")
        logger.info(f"  Μετακινημένα αρχεία: {moved_files}")
        logger.info(f"  Διαγραμμένα αρχεία: {removed_files}")

def main():
    """Κύρια συνάρτηση"""
    print("🧹 File Cleanup Manager")
    print("=" * 50)

    cleanup_manager = FileCleanupManager()

    # Πρώτα κάνε dry run
    print("\n🔍 Ανάλυση αρχείων (Dry Run)...")
    report = cleanup_manager.organize_files(dry_run=True)

    # Εμφάνιση στατιστικών
    print("\n📊 Βρέθηκαν:")
    for category, count in report["statistics"].items():
        print(f"  {category}: {count} αρχεία")

    # Ερώτηση για εκτέλεση
    response = input("\n❓ Θέλετε να προχωρήσετε με την οργάνωση; (y/N): ")

    if response.lower() in ['y', 'yes', 'ναι', 'ν']:
        print("\n🚀 Εκτέλεση καθαρισμού...")
        cleanup_manager.organize_files(dry_run=False)
        cleanup_manager.generate_report()
        print("\n✅ Καθαρισμός ολοκληρώθηκε!")
    else:
        print("\n❌ Καθαρισμός ακυρώθηκε")

if __name__ == "__main__":
    main()