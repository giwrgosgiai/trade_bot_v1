#!/usr/bin/env python3
"""
Script για διόρθωση paths μετά την οργάνωση του project
"""

import os
import re
from pathlib import Path

def fix_paths_in_file(file_path, replacements):
    """Διορθώνει paths σε ένα αρχείο"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        for old_path, new_path in replacements.items():
            content = content.replace(old_path, new_path)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Διορθώθηκε: {file_path}")
            return True

        return False
    except Exception as e:
        print(f"❌ Σφάλμα στο {file_path}: {e}")
        return False

def main():
    """Κύρια συνάρτηση"""
    print("🔧 Διόρθωση paths μετά την οργάνωση...")

    # Paths που χρειάζονται διόρθωση
    path_replacements = {
        # Για scripts που τρέχουν από scripts/
        "'logs/": "'../data/logs/",
        '"logs/': '"../data/logs/',
        "'configs/": "'../configs/",
        '"configs/': '"../configs/',
        "'data/": "'../data/",
        '"data/': '"../data/',
        "'apps/": "'../apps/",
        '"apps/': '"../apps/',

        # Για apps που τρέχουν από apps/
        "'logs/": "'../../data/logs/",
        '"logs/': '"../../data/logs/',
        "'configs/": "'../../configs/",
        '"configs/': '"../../configs/',
        "'data/": "'../../data/",
        '"data/': '"../../data/',
    }

    # Αρχεία που χρειάζονται διόρθωση
    files_to_fix = []

    # Scripts
    scripts_dir = Path("../scripts")
    if scripts_dir.exists():
        for file_path in scripts_dir.glob("*.py"):
            files_to_fix.append(file_path)
        for file_path in scripts_dir.glob("*.sh"):
            files_to_fix.append(file_path)

    # Apps
    apps_dir = Path("../apps")
    if apps_dir.exists():
        for file_path in apps_dir.rglob("*.py"):
            files_to_fix.append(file_path)
        for file_path in apps_dir.rglob("*.sh"):
            files_to_fix.append(file_path)

    # Utils
    utils_dir = Path("../utils")
    if utils_dir.exists():
        for file_path in utils_dir.rglob("*.py"):
            files_to_fix.append(file_path)

    fixed_count = 0

    for file_path in files_to_fix:
        if fix_paths_in_file(file_path, path_replacements):
            fixed_count += 1

    print(f"\n✅ Διορθώθηκαν {fixed_count} αρχεία από {len(files_to_fix)} συνολικά")
    print("🎉 Η οργάνωση ολοκληρώθηκε!")

if __name__ == "__main__":
    main()