# 🛠️ Scripts Manager UI

Ένα όμορφο και λειτουργικό web interface για τη διαχείριση όλων των shell scripts στο workspace.

## 🌟 Χαρακτηριστικά

### 📊 Οργάνωση Scripts
- **Αυτόματη κατηγοριοποίηση** σε 7 κατηγορίες:
  - 🚀 **Start Scripts** - Εκκίνηση υπηρεσιών
  - 🛑 **Stop Scripts** - Σταμάτημα υπηρεσιών
  - 🔧 **Setup Scripts** - Εγκατάσταση και ρύθμιση
  - 📋 **Management Scripts** - Διαχείριση συστήματος
  - 🗂️ **Organization Scripts** - Οργάνωση workspace
  - 📊 **Monitoring Scripts** - Παρακολούθηση συστήματος
  - 🛠️ **Utility Scripts** - Βοηθητικά scripts

### 📝 Πλήρεις Πληροφορίες
Για κάθε script εμφανίζονται:
- **Όνομα και περιγραφή**
- **Χαρακτηριστικά και δυνατότητες**
- **Απαιτήσεις συστήματος**
- **Ports που χρησιμοποιεί**
- **Log files που δημιουργεί**
- **Μέγεθος αρχείου και τελευταία τροποποίηση**
- **Κατάσταση εκτελεσιμότητας**

### ⚡ Εκτέλεση Scripts
- **Άμεση εκτέλεση** με ένα κλικ
- **Background εκτέλεση** για long-running scripts
- **Real-time αποτελέσματα** με stdout/stderr
- **Έλεγχος σφαλμάτων** και timeout protection

### 🎨 Όμορφο UI
- **Modern responsive design**
- **Χρωματική κωδικοποίηση** κατηγοριών
- **Interactive cards** με hover effects
- **Modal dialogs** για εκτέλεση
- **Auto-refresh** κάθε 30 δευτερόλεπτα

## 🚀 Εκκίνηση

### Γρήγορη Εκκίνηση
```bash
./scripts_ui.sh
```

### Χειροκίνητη Εκκίνηση
```bash
./start_scripts_manager.sh
```

### Πρόσβαση
- **URL**: http://localhost:8002
- **Port**: 8002
- **Auto-refresh**: Κάθε 30 δευτερόλεπτα

## 📋 Διαθέσιμα Scripts

### 🚀 Start Scripts (18 scripts)
- **24/7 Trading System** - Σύστημα που κρατάει telegram και freqtrade ανοιχτά 24/7
- **Advanced Trading UI** - Πλήρες trading σύστημα με real-time monitoring
- **Beautiful Telegram Bot** - Όμορφο telegram bot με formatted messages
- **Clean Trading System** - Καθαρό trading σύστημα χωρίς περιττά
- **Greek Trading Bot** - Ελληνικό trading bot
- και άλλα...

### 🛑 Stop Scripts (7 scripts)
- **Stop 24/7 System** - Σταμάτημα 24/7 monitoring
- **Stop Advanced Trading UI** - Σταμάτημα advanced trading UI
- **Stop All Bots** - Σταμάτημα όλων των telegram bots
- και άλλα...

### 🔧 Setup Scripts (3 scripts)
- **Setup 24/7 System** - Εγκατάσταση 24/7 monitoring
- **Setup Beautiful Telegram** - Εγκατάσταση telegram bot
- **Setup Cron Mock API** - Εγκατάσταση cron jobs
- και άλλα...

### 📋 Management Scripts (3 scripts)
- **Trading System Manager** - Διαχείριση trading συστήματος
- **System Status Checker** - Έλεγχος κατάστασης υπηρεσιών
- **Check and Restart Mock API** - Έλεγχος Mock API
- και άλλα...

### 🗂️ Organization Scripts (4 scripts)
- **Smart Workspace Organizer** - Έξυπνη οργάνωση αρχείων
- **Complete Organizer** - Πλήρης οργάνωση workspace
- **Quick Organizer** - Γρήγορη οργάνωση
- **Organize** - Master organization script

### 📊 Monitoring Scripts (3 scripts)
- **Strategy Monitor** - Παρακολούθηση trading strategies
- **UI Status Monitor** - Έλεγχος κατάστασης UI εφαρμογών
- **Status 24/7 System** - Κατάσταση 24/7 συστήματος

### 🛠️ Utility Scripts (12 scripts)
- **UI Mode Toggle** - Εναλλαγή UI modes
- **Switch to Keepalive** - Μετάβαση σε keepalive mode
- **iPhone UI Access** - Πρόσβαση από iPhone
- **Quick Access** - Γρήγορη πρόσβαση σε αρχεία
- και άλλα...

## 🔧 Τεχνικές Λεπτομέρειες

### Τεχνολογίες
- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla JavaScript + HTML/CSS
- **Styling**: Modern CSS με gradients και animations
- **API**: RESTful endpoints

### Αρχιτεκτονική
```
scripts_manager_ui.py
├── ScriptsManager Class
│   ├── scan_scripts() - Σάρωση όλων των scripts
│   ├── get_script_info() - Πληροφορίες script
│   ├── categorize_script() - Κατηγοριοποίηση
│   └── execute_script() - Εκτέλεση script
├── FastAPI Routes
│   ├── GET / - Κύρια σελίδα HTML
│   ├── GET /api/scripts - Λίστα scripts
│   ├── POST /api/scripts/execute - Εκτέλεση
│   └── GET /api/scripts/{name} - Λεπτομέρειες
└── HTML Template με JavaScript
```

### API Endpoints

#### GET /api/scripts
Επιστρέφει όλα τα scripts κατηγοριοποιημένα:
```json
{
  "scripts": {
    "start": [...],
    "stop": [...],
    ...
  },
  "categories": {...},
  "total_scripts": 50,
  "last_scan": "2025-06-15T09:30:00"
}
```

#### POST /api/scripts/execute
Εκτελεί ένα script:
```json
{
  "script_path": "/path/to/script.sh",
  "background": false
}
```

#### GET /api/scripts/{script_name}
Επιστρέφει λεπτομέρειες για συγκεκριμένο script.

## 📊 Στατιστικά

- **Σύνολο Scripts**: 50
- **Κατηγορίες**: 7
- **Start Scripts**: 18
- **Stop Scripts**: 7
- **Setup Scripts**: 3
- **Management Scripts**: 3
- **Organization Scripts**: 4
- **Monitoring Scripts**: 3
- **Utility Scripts**: 12

## 🔒 Ασφάλεια

- **Timeout Protection**: Scripts timeout μετά από 30 δευτερόλεπτα
- **Error Handling**: Graceful handling σφαλμάτων
- **File Validation**: Έλεγχος ύπαρξης αρχείων
- **Permission Check**: Έλεγχος εκτελεσιμότητας

## 📝 Logs

- **Scripts Manager Log**: `data/logs/scripts_manager.log`
- **Execution Logs**: Εμφανίζονται στο UI
- **Error Logs**: Καταγράφονται στο κύριο log

## 🛑 Σταμάτημα

```bash
# Σταμάτημα Scripts Manager
pkill -f scripts_manager_ui.py

# Έλεγχος κατάστασης
pgrep -f scripts_manager_ui.py

# Παρακολούθηση logs
tail -f data/logs/scripts_manager.log
```

## 🎯 Χρήση

1. **Εκκίνηση**: `./scripts_ui.sh`
2. **Πρόσβαση**: http://localhost:8002
3. **Επιλογή Script**: Κλικ σε κάρτα script
4. **Εκτέλεση**: Κλικ "Εκτέλεση" ή "Background"
5. **Παρακολούθηση**: Παρακολούθηση αποτελεσμάτων στο modal

## 🔄 Auto-Refresh

Το UI ανανεώνεται αυτόματα κάθε 30 δευτερόλεπτα για:
- Νέα scripts
- Αλλαγές σε υπάρχοντα scripts
- Ενημερωμένες πληροφορίες

## 📱 Mobile Support

Το UI είναι πλήρως responsive και λειτουργεί σε:
- Desktop browsers
- Tablets
- Mobile phones
- iPhone (με ειδικό script: `iphone_ui_access.sh`)

---

**🎉 Απόλαυσε τη διαχείριση των scripts σου με στυλ!**