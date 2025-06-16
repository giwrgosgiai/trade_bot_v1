# System Dashboard Telegram Bot

## Περιγραφή
Το **System Dashboard Telegram Bot** σας επιτρέπει να ελέγχετε και να διαχειρίζεστε το System Status Dashboard απευθείας από το Telegram.

## Τι μπορείτε να κάνετε:
- 📊 **Έλεγχος κατάστασης** - Δείτε την κατάσταση όλων των συστημάτων
- 🔍 **Εκκίνηση ελέγχου** - Ξεκινήστε έλεγχο όλων των συστημάτων
- 🚀 **Εκκίνηση Dashboard** - Ξεκινήστε το dashboard αν δεν τρέχει
- 🛑 **Τερματισμός Dashboard** - Σταματήστε το dashboard
- 🔄 **Επανεκκίνηση Dashboard** - Κάντε restart το dashboard

## Εγκατάσταση

### 1. Εγκατάσταση Dependencies
```bash
pip install python-telegram-bot
```

### 2. Δημιουργία Telegram Bot
1. Στείλτε μήνυμα στο [@BotFather](https://t.me/BotFather)
2. Πληκτρολογήστε `/newbot`
3. Δώστε όνομα στο bot (π.χ. "My System Dashboard Bot")
4. Δώστε username (π.χ. "my_system_dashboard_bot")
5. Αντιγράψτε το **Bot Token** που θα σας δώσει

### 3. Εύρεση του User ID σας
1. Στείλτε μήνυμα στο [@userinfobot](https://t.me/userinfobot)
2. Στείλτε `/start`
3. Αντιγράψτε το **User ID** που θα σας δώσει

### 4. Ρύθμιση Configuration
Επεξεργαστείτε το αρχείο `configs/telegram/bot_config.py`:

```python
# Bot Token από το @BotFather
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

# Telegram User IDs που επιτρέπεται να χρησιμοποιούν το bot
ALLOWED_USERS = [
    123456789,  # Το δικό σας User ID
    987654321,  # User ID άλλου χρήστη (προαιρετικό)
]
```

### 5. Εκκίνηση Bot
```bash
./start_telegram_bot.sh
```

ή

```bash
python3 apps/telegram/system_dashboard_bot.py
```

## Χρήση

### Εντολές
- `/start` - Εμφάνιση κύριου μενού
- `/status` - Γρήγορος έλεγχος κατάστασης
- `/help` - Εμφάνιση βοήθειας

### Κουμπιά
Το bot χρησιμοποιεί **Inline Keyboards** για εύκολη χρήση:

#### Κύριο Μενού:
- 📊 **Κατάσταση Dashboard** - Δείτε την τρέχουσα κατάσταση
- 🔍 **Έλεγχος Συστημάτων** - Εκκινήστε έλεγχο όλων των συστημάτων
- 🚀 **Εκκίνηση Dashboard** - Ξεκινήστε το dashboard
- 🛑 **Τερματισμός Dashboard** - Σταματήστε το dashboard
- 🔄 **Επανεκκίνηση Dashboard** - Κάντε restart το dashboard

#### Μενού Κατάστασης:
- 🔄 **Ανανέωση** - Ανανεώστε την κατάσταση
- 🔍 **Έλεγχος Συστημάτων** - Εκκινήστε νέο έλεγχο
- 🏠 **Αρχική** - Επιστροφή στο κύριο μενού

## Τι ελέγχει το Dashboard

### 🤖 Trading Bots
- Original Bot (E0V1E) - Port 8081
- Enhanced Bot (E0V1E_Enhanced) - Port 8082

### 💾 Databases
- bot_monitor_status.json
- simple_trades.sqlite
- user_data/tradesv3.sqlite
- freqtrade/tradesv3.sqlite

### 🎯 Strategies
- user_data/strategies/
- freqtrade/user_data/strategies/
- strategies/active/

### ⚙️ System Resources
- CPU Usage
- Memory Usage
- Disk Usage

### 📈 Monitoring Services
- simple_trading_monitor.py
- strategy_conditions_monitor.py
- emergency_trading_monitor.py

## Παραδείγματα Μηνυμάτων

### Υγιές Σύστημα:
```
✅ Dashboard Status

Συνολική κατάσταση: Όλα τα συστήματα λειτουργούν κανονικά

🤖 Bots: 2/2 τρέχουν
🎯 Strategies: 7 αρχεία
⚙️ CPU: 15.2%, Memory: 60.6%

🕐 Τελευταίος έλεγχος: 14:30:25

🌐 Dashboard: http://localhost:8503
```

### Σύστημα με Προβλήματα:
```
⚠️ Dashboard Status

Συνολική κατάσταση: Βρέθηκαν 2 προβλήματα

🤖 Bots: 0/2 τρέχουν
🎯 Strategies: 7 αρχεία
⚙️ CPU: 5.1%, Memory: 45.2%

🕐 Τελευταίος έλεγχος: 14:30:25

🌐 Dashboard: http://localhost:8503
```

## Ασφάλεια

### Έλεγχος Πρόσβασης
- Μόνο οι χρήστες στη λίστα `ALLOWED_USERS` μπορούν να χρησιμοποιήσουν το bot
- Όλες οι εντολές ελέγχονται για εξουσιοδότηση

### Προστασία Token
- Μην μοιραστείτε ποτέ το Bot Token
- Κρατήστε το αρχείο `bot_config.py` ασφαλές

## Troubleshooting

### Bot δεν απαντά
1. Ελέγξτε αν το Bot Token είναι σωστό
2. Ελέγξτε αν το User ID σας είναι στη λίστα `ALLOWED_USERS`
3. Ελέγξτε τη σύνδεση internet

### Σφάλμα "python-telegram-bot not found"
```bash
pip install python-telegram-bot
```

### Dashboard δεν ξεκινάει
1. Ελέγξτε αν το port 8503 είναι ελεύθερο
2. Ελέγξτε αν το αρχείο `system_status_dashboard.py` υπάρχει
3. Ελέγξτε τα permissions του αρχείου

### Bot σταματάει απροσδόκητα
1. Ελέγξτε τα logs για σφάλματα
2. Ελέγξτε τη σύνδεση internet
3. Επανεκκινήστε το bot

## Αρχεία
- `apps/telegram/system_dashboard_bot.py` - Κύριο script του bot
- `configs/telegram/bot_config.py` - Configuration αρχείο
- `start_telegram_bot.sh` - Script εκκίνησης
- `apps/telegram/README_TELEGRAM_BOT.md` - Αυτό το αρχείο

## Υποστήριξη
Για προβλήματα ή ερωτήσεις, ελέγξτε:
1. Τα logs του bot
2. Την κατάσταση του dashboard
3. Τη σύνδεση δικτύου