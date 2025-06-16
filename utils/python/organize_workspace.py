#!/usr/bin/env python3
"""
Workspace Organization Script
Οργανώνει τα αρχεία του workspace σε λογικές κατηγορίες
"""

import os
import shutil
from pathlib import Path
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkspaceOrganizer:
    """Οργανωτής workspace"""

    def __init__(self, workspace_path="."):
        self.workspace_path = Path(workspace_path)
        self.organization_plan = {
            "scripts": {
                "description": "Shell scripts και εκτελέσιμα αρχεία",
                "patterns": ["*.sh"],
                "folder": "scripts"
            },
            "python_apps": {
                "description": "Python εφαρμογές και modules",
                "patterns": ["*_app.py", "*_dashboard.py", "*_monitor.py", "*_bot.py"],
                "folder": "apps"
            },
            "configs": {
                "description": "Configuration αρχεία",
                "patterns": ["*.json", "*.yml", "*.yaml", "*.service"],
                "folder": "configs",
                "exclude": ["package*.json", "requirements*.txt"]
            },
            "documentation": {
                "description": "Documentation και README αρχεία",
                "patterns": ["*.md", "*.txt"],
                "folder": "docs",
                "exclude": ["requirements*.txt", "*_pid.txt", "*marker*.txt", "*offset*.txt"]
            },
            "databases": {
                "description": "Database αρχεία",
                "patterns": ["*.db", "*.sqlite", "*.sqlite3"],
                "folder": "data"
            },
            "logs": {
                "description": "Log αρχεία",
                "patterns": ["*.log"],
                "folder": "logs"
            },
            "python_utils": {
                "description": "Python utility scripts",
                "patterns": ["*_utils.py", "*_helper.py", "*_connector.py", "*_formatter.py"],
                "folder": "utils"
            }
        }

    def analyze_current_structure(self):
        """Αναλύει την τρέχουσα δομή του workspace"""
        analysis = {
            "total_files": 0,
            "file_types": {},
            "large_files": [],
            "organization_suggestions": []
        }

        for file_path in self.workspace_path.rglob("*"):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                analysis["total_files"] += 1

                # Ανάλυση τύπων αρχείων
                suffix = file_path.suffix.lower()
                if suffix not in analysis["file_types"]:
                    analysis["file_types"][suffix] = 0
                analysis["file_types"][suffix] += 1

                # Μεγάλα αρχεία (>10MB)
                try:
                    size = file_path.stat().st_size
                    if size > 10 * 1024 * 1024:  # 10MB
                        analysis["large_files"].append({
                            "path": str(file_path),
                            "size_mb": round(size / (1024 * 1024), 2)
                        })
                except:
                    pass

        return analysis

    def _should_ignore_file(self, file_path):
        """Ελέγχει αν ένα αρχείο πρέπει να αγνοηθεί"""
        ignore_patterns = [
            ".git/", "__pycache__/", ".cache/", "node_modules/",
            "myenv/", ".venv/", "venv/", ".cursor-server/",
            "temp_files/", "logs_archive/", "cache_files/", "backups_archive/"
        ]

        path_str = str(file_path)
        return any(pattern in path_str for pattern in ignore_patterns)

    def suggest_organization(self):
        """Προτείνει οργάνωση αρχείων"""
        suggestions = {}

        for file_path in self.workspace_path.rglob("*"):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                # Έλεγξε αν το αρχείο ταιριάζει σε κάποια κατηγορία
                for category, config in self.organization_plan.items():
                    if self._matches_category(file_path, config):
                        if category not in suggestions:
                            suggestions[category] = []
                        suggestions[category].append(str(file_path))
                        break

        return suggestions

    def _matches_category(self, file_path, config):
        """Ελέγχει αν ένα αρχείο ταιριάζει σε μια κατηγορία"""
        # Έλεγξε patterns
        for pattern in config["patterns"]:
            if file_path.match(pattern):
                # Έλεγξε exclusions
                if "exclude" in config:
                    for exclude_pattern in config["exclude"]:
                        if file_path.match(exclude_pattern):
                            return False
                return True
        return False

    def create_organization_folders(self):
        """Δημιουργεί φακέλους οργάνωσης"""
        created_folders = []

        for category, config in self.organization_plan.items():
            folder_path = self.workspace_path / config["folder"]
            if not folder_path.exists():
                folder_path.mkdir(exist_ok=True)
                created_folders.append(str(folder_path))
                logger.info(f"📁 Δημιουργήθηκε φάκελος: {config['folder']}")

        return created_folders

    def organize_files(self, suggestions, dry_run=True):
        """Οργανώνει τα αρχεία βάσει των προτάσεων"""
        actions = []

        if not dry_run:
            self.create_organization_folders()

        for category, files in suggestions.items():
            config = self.organization_plan[category]
            target_folder = config["folder"]

            logger.info(f"📦 Κατηγορία: {category} ({len(files)} αρχεία)")

            for file_path_str in files:
                file_path = Path(file_path_str)

                if not file_path.exists():
                    continue

                # Υπολόγισε τον προορισμό
                target_path = self.workspace_path / target_folder / file_path.name

                # Αν υπάρχει ήδη, πρόσθεσε timestamp
                if target_path.exists():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    stem = target_path.stem
                    suffix = target_path.suffix
                    target_path = target_path.parent / f"{stem}_{timestamp}{suffix}"

                action = {
                    "category": category,
                    "source": str(file_path),
                    "destination": str(target_path),
                    "action": "move" if not dry_run else "would_move"
                }

                if not dry_run:
                    try:
                        shutil.move(str(file_path), str(target_path))
                        logger.info(f"✅ Μετακινήθηκε: {file_path.name} -> {target_folder}/")
                    except Exception as e:
                        logger.error(f"❌ Σφάλμα μετακίνησης {file_path}: {e}")
                        action["error"] = str(e)
                else:
                    logger.info(f"📋 Θα μετακινηθεί: {file_path.name} -> {target_folder}/")

                actions.append(action)

        return actions

    def generate_report(self, analysis, suggestions, actions):
        """Δημιουργεί αναφορά οργάνωσης"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "suggestions": suggestions,
            "actions": actions,
            "summary": {
                "total_files_analyzed": analysis["total_files"],
                "categories_found": len(suggestions),
                "files_to_organize": sum(len(files) for files in suggestions.values()),
                "actions_taken": len(actions)
            }
        }

        return report

    def print_analysis(self, analysis):
        """Εκτυπώνει την ανάλυση"""
        print("\n📊 ΑΝΑΛΥΣΗ WORKSPACE")
        print("=" * 50)
        print(f"📄 Συνολικά αρχεία: {analysis['total_files']}")

        print(f"\n📁 Τύποι αρχείων:")
        for file_type, count in sorted(analysis["file_types"].items(), key=lambda x: x[1], reverse=True):
            if file_type:
                print(f"  {file_type}: {count}")
            else:
                print(f"  (χωρίς επέκταση): {count}")

        if analysis["large_files"]:
            print(f"\n📦 Μεγάλα αρχεία (>10MB):")
            for large_file in analysis["large_files"][:5]:  # Πρώτα 5
                print(f"  {large_file['path']}: {large_file['size_mb']}MB")

    def print_suggestions(self, suggestions):
        """Εκτυπώνει τις προτάσεις οργάνωσης"""
        print(f"\n📋 ΠΡΟΤΑΣΕΙΣ ΟΡΓΑΝΩΣΗΣ")
        print("=" * 50)

        for category, files in suggestions.items():
            config = self.organization_plan[category]
            print(f"\n📁 {config['folder']}/ ({len(files)} αρχεία)")
            print(f"   {config['description']}")

            # Εμφάνιση μερικών παραδειγμάτων
            for file_path in files[:3]:
                file_name = Path(file_path).name
                print(f"   - {file_name}")

            if len(files) > 3:
                print(f"   ... και {len(files) - 3} ακόμα")

def main():
    """Κύρια συνάρτηση"""
    print("🗂️ Workspace Organizer")
    print("=" * 50)

    organizer = WorkspaceOrganizer()

    # Ανάλυση τρέχουσας δομής
    print("\n🔍 Ανάλυση workspace...")
    analysis = organizer.analyze_current_structure()
    organizer.print_analysis(analysis)

    # Προτάσεις οργάνωσης
    print("\n📋 Δημιουργία προτάσεων...")
    suggestions = organizer.suggest_organization()
    organizer.print_suggestions(suggestions)

    # Ερώτηση για εκτέλεση
    if suggestions:
        response = input("\n❓ Θέλετε να προχωρήσετε με την οργάνωση; (y/N): ")

        if response.lower() in ['y', 'yes', 'ναι', 'ν']:
            print("\n🚀 Οργάνωση αρχείων...")
            actions = organizer.organize_files(suggestions, dry_run=False)

            # Δημιουργία αναφοράς
            report = organizer.generate_report(analysis, suggestions, actions)

            report_file = "organization_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            print(f"\n✅ Οργάνωση ολοκληρώθηκε!")
            print(f"📄 Αναφορά αποθηκεύτηκε: {report_file}")
            print(f"📦 Οργανώθηκαν {len(actions)} αρχεία")
        else:
            print("\n❌ Οργάνωση ακυρώθηκε")
    else:
        print("\n✅ Δεν βρέθηκαν αρχεία για οργάνωση")

if __name__ == "__main__":
    main()