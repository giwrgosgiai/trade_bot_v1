# 🚀 Complete Live Trading System

Ένα ολοκληρωμένο σύστημα παρακολούθησης ζωντανών συναλλαγών με **κέρδη σε USDT** (όχι ποσοστά).

## 📋 Περιεχόμενα

- [Γρήγορη Εκκίνηση](#-γρήγορη-εκκίνηση)
- [Συστατικά Μέρη](#-συστατικά-μέρη)
- [Εγκατάσταση](#-εγκατάσταση)
- [Χρήση](#-χρήση)
- [Telegram Bot](#-telegram-bot)
- [Web Dashboard](#-web-dashboard)
- [Αντιμετώπιση Προβλημάτων](#-αντιμετώπιση-προβλημάτων)

## 🚀 Γρήγορη Εκκίνηση

### 1. Εκκίνηση Όλου του Συστήματος
```bash
./start_complete_system.sh
```

### 2. Πρόσβαση στο Web Dashboard
- **Τοπικά**: http://localhost:8081
- **Δίκτυο**: http://192.168.2.7:8081

### 3. Έλεγχος Κατάστασης
```bash
./check_system_status.sh
```

### 4. Διακοπή Συστήματος
```bash
./stop_complete_system.sh
```

## 🔧 Συστατικά Μέρη

### 1. **Freqtrade Trading Bot**
- **Λειτουργία**: Paper trading με 2000 USDT
- **API**: http://localhost:8080
- **Στρατηγική**: UltimateProfitStrategyOptimized
- **Ζεύγη**: BTC/USDT, ETH/USDT, SOL/USDT, ADA/USDT, BNB/USDT, DOGE/USDT

### 2. **Web Dashboard**
- **URL**: http://localhost:8081
- **Χαρακτηριστικά**:
  - Ανοιχτές συναλλαγές
  - Πρόσφατες κλειστές συναλλαγές
  - Κέρδη σε USDT (όχι ποσοστά)
  - Αυτόματη ανανέωση κάθε 30 δευτερόλεπτα

### 3. **Telegram Bot**
- **Εντολές**: `/start`, `/trades`, `/profit`
- **Χαρακτηριστικά**:
  - Διαδραστικά κουμπιά
  - Περιοδικές ενημερώσεις
  - Κέρδη σε USDT

## 📦 Εγκατάσταση

### Προαπαιτούμενα
```bash
# Python dependencies
pip install flask requests python-telegram-bot

# System tools
sudo apt-get install curl netstat-nat
```

### Αρχεία Συστήματος
- `live_trading_config.json` - Ρυθμίσεις Freqtrade
- `live_trades_telegram_bot.py` - Telegram Bot
- `web_trades_dashboard.py` - Web Dashboard
- `start_complete_system.sh` - Εκκίνηση όλων
- `stop_complete_system.sh` - Διακοπή όλων
- `check_system_status.sh` - Έλεγχος κατάστασης

## 🎮 Χρήση

### Εκκίνηση Συστήματος
```bash
# Εκκίνηση όλων των συστημάτων
./start_complete_system.sh

# Εκκίνηση μόνο Web Dashboard
python web_trades_dashboard.py

# Εκκίνηση μόνο Freqtrade
cd freqtrade && python -m freqtrade trade --config ../live_trading_config.json
```

### Παρακολούθηση
```bash
# Έλεγχος κατάστασης
./check_system_status.sh

# Παρακολούθηση logs
tail -f logs/*.log

# Παρακολούθηση συγκεκριμένου log
tail -f logs/freqtrade_live.log
```

## 🤖 Telegram Bot

### Ρύθμιση
```bash
# Ρύθμιση environment variables
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"

# Εκκίνηση bot
python live_trades_telegram_bot.py
```

### Εντολές
- `/start` - Κύριο μενού με κουμπιά
- `/trades` - Ανοιχτές συναλλαγές
- `/profit` - Συνοψη κερδών

### Χαρακτηριστικά
- **Κέρδη σε USDT**: Εμφανίζει +15.50 USDT αντί για 2.1%
- **Διαδραστικά κουμπιά**: Εύκολη πλοήγηση
- **Περιοδικές ενημερώσεις**: Κάθε 30 λεπτά
- **Χρονική διάρκεια**: Εμφανίζει πόσο καιρό είναι ανοιχτή κάθε συναλλαγή

## 🌐 Web Dashboard

### Πρόσβαση
- **Τοπικά**: http://localhost:8081
- **Δίκτυο**: http://192.168.2.7:8081

### Χαρακτηριστικά
- **Responsive Design**: Λειτουργεί σε κινητά και desktop
- **Real-time Updates**: Αυτόματη ανανέωση κάθε 30 δευτερόλεπτα
- **Demo Mode**: Εμφανίζει demo δεδομένα όταν το Freqtrade δεν τρέχει
- **Κέρδη σε USDT**: Όλα τα κέρδη εμφανίζονται σε USDT

### Ενότητες
1. **Ανοιχτές Συναλλαγές**
   - Ζεύγος συναλλαγής
   - Κέρδος σε USDT και ποσοστό
   - Διάρκεια συναλλαγής

2. **Πρόσφατες Συναλλαγές**
   - Τελευταίες 10 κλειστές συναλλαγές
   - Ώρα κλεισίματος
   - Κέρδος/ζημία σε USDT

3. **Συνοψη Κερδών**
   - Συνολικά κέρδη
   - Τρέχον κέρδος
   - Υπόλοιπο λογαριασμού
   - Αριθμός συναλλαγών
   - Ποσοστό επιτυχίας

## 🔧 Ρυθμίσεις

### Freqtrade Configuration
```json
{
    "dry_run": true,
    "dry_run_wallet": 2000,
    "max_open_trades": 6,
    "stake_amount": 300,
    "api_server": {
        "enabled": true,
        "listen_port": 8080,
        "username": "freqtrade",
        "password": "freqtrade123"
    }
}
```

### Telegram Bot Environment
```bash
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="123456789"
```

## 🚨 Αντιμετώπιση Προβλημάτων

### Συχνά Προβλήματα

#### 1. Freqtrade δεν ξεκινάει
```bash
# Έλεγχος logs
tail -f logs/freqtrade_live.log

# Έλεγχος configuration
python -m freqtrade show-config --config live_trading_config.json
```

#### 2. Web Dashboard δεν φορτώνει
```bash
# Έλεγχος αν τρέχει
pgrep -f web_trades_dashboard.py

# Έλεγχος port
netstat -tuln | grep 8081

# Restart
pkill -f web_trades_dashboard.py
python web_trades_dashboard.py
```

#### 3. Telegram Bot δεν απαντάει
```bash
# Έλεγχος environment variables
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID

# Έλεγχος logs
tail -f logs/telegram_bot.log
```

#### 4. API Connection Errors
```bash
# Test Freqtrade API
curl -u freqtrade:freqtrade123 http://localhost:8080/api/v1/ping

# Check if port is open
netstat -tuln | grep 8080
```

### Logs Locations
- **Freqtrade**: `logs/freqtrade_live.log`
- **Web Dashboard**: `logs/web_dashboard.log`
- **Telegram Bot**: `logs/telegram_bot.log`

### Επανεκκίνηση Συστήματος
```bash
# Πλήρης επανεκκίνηση
./stop_complete_system.sh
sleep 5
./start_complete_system.sh
```

## 📊 Παρακολούθηση Απόδοσης

### Σημαντικοί Δείκτες
- **Κέρδη σε USDT**: Πραγματικό κέρδος σε δολάρια
- **Ποσοστό Επιτυχίας**: Κερδοφόρες vs ζημιογόνες συναλλαγές
- **Διάρκεια Συναλλαγών**: Πόσο καιρό μένουν ανοιχτές
- **Συχνότητα Συναλλαγών**: Πόσες συναλλαγές ανά ημέρα

### Αναμενόμενη Συμπεριφορά
- **Εκκίνηση συναλλαγών**: 1-5 λεπτά μετά την εκκίνηση
- **Διάρκεια συναλλαγών**: 30 λεπτά - 4 ώρες
- **Μέγιστες ανοιχτές**: 6 συναλλαγές ταυτόχρονα
- **Timeframe**: 5 λεπτά κεριά

## 🎯 Χρήσιμες Εντολές

```bash
# Γρήγορος έλεγχος κατάστασης
./check_system_status.sh

# Παρακολούθηση όλων των logs
tail -f logs/*.log

# Restart μόνο Web Dashboard
pkill -f web_trades_dashboard.py && python web_trades_dashboard.py &

# Restart μόνο Telegram Bot
pkill -f live_trades_telegram_bot.py && python live_trades_telegram_bot.py &

# Έλεγχος API
curl -u freqtrade:freqtrade123 http://localhost:8080/api/v1/status | jq

# Έλεγχος κερδών
curl -u freqtrade:freqtrade123 http://localhost:8080/api/v1/profit | jq
```

## 📞 Υποστήριξη

Για προβλήματα ή ερωτήσεις:
1. Ελέγξτε τα logs: `tail -f logs/*.log`
2. Τρέξτε status check: `./check_system_status.sh`
3. Επανεκκινήστε το σύστημα: `./stop_complete_system.sh && ./start_complete_system.sh`

---

**🎉 Καλή επιτυχία με τις συναλλαγές σας!**