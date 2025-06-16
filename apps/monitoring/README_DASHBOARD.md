# System Status Dashboard

## Περιγραφή
Το System Status Dashboard είναι ένα web-based εργαλείο που σας επιτρέπει να ελέγχετε την κατάσταση όλων των συστημάτων σας με ένα κλικ.

## Χαρακτηριστικά
- 🤖 **Έλεγχος Trading Bots**: Ελέγχει αν τα Freqtrade bots τρέχουν (ports 8081, 8082)
- 💾 **Έλεγχος Databases**: Ελέγχει την κατάσταση των SQLite databases και JSON αρχείων
- 🎯 **Έλεγχος Strategies**: Μετράει τα strategy αρχεία σε διάφορους φακέλους
- ⚙️ **System Resources**: Παρακολουθεί CPU, Memory και Disk usage
- 📈 **Monitoring Services**: Ελέγχει αν τρέχουν τα monitoring scripts

## Εκκίνηση

### Μέθοδος 1: Με το script
```bash
./start_system_dashboard.sh
```

### Μέθοδος 2: Απευθείας
```bash
python3 apps/monitoring/system_status_dashboard.py
```

## Πρόσβαση
Μετά την εκκίνηση, ανοίξτε τον browser και πηγαίνετε στο:
```
http://localhost:8503
```

## Χρήση
1. Πατήστε το κουμπί **"🚀 Έλεγχος Συστημάτων"**
2. Περιμένετε 3-5 δευτερόλεπτα για τον έλεγχο
3. Δείτε τα αποτελέσματα σε κάρτες:
   - **Πράσινο**: Όλα καλά
   - **Κίτρινο**: Προειδοποίηση
   - **Κόκκινο**: Πρόβλημα

## API Endpoints

### GET /api/status
Επιστρέφει την τρέχουσα κατάσταση όλων των συστημάτων.

### POST /api/check
Ξεκινάει νέο έλεγχο όλων των συστημάτων.

## Παραδείγματα API

### Έλεγχος κατάστασης
```bash
curl http://localhost:8503/api/status
```

### Εκκίνηση νέου ελέγχου
```bash
curl -X POST http://localhost:8503/api/check
```

## Αυτόματη Ανανέωση
Το dashboard ανανεώνεται αυτόματα κάθε 5 λεπτά.

## Τερματισμός
Πατήστε `Ctrl+C` στο terminal για να σταματήσετε το dashboard.

## Troubleshooting

### Port 8503 σε χρήση
Αν το port είναι ήδη σε χρήση:
```bash
# Δείτε τι τρέχει
lsof -i :8503

# Σταματήστε τη διεργασία
kill <PID>
```

### Σφάλματα σύνδεσης
- Ελέγξτε αν τα Freqtrade bots τρέχουν στα ports 8081, 8082
- Ελέγξτε αν έχετε τα σωστά credentials (freqtrade:ruriu7AY)

### Αργή απόκριση
- Το σύστημα μπορεί να είναι φορτωμένο
- Ελέγξτε τη χρήση CPU/Memory στο dashboard

## Αρχεία
- `apps/monitoring/system_status_dashboard.py` - Κύριο script
- `start_system_dashboard.sh` - Script εκκίνησης
- `bot_monitor_status.json` - Αρχείο κατάστασης bots