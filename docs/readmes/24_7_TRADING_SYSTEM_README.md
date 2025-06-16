# 🚀 24/7 Trading System - Σύστημα Trading χωρίς Διακοπές

Ένα ολοκληρωμένο σύστημα trading που τρέχει 24/7 χωρίς διακοπές με αυτόματη επανεκκίνηση, monitoring και hot-reload capabilities.

## 🎯 Χαρακτηριστικά

- **24/7 Λειτουργία**: Τρέχει συνεχώς χωρίς διακοπές
- **Auto-Restart**: Αυτόματη επανεκκίνηση σε περίπτωση σφάλματος
- **Hot Updates**: Ενημερώσεις χωρίς διακοπή του trading
- **Health Monitoring**: Συνεχής παρακολούθηση υγείας των υπηρεσιών
- **Systemd Integration**: Αυτόματη εκκίνηση στο boot
- **Log Management**: Αυτόματη διαχείριση και rotation των logs

## 🏗️ Αρχιτεκτονική

### Υπηρεσίες (Services)

| Port | Υπηρεσία | Περιγραφή | Critical |
|------|----------|-----------|----------|
| 8000 | Strategy Dashboard | Παρακολούθηση στρατηγικών | ❌ |
| 8001 | Advanced Trading UI | Κύρια διεπαφή trading | ✅ |
| 8081 | Web Trades Dashboard | Παρακολούθηση συναλλαγών | ❌ |

### Αρχεία Συστήματος

- `24_7_trading_system.py` - Κύριος διαχειριστής συστήματος
- `hot_update_system.py` - Σύστημα hot updates
- `setup_24_7_system.sh` - Script εγκατάστασης
- `trading-system.service` - Systemd service file

## 🚀 Εγκατάσταση

### 1. Γρήγορη Εγκατάσταση

```bash
# Εκτέλεση ως κανονικός χρήστης (user service)
./setup_24_7_system.sh

# Ή ως root για system service
sudo ./setup_24_7_system.sh
```

### 2. Χειροκίνητη Εγκατάσταση

```bash
# Εγκατάσταση dependencies
source myenv/bin/activate
pip install psutil schedule watchdog requests flask fastapi uvicorn

# Δημιουργία systemd service
sudo cp trading-system.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable trading-system
sudo systemctl start trading-system
```

## 🛠️ Διαχείριση

### Βασικές Εντολές

```bash
# Εκκίνηση συστήματος
./start_24_7_system.sh

# Διακοπή συστήματος
./stop_24_7_system.sh

# Επανεκκίνηση συστήματος
./restart_24_7_system.sh

# Έλεγχος κατάστασης
./status_24_7_system.sh
```

### Systemd Commands

```bash
# System service
sudo systemctl start trading-system
sudo systemctl stop trading-system
sudo systemctl status trading-system
sudo systemctl restart trading-system

# User service
systemctl --user start trading-system
systemctl --user stop trading-system
systemctl --user status trading-system
systemctl --user restart trading-system
```

## 🔄 Hot Updates

### Ενημέρωση Υπηρεσίας

```bash
# Έλεγχος κατάστασης υπηρεσιών
python3 hot_update_system.py status

# Ενημέρωση συγκεκριμένης υπηρεσίας
python3 hot_update_system.py update --service strategy_dashboard --file new_strategy_dashboard.py

# Προγραμματισμένη ενημέρωση (σε 30 λεπτά)
python3 hot_update_system.py update --service advanced_trading_ui --file new_ui.py --delay 30

# Ενημέρωση από Git
python3 hot_update_system.py git-update --branch main
```

### Έλεγχος Syntax

```bash
# Έλεγχος αρχείου πριν την ενημέρωση
python3 hot_update_system.py test --service strategy_dashboard
```

## 📊 Monitoring

### URLs Πρόσβασης

- **Strategy Dashboard**: http://localhost:8000
- **Advanced Trading UI**: http://localhost:8001
- **Web Trades Dashboard**: http://localhost:8081
- **System Monitor**: http://localhost:8001/api/telegram/bot-status

### Logs

```bash
# System logs
tail -f 24_7_trading_system.log

# Health check logs
tail -f health_check.log

# Hot update logs
tail -f hot_update.log

# Systemd logs
journalctl -u trading-system -f
# ή για user service
journalctl --user -u trading-system -f
```

### Health Checks

Το σύστημα εκτελεί αυτόματους ελέγχους κάθε 30 δευτερόλεπτα:

- **Process Check**: Έλεγχος αν τρέχει η διεργασία
- **HTTP Check**: Έλεγχος αν απαντά το HTTP endpoint
- **Auto-Restart**: Αυτόματη επανεκκίνηση σε περίπτωση προβλήματος

## 🔧 Ρυθμίσεις

### Service Configuration

Επεξεργασία του `24_7_trading_system.py`:

```python
# Ρύθμιση υπηρεσιών
services_config = [
    ServiceConfig(
        name="Strategy Dashboard",
        port=8000,
        script_path="strategy_dashboard.py",
        command=["python3", "strategy_dashboard.py"],
        health_check_url="http://localhost:8000",
        restart_delay=5,           # Καθυστέρηση επανεκκίνησης
        max_restarts=10,          # Μέγιστες επανεκκινήσεις
        restart_window=3600,      # Παράθυρο επανεκκινήσεων (1 ώρα)
        critical=False,           # Κρίσιμη υπηρεσία
        auto_reload=True,         # Αυτόματο reload
        watch_files=["strategy_dashboard.py"]  # Αρχεία προς παρακολούθηση
    )
]
```

### Cron Jobs

Το σύστημα δημιουργεί αυτόματα:

```bash
# Health check κάθε 5 λεπτά
*/5 * * * * /home/giwrgosgiai/status_24_7_system.sh >> /home/giwrgosgiai/health_check.log 2>&1

# Log rotation καθημερινά στις 2 π.μ.
0 2 * * * /home/giwrgosgiai/rotate_logs.sh
```

## 🚨 Troubleshooting

### Κοινά Προβλήματα

#### 1. Υπηρεσία δεν εκκινεί

```bash
# Έλεγχος logs
tail -f 24_7_trading_system.log
journalctl -u trading-system -f

# Έλεγχος ports
netstat -tlnp | grep -E ':(8000|8001|8081)'

# Χειροκίνητη εκκίνηση για debugging
cd /home/giwrgosgiai
source myenv/bin/activate
python3 24_7_trading_system.py
```

#### 2. Port σε χρήση

```bash
# Εύρεση διεργασίας που χρησιμοποιεί το port
sudo lsof -i :8001

# Τερματισμός διεργασίας
sudo kill -9 <PID>

# Ή χρήση του built-in port killer
python3 -c "
from 24_7_trading_system import ServiceManager, ServiceConfig
config = ServiceConfig('test', 8001, '', [], '')
manager = ServiceManager(config)
manager._kill_port_process()
"
```

#### 3. Systemd service προβλήματα

```bash
# Επαναφόρτωση systemd
sudo systemctl daemon-reload

# Έλεγχος service file
sudo systemctl cat trading-system

# Έλεγχος permissions
ls -la /etc/systemd/system/trading-system.service
```

#### 4. Hot update αποτυχίες

```bash
# Έλεγχος syntax πριν την ενημέρωση
python3 hot_update_system.py test --service advanced_trading_ui

# Χειροκίνητη επαναφορά από backup
ls -la backups/hot_updates/
cp backups/hot_updates/advanced_trading_ui_20250615_120000 advanced_trading_ui.py
```

### Emergency Recovery

```bash
# Διακοπή όλων των υπηρεσιών
./stop_24_7_system.sh

# Τερματισμός όλων των Python processes
pkill -f python3

# Καθαρισμός ports
for port in 8000 8001 8081; do
    sudo lsof -ti:$port | xargs sudo kill -9 2>/dev/null || true
done

# Επανεκκίνηση
./start_24_7_system.sh
```

## 📈 Performance Tuning

### Βελτιστοποιήσεις

1. **Memory Management**:
   ```python
   # Στο 24_7_trading_system.py
   # Αύξηση memory limits για critical services
   ```

2. **Health Check Frequency**:
   ```python
   # Ρύθμιση συχνότητας health checks
   schedule.every(30).seconds.do(self._health_check_all)  # Default
   schedule.every(10).seconds.do(self._health_check_all)  # Πιο συχνά
   ```

3. **Log Rotation**:
   ```bash
   # Μείωση μεγέθους log files
   # Στο rotate_logs.sh αλλάξτε το MAX_SIZE
   ```

## 🔐 Security

### Βέλτιστες Πρακτικές

1. **Service Isolation**: Κάθε υπηρεσία τρέχει σε ξεχωριστή διεργασία
2. **User Permissions**: Τρέχει με user permissions, όχι root
3. **Network Security**: Bind μόνο σε localhost (εκτός αν χρειάζεται)
4. **Log Security**: Logs δεν περιέχουν sensitive data

### Firewall Configuration

```bash
# Άνοιγμα ports μόνο για local access
sudo ufw allow from 127.0.0.1 to any port 8000
sudo ufw allow from 127.0.0.1 to any port 8001
sudo ufw allow from 127.0.0.1 to any port 8081

# Για remote access (προσοχή!)
sudo ufw allow from <TRUSTED_IP> to any port 8001
```

## 📚 API Reference

### System Manager API

```python
from 24_7_trading_system import TradingSystemManager

manager = TradingSystemManager()

# Εκκίνηση όλων των υπηρεσιών
manager.start_all()

# Διακοπή όλων των υπηρεσιών
manager.stop_all()

# Επανεκκίνηση όλων των υπηρεσιών
manager.restart_all()

# Λήψη κατάστασης
status = manager.get_status()
```

### Hot Update API

```python
from hot_update_system import HotUpdateManager

updater = HotUpdateManager()

# Ενημέρωση υπηρεσίας
success = updater.update_service("strategy_dashboard", "new_file.py")

# Έλεγχος υγείας
healthy = updater.is_service_healthy("advanced_trading_ui")

# Λήψη κατάστασης
status = updater.get_service_status()
```

## 🤝 Contributing

### Development Workflow

1. **Local Testing**:
   ```bash
   # Test changes locally
   python3 hot_update_system.py test --service <service_name>
   ```

2. **Staging Update**:
   ```bash
   # Update non-critical service first
   python3 hot_update_system.py update --service strategy_dashboard --file new_version.py
   ```

3. **Production Update**:
   ```bash
   # Schedule update during low activity
   python3 hot_update_system.py update --service advanced_trading_ui --file new_version.py --delay 60
   ```

### Code Standards

- Ακολουθήστε τα coding standards του repository
- Προσθέστε tests για νέα features
- Ενημερώστε documentation
- Χρησιμοποιήστε type hints

## 📞 Support

### Logs για Support

Όταν αναφέρετε πρόβλημα, συμπεριλάβετε:

```bash
# System status
./status_24_7_system.sh > system_status.txt

# Recent logs
tail -100 24_7_trading_system.log > recent_system.log
tail -100 health_check.log > recent_health.log

# Service status
systemctl --user status trading-system > service_status.txt
```

### Emergency Contacts

- **System Issues**: Έλεγχος logs και restart
- **Trading Issues**: Έλεγχος Advanced Trading UI
- **Performance Issues**: Έλεγχος resource usage

---

## 🎉 Επιτυχής Εγκατάσταση!

Μετά την επιτυχή εγκατάσταση, το σύστημά σας θα:

✅ Τρέχει 24/7 χωρίς διακοπές
✅ Επανεκκινεί αυτόματα σε περίπτωση προβλήματος
✅ Παρακολουθεί την υγεία των υπηρεσιών
✅ Υποστηρίζει hot updates χωρίς διακοπή
✅ Διαχειρίζεται αυτόματα τα logs
✅ Εκκινεί αυτόματα στο boot

**Καλό Trading! 🚀📈**