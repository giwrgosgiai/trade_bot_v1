#!/usr/bin/env python3
"""
File Usage Checker
Ελέγχει ποια αρχεία δεν χρησιμοποιούνται από άλλα scripts
"""

import os
import re
from pathlib import Path
import json
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileUsageChecker:
    """Ελεγκτής χρήσης αρχείων"""

    def __init__(self, workspace_path="."):
        self.workspace_path = Path(workspace_path)
        self.file_references = defaultdict(set)
        self.python_files = []
        self.shell_files = []
        self.config_files = []

    def scan_files(self):
        """Σαρώνει όλα τα αρχεία στο workspace"""
        logger.info("🔍 Σάρωση αρχείων...")

        # Python files
        self.python_files = list(self.workspace_path.rglob("*.py"))
        logger.info(f"📄 Βρέθηκαν {len(self.python_files)} Python αρχεία")

        # Shell scripts
        self.shell_files = list(self.workspace_path.rglob("*.sh"))
        logger.info(f"📜 Βρέθηκαν {len(self.shell_files)} Shell scripts")

        # Config files
        self.config_files = list(self.workspace_path.rglob("*.json"))
        self.config_files.extend(list(self.workspace_path.rglob("*.yml")))
        self.config_files.extend(list(self.workspace_path.rglob("*.yaml")))
        logger.info(f"⚙️ Βρέθηκαν {len(self.config_files)} Config αρχεία")

    def find_file_references(self):
        """Βρίσκει αναφορές σε αρχεία"""
        logger.info("🔗 Αναζήτηση αναφορών...")

        all_files = self.python_files + self.shell_files + self.config_files

        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Βρες αναφορές σε άλλα αρχεία
                self._find_references_in_content(content, file_path)

            except Exception as e:
                logger.warning(f"⚠️ Δεν μπόρεσα να διαβάσω {file_path}: {e}")

    def _find_references_in_content(self, content, source_file):
        """Βρίσκει αναφορές σε αρχεία μέσα στο περιεχόμενο"""

        # Python imports
        import_patterns = [
            r'from\s+(\w+)\s+import',
            r'import\s+(\w+)',
            r'importlib\.import_module\(["\']([^"\']+)["\']',
        ]

        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Βρες αν υπάρχει αντίστοιχο .py αρχείο
                py_file = self.workspace_path / f"{match}.py"
                if py_file.exists():
                    self.file_references[str(py_file)].add(str(source_file))

        # File paths σε strings
        file_patterns = [
            r'["\']([^"\']*\.py)["\']',
            r'["\']([^"\']*\.sh)["\']',
            r'["\']([^"\']*\.json)["\']',
            r'["\']([^"\']*\.log)["\']',
            r'["\']([^"\']*\.db)["\']',
            r'["\']([^"\']*\.sqlite)["\']',
        ]

        for pattern in file_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Έλεγξε αν το αρχείο υπάρχει
                referenced_file = self.workspace_path / match
                if referenced_file.exists():
                    self.file_references[str(referenced_file)].add(str(source_file))

                # Έλεγξε και σχετικές διαδρομές
                for py_file in self.python_files:
                    if py_file.name == match or str(py_file).endswith(match):
                        self.file_references[str(py_file)].add(str(source_file))

    def find_unused_files(self):
        """Βρίσκει αχρησιμοποίητα αρχεία"""
        logger.info("🔍 Αναζήτηση αχρησιμοποίητων αρχείων...")

        unused_files = {
            "python": [],
            "shell": [],
            "config": [],
            "other": []
        }

        # Έλεγξε Python αρχεία
        for py_file in self.python_files:
            if str(py_file) not in self.file_references:
                # Εξαίρεση για main scripts και __init__.py
                if (py_file.name != "__init__.py" and
                    "if __name__ == '__main__'" not in open(py_file, 'r', encoding='utf-8', errors='ignore').read()):
                    unused_files["python"].append(str(py_file))

        # Έλεγξε Shell scripts
        for sh_file in self.shell_files:
            if str(sh_file) not in self.file_references:
                unused_files["shell"].append(str(sh_file))

        # Έλεγξε Config αρχεία
        for config_file in self.config_files:
            if str(config_file) not in self.file_references:
                unused_files["config"].append(str(config_file))

        return unused_files

    def find_potentially_safe_to_organize(self):
        """Βρίσκει αρχεία που είναι ασφαλή για οργάνωση"""
        safe_to_organize = []

        # Backup αρχεία
        for backup_file in self.workspace_path.rglob("*backup*"):
            if backup_file.is_file():
                safe_to_organize.append(str(backup_file))

        # Αρχεία με timestamps
        timestamp_patterns = [
            r'.*_\d{8}_\d{6}.*',  # YYYYMMDD_HHMMSS
            r'.*_\d{8}.*',        # YYYYMMDD
            r'.*20250614.*',      # Specific date
        ]

        for pattern in timestamp_patterns:
            for file_path in self.workspace_path.rglob("*"):
                if file_path.is_file() and re.match(pattern, file_path.name):
                    safe_to_organize.append(str(file_path))

        return list(set(safe_to_organize))  # Remove duplicates

    def generate_usage_report(self):
        """Δημιουργεί αναφορά χρήσης αρχείων"""
        unused_files = self.find_unused_files()
        safe_to_organize = self.find_potentially_safe_to_organize()

        report = {
            "timestamp": str(Path().cwd()),
            "statistics": {
                "total_python_files": len(self.python_files),
                "total_shell_files": len(self.shell_files),
                "total_config_files": len(self.config_files),
                "unused_python": len(unused_files["python"]),
                "unused_shell": len(unused_files["shell"]),
                "unused_config": len(unused_files["config"]),
                "safe_to_organize": len(safe_to_organize)
            },
            "unused_files": unused_files,
            "safe_to_organize": safe_to_organize,
            "file_references": dict(self.file_references)
        }

        return report

    def print_report(self, report):
        """Εκτυπώνει την αναφορά"""
        print("\n📊 ΑΝΑΦΟΡΑ ΧΡΗΣΗΣ ΑΡΧΕΙΩΝ")
        print("=" * 50)

        stats = report["statistics"]
        print(f"📄 Συνολικά Python αρχεία: {stats['total_python_files']}")
        print(f"📜 Συνολικά Shell scripts: {stats['total_shell_files']}")
        print(f"⚙️ Συνολικά Config αρχεία: {stats['total_config_files']}")

        print(f"\n🔍 ΑΧΡΗΣΙΜΟΠΟΙΗΤΑ ΑΡΧΕΙΑ:")
        print(f"  Python: {stats['unused_python']}")
        print(f"  Shell: {stats['unused_shell']}")
        print(f"  Config: {stats['unused_config']}")

        print(f"\n📦 Ασφαλή για οργάνωση: {stats['safe_to_organize']}")

        # Εμφάνιση λεπτομερειών
        if report["unused_files"]["python"]:
            print(f"\n🐍 Αχρησιμοποίητα Python αρχεία:")
            for file_path in report["unused_files"]["python"][:10]:  # Πρώτα 10
                print(f"  - {file_path}")
            if len(report["unused_files"]["python"]) > 10:
                print(f"  ... και {len(report['unused_files']['python']) - 10} ακόμα")

        if report["safe_to_organize"]:
            print(f"\n📦 Ασφαλή για οργάνωση:")
            for file_path in report["safe_to_organize"][:10]:  # Πρώτα 10
                print(f"  - {file_path}")
            if len(report["safe_to_organize"]) > 10:
                print(f"  ... και {len(report['safe_to_organize']) - 10} ακόμα")

def main():
    """Κύρια συνάρτηση"""
    print("🔍 File Usage Checker")
    print("=" * 50)

    checker = FileUsageChecker()

    # Σάρωση αρχείων
    checker.scan_files()

    # Αναζήτηση αναφορών
    checker.find_file_references()

    # Δημιουργία αναφοράς
    report = checker.generate_usage_report()

    # Εκτύπωση αναφοράς
    checker.print_report(report)

    # Αποθήκευση αναφοράς
    report_file = "file_usage_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Αναφορά αποθηκεύτηκε: {report_file}")

if __name__ == "__main__":
    main()