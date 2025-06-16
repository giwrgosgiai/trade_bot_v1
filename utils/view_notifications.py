#!/usr/bin/env python3
"""
Προβολή Ειδοποιήσεων Οργάνωσης
Εμφανίζει τις ειδοποιήσεις του αυτόματου οργανωτή
"""

import json
import os
from pathlib import Path
from datetime import datetime
import argparse

def load_notifications():
    """Φόρτωση ειδοποιήσεων από JSON file"""
    notifications_file = Path.home() / 'logs' / 'organization_notifications.json'

    if not notifications_file.exists():
        return []

    try:
        with open(notifications_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Σφάλμα φόρτωσης notifications: {e}")
        return []

def format_timestamp(timestamp_str):
    """Μορφοποίηση timestamp"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y %H:%M:%S')
    except:
        return timestamp_str

def show_notifications(count=10, filter_type=None):
    """Εμφάνιση ειδοποιήσεων"""
    notifications = load_notifications()

    if not notifications:
        print("📭 Δεν υπάρχουν ειδοποιήσεις")
        return

    # Φιλτράρισμα αν χρειάζεται
    if filter_type:
        notifications = [n for n in notifications if filter_type.lower() in n.get('filename', '').lower()]

    # Τελευταίες ειδοποιήσεις
    recent_notifications = notifications[-count:] if count else notifications
    recent_notifications.reverse()  # Νεότερες πρώτα

    print(f"📬 Τελευταίες {len(recent_notifications)} Ειδοποιήσεις:")
    print("=" * 60)

    for i, notification in enumerate(recent_notifications, 1):
        timestamp = format_timestamp(notification.get('timestamp', ''))
        filename = notification.get('filename', 'N/A')
        final_path = notification.get('final_path', 'N/A')
        description = notification.get('description', 'N/A')

        print(f"{i:2d}. 📁 {filename}")
        print(f"    ⏰ {timestamp}")
        print(f"    📂 {final_path}")
        print(f"    📝 {description}")
        print()

def show_stats():
    """Εμφάνιση στατιστικών"""
    notifications = load_notifications()

    if not notifications:
        print("📊 Δεν υπάρχουν στατιστικά")
        return

    # Στατιστικά ανά φάκελο
    folder_stats = {}
    for notification in notifications:
        final_path = notification.get('final_path', '')
        if '/' in final_path:
            folder = final_path.split('/')[-2]  # Παίρνουμε το όνομα του φακέλου
            folder_stats[folder] = folder_stats.get(folder, 0) + 1

    print("📊 Στατιστικά Οργάνωσης:")
    print("=" * 30)
    print(f"📈 Συνολικές οργανώσεις: {len(notifications)}")
    print()
    print("📁 Ανά φάκελο:")
    for folder, count in sorted(folder_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {folder}/: {count} αρχεία")

    # Τελευταία δραστηριότητα
    if notifications:
        last_notification = notifications[-1]
        last_time = format_timestamp(last_notification.get('timestamp', ''))
        print(f"\n⏰ Τελευταία οργάνωση: {last_time}")

def clear_notifications():
    """Καθαρισμός ειδοποιήσεων"""
    notifications_file = Path.home() / 'logs' / 'organization_notifications.json'

    if notifications_file.exists():
        try:
            with open(notifications_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
            print("🧹 Ειδοποιήσεις καθαρίστηκαν")
        except Exception as e:
            print(f"❌ Σφάλμα καθαρισμού: {e}")
    else:
        print("📭 Δεν υπάρχουν ειδοποιήσεις για καθαρισμό")

def main():
    """Κύρια συνάρτηση"""
    parser = argparse.ArgumentParser(description='Προβολή ειδοποιήσεων οργάνωσης αρχείων')
    parser.add_argument('-n', '--count', type=int, default=10, help='Αριθμός ειδοποιήσεων (default: 10)')
    parser.add_argument('-f', '--filter', type=str, help='Φιλτράρισμα ανά όνομα αρχείου')
    parser.add_argument('-s', '--stats', action='store_true', help='Εμφάνιση στατιστικών')
    parser.add_argument('-c', '--clear', action='store_true', help='Καθαρισμός ειδοποιήσεων')
    parser.add_argument('-a', '--all', action='store_true', help='Εμφάνιση όλων των ειδοποιήσεων')

    args = parser.parse_args()

    if args.clear:
        clear_notifications()
    elif args.stats:
        show_stats()
    else:
        count = None if args.all else args.count
        show_notifications(count=count, filter_type=args.filter)

if __name__ == "__main__":
    main()