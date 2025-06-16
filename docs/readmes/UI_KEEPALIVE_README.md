# Trading UI Keepalive System

Αυτό το σύστημα κρατάει το Trading UI ενεργό στο port 8002 και το επανεκκινεί αυτόματα αν σβήσει.

## 🚀 Γρήγορη Εκκίνηση

### Μέθοδος 1: Χειροκίνητη Εκκίνηση
```bash
# Εκκίνηση του keepalive monitor
./start_ui_keepalive.sh
```

### Μέθοδος 2: Systemd Service (Αυτόματη εκκίνηση)
```bash
# Εγκατάσταση του service
./install_ui_service.sh

# Εκκίνηση του service
sudo systemctl start trading-ui

# Έλεγχος κατάστασης
sudo systemctl status trading-ui
```

## 📋 Χαρακτηριστικά

- **Αυτόματη Επανεκκίνηση**: Επανεκκινεί το UI αν σβήσει
- **Έξυπνος Έλεγχος**: Ελέγχει κάθε 30 δευτερόλεπτα
- **Προστασία από Loops**: Μέγιστο 10 επανεκκινήσεις ανά ώρα
- **Καθαρισμός Port**: Σκοτώνει παλιά processes αυτόματα
- **Logging**: Καταγράφει όλες τις ενέργειες
- **Graceful Shutdown**: Καθαρό κλείσιμο με Ctrl+C

## 🔧 Αρχεία Συστήματος

- `keep_ui_alive.py` - Κύριο script παρακολούθησης
- `start_ui_keepalive.sh` - Script εκκίνησης
- `trading-ui.service` - Systemd service file
- `install_ui_service.sh` - Script εγκατάστασης service
- `ui_keepalive.log` - Log file

## 📊 Πρόσβαση στο UI

Το Trading UI είναι διαθέσιμο στο:
- **Local**: http://localhost:8002
- **Network**: http://192.168.2.7:8002

## 🛠️ Εντολές Systemd

```bash
# Εκκίνηση
sudo systemctl start trading-ui

# Διακοπή
sudo systemctl stop trading-ui

# Επανεκκίνηση
sudo systemctl restart trading-ui

# Κατάσταση
sudo systemctl status trading-ui

# Ενεργοποίηση (εκκίνηση στο boot)
sudo systemctl enable trading-ui

# Απενεργοποίηση
sudo systemctl disable trading-ui

# Προβολή logs
journalctl -u trading-ui -f

# Προβολή τελευταίων logs
journalctl -u trading-ui --since "1 hour ago"
```

## 📝 Logs

### Προβολή Keepalive Logs
```bash
# Τελευταίες γραμμές
tail -f ui_keepalive.log

# Όλο το log
cat ui_keepalive.log
```

### Προβολή System Logs
```bash
# Live logs
journalctl -u trading-ui -f

# Τελευταίες 100 γραμμές
journalctl -u trading-ui -n 100
```

## 🔍 Troubleshooting

### Έλεγχος αν τρέχει το UI
```bash
curl http://localhost:8002
```

### Έλεγχος ποια process χρησιμοποιεί το port 8002
```bash
lsof -i :8002
```

### Σκότωμα process στο port 8002
```bash
sudo lsof -ti :8002 | xargs kill -9
```

### Έλεγχος κατάστασης service
```bash
systemctl is-active trading-ui
systemctl is-enabled trading-ui
```

## ⚙️ Ρυθμίσεις

Μπορείς να αλλάξεις τις ρυθμίσεις στο `keep_ui_alive.py`:

```python
self.check_interval = 30      # Έλεγχος κάθε 30 δευτερόλεπτα
self.max_restarts = 10        # Μέγιστο 10 επανεκκινήσεις ανά ώρα
self.ui_port = 8002          # Port του UI
```

## 🚨 Σημαντικές Σημειώσεις

1. **Virtual Environment**: Το σύστημα ενεργοποιεί αυτόματα το `myenv`
2. **Permissions**: Τα scripts πρέπει να είναι executable
3. **Network**: Το UI είναι προσβάσιμο από όλες τις IP (0.0.0.0)
4. **Security**: Το systemd service τρέχει με περιορισμένα δικαιώματα

## 📈 Παρακολούθηση

Το σύστημα παρέχει:
- Real-time logs
- Στατιστικά επανεκκινήσεων
- Κατάσταση υγείας του UI
- Αυτόματη ανάκαμψη από σφάλματα

## 🔄 Ενημερώσεις

Για να ενημερώσεις το σύστημα:

1. Κάνε τις αλλαγές στα αρχεία
2. Επανεκκίνησε το service:
   ```bash
   sudo systemctl restart trading-ui
   ```

Ή για χειροκίνητη λειτουργία, απλά σταμάτα και ξεκίνα ξανά το script.