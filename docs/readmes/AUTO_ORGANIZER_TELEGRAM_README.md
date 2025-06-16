# Auto Organizer με Telegram Notifications

## Περιγραφή
Ο αυτόματος οργανωτής αρχείων τώρα στέλνει notifications στο Telegram κάθε φορά που οργανώνει ένα αρχείο.

## Χαρακτηριστικά

### 🔧 Τεχνικά Χαρακτηριστικά
- **Telegram Bot Integration**: Χρήση Telegram Bot API
- **Async Notifications**: Αποστολή σε background threads για performance
- **Retry Logic**: 2 προσπάθειες αποστολής με 1 δευτερόλεπτο καθυστέρηση
- **Timeout**: 5 δευτερόλεπτα timeout για κάθε αίτημα
- **Fallback**: Πάντα αποθηκεύει στο JSON file ακόμα και αν το Telegram αποτύχει

### 📱 Telegram Notifications
- **Startup Notification**: Όταν ξεκινάει ο οργανωτής
- **File Organization**: Για κάθε αρχείο που οργανώνεται
- **Shutdown Notification**: Όταν σταματάει ο οργανωτής

### 📋 Μορφή Μηνύματος
```
🎯 ΑΥΤΟΜΑΤΗ ΟΡΓΑΝΩΣΗ

📁 Αρχείο: filename.py
📂 Φάκελος: utils/
📝 Τύπος: Python utility scripts
⏰ Χρόνος: 14/06/2025 18:56:48
📍 Path: /home/giwrgosgiai/utils/filename.py
```

## Ρυθμίσεις

### Telegram Configuration
```python
TELEGRAM_TOKEN = "7295982134:AAF242CTc3vVc9m0qBT3wcF0wljByhlptMQ"
TELEGRAM_CHAT_ID = 930268785
ENABLE_TELEGRAM_NOTIFICATIONS = True
TELEGRAM_TIMEOUT = 5
TELEGRAM_RETRY_ATTEMPTS = 2
```

### Ενεργοποίηση/Απενεργοποίηση
Για να απενεργοποιήσεις τα Telegram notifications:
```python
ENABLE_TELEGRAM_NOTIFICATIONS = False
```

## Εκκίνηση

### Με το startup script:
```bash
./start_auto_organizer.sh
```

### Χειροκίνητα:
```bash
python3 auto_organizer.py
```

## Δοκιμή

### Test Telegram Connection:
```bash
python3 -c "
import requests
response = requests.get('https://api.telegram.org/bot7295982134:AAF242CTc3vVc9m0qBT3wcF0wljByhlptMQ/getMe', timeout=5)
print('✅ Connected!' if response.status_code == 200 else '❌ Failed!')
"
```

### Δημιουργία Test File:
```bash
echo "# Test file" > test_demo.py
# Θα πρέπει να δεις notification στο Telegram και στα logs
```

## Logs

### Auto Organizer Logs:
```bash
tail -f logs/auto_organizer.log
```

### JSON Notifications:
```bash
cat logs/organization_notifications.json | jq '.[].message'
```

## Troubleshooting

### Telegram Notifications δεν λειτουργούν:
1. Έλεγχος internet σύνδεσης
2. Έλεγχος Telegram bot token
3. Έλεγχος chat ID
4. Έλεγχος αν το bot έχει προστεθεί στο chat

### Logs για debugging:
```bash
grep "Telegram" logs/auto_organizer.log
```

## Κατηγορίες Οργάνωσης

| Κατηγορία | Extensions | Patterns | Περιγραφή |
|-----------|------------|----------|-----------|
| scripts | .sh | start_, stop_, setup_, run_, quick_ | Shell scripts και εκτελέσιμα |
| configs | .json, .yaml, .yml, .ini, .conf | config_, _config, settings_ | Configuration files |
| docs | .md, .txt, .rst | README, CHANGELOG, LICENSE, GUIDE | Documentation files |
| monitoring | .py | ai_, monitor, watchdog, tracker | AI monitoring scripts |
| backtest | .py | backtest, bt_, test_strategy | Backtest scripts |
| telegram | .py | telegram, bot_, _bot | Telegram bot files |
| utils | .py, .txt | util, helper, tool, example | Utility scripts και tools |
| logs | .log, .txt | log, output, result | Log files |

## Παραδείγματα Notifications

### Startup:
```
🚀 ΑΥΤΟΜΑΤΟΣ ΟΡΓΑΝΩΤΗΣ ΕΝΕΡΓΟΠΟΙΗΘΗΚΕ

⏰ Χρόνος: 14/06/2025 18:54:31
📁 Παρακολουθώ: /home/giwrgosgiai
🎯 Κατηγορίες: 8
📱 Telegram: Ενεργό

Θα ενημερώνομαι για κάθε αρχείο που οργανώνεται!
```

### Shutdown:
```
🛑 ΑΥΤΟΜΑΤΟΣ ΟΡΓΑΝΩΤΗΣ ΣΤΑΜΑΤΗΣΕ

⏰ Χρόνος: 14/06/2025 18:55:00
📊 Κατάσταση: Απενεργοποιήθηκε
🔄 Επανεκκίνηση: Χειροκίνητα

Ο αυτόματος οργανωτής δεν παρακολουθεί πλέον για νέα αρχεία.
```

## Απαιτήσεις

### Python Modules:
- `requests` - για Telegram API
- `watchdog` - για file monitoring
- `pathlib` - για path operations
- `threading` - για async notifications

### Εγκατάσταση:
```bash
pip3 install requests watchdog
```

## Ασφάλεια

⚠️ **Προσοχή**: Το Telegram token είναι hardcoded στον κώδικα. Για production χρήση, χρησιμοποίησε environment variables:

```python
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', 'default_token')
TELEGRAM_CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID', '0'))
```