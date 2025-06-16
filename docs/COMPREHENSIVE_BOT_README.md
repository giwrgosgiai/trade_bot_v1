# 🤖 Comprehensive Telegram Bot

Ένα ολοκληρωμένο Telegram bot που διαχειρίζεται όλα τα features του Auto Trading System με ένα κλικ από το `/help`.

## 🎯 Χαρακτηριστικά

✅ **Ολοκληρωμένο Control Panel** - Όλα τα features σε ένα bot
✅ **One-Click Access** - Όλα προσβάσιμα από το `/help`
✅ **Real-time Monitoring** - Live system monitoring
✅ **Process Management** - Start/stop όλες τις διεργασίες
✅ **Smart Notifications** - Καθαρά μηνύματα χωρίς εξωτερικές αναφορές
✅ **Interactive Menus** - Εύκολη πλοήγηση με buttons
✅ **Background Processing** - Όλα τρέχουν στο background
✅ **Error Handling** - Robust error handling και recovery

## 🚀 Εγκατάσταση & Εκκίνηση

### Γρήγορη Εκκίνηση
```bash
# Κάνε το script executable
chmod +x start_comprehensive_bot.sh

# Ξεκίνα το bot
./start_comprehensive_bot.sh
```

### Σταμάτημα Bot
```bash
# Κάνε το script executable
chmod +x stop_comprehensive_bot.sh

# Σταμάτα το bot
./stop_comprehensive_bot.sh
```

### Manual Εκκίνηση
```bash
# Ενεργοποίηση virtual environment (αν υπάρχει)
source myenv/bin/activate

# Εγκατάσταση dependencies
pip install python-telegram-bot psutil

# Εκκίνηση bot
python comprehensive_telegram_bot.py
```

## 📱 Χρήση

### Βασικές Εντολές
- `/start` - Ξεκίνα το bot και δες welcome message
- `/help` - **Κύριο menu με όλα τα features**
- `/status` - Γρήγορο system status
- `/stop_all` - Emergency stop όλων των διεργασιών

### 🎯 Main Menu Features

Όταν πατάς `/help`, βλέπεις το κύριο menu με 8 κατηγορίες:

#### 🚀 Auto Backtesting
- **Quick Backtest** - Γρήγορο backtest με default settings
- **X5 Backtest** - Backtest με 5x leverage
- **Comprehensive BT** - Πλήρες comprehensive backtesting
- **Simple BT Basic** - Βασικό simple backtesting
- **View Results** - Δες αποτελέσματα backtests
- **Stop Backtest** - Σταμάτα τρέχον backtest

#### 🧠 AI Monitoring
- **Start/Stop AI Monitor** - Control AI monitoring system
- **AI Status** - Τρέχων status AI systems
- **AI Activity Log** - Δες log δραστηριότητας
- **Smart Monitor** - Έξυπνο monitoring με auto-detection
- **Auto Monitor** - Αυτόματο monitoring system

#### 📊 Data Management
- **Download Data** - Κατέβασε νέα trading data
- **Update Data** - Ενημέρωση υπάρχοντων data
- **Data Status** - Έλεγχος status των data
- **Manage Files** - Διαχείριση αρχείων
- **Cleanup Data** - Καθαρισμός παλιών data
- **Backup Data** - Backup των data

#### ⚙️ Strategy Tools
- **List Strategies** - Δες όλες τις strategies
- **Test Strategy** - Test μια strategy
- **Strategy Config** - Διαμόρφωση strategy
- **Strategy Stats** - Στατιστικά strategies
- **Optimize Strategy** - Strategy optimization
- **Compare Strategies** - Σύγκριση strategies

#### 📈 System Status
- **System Info** - Πληροφορίες συστήματος
- **Resource Usage** - CPU, Memory, Disk usage
- **Process List** - Τρέχουσες διεργασίες
- **Performance** - Performance metrics
- **Disk Usage** - Χώρος δίσκου
- **Network Status** - Network connectivity

#### 🔧 Process Control
- **Start/Stop Freqtrade** - Control Freqtrade
- **Restart System** - Restart όλο το σύστημα
- **Kill All Python** - Σκότωσε Python processes
- **Service Status** - Status των services
- **Manage Services** - Διαχείριση services

#### 📱 Quick Actions
- **Quick Start** - Ξεκίνα όλα τα βασικά με ένα κλικ
- **Emergency Stop** - Σταμάτα όλα άμεσα
- **Quick Status** - Γρήγορο status check
- **Quick Restart** - Restart όλο το σύστημα
- **Quick Backup** - Γρήγορο backup
- **Quick Cleanup** - Καθαρισμός temp files

#### 🛠️ Advanced Tools
- **Debug Mode** - Enable debug logging
- **View Logs** - Δες system logs
- **Config Editor** - Edit configurations
- **Test Suite** - Run test suites
- **Analytics** - Detailed analytics
- **Maintenance** - System maintenance

## 🔄 Workflow

### Τυπικό Workflow
1. **Στείλε `/help`** - Δες το main menu
2. **Επίλεξε κατηγορία** - π.χ. "🚀 Auto Backtesting"
3. **Επίλεξε action** - π.χ. "Quick Backtest"
4. **Περίμενε notification** - Θα λάβεις update όταν τελειώσει
5. **Δες αποτελέσματα** - Μέσω του menu ή notifications

### Quick Start Workflow
1. **Στείλε `/help`**
2. **Πάτα "📱 Quick Actions"**
3. **Πάτα "⚡ Quick Start"**
4. **Όλα ξεκινούν αυτόματα!**

## 🔔 Notifications

Το bot στέλνει notifications για:

### ✅ Επιτυχημένες Ενέργειες
- Backtesting completed
- Data download finished
- Monitoring started
- System status updates

### ❌ Errors & Failures
- Process failures
- System errors
- Resource warnings
- Timeout alerts

### 📊 Status Updates
- Process completion
- System performance
- Resource usage
- Activity summaries

## 🛡️ Ασφάλεια & Privacy

### Καθαρά Μηνύματα
- **Χωρίς εξωτερικές αναφορές** - Όλες οι αναφορές σε exchanges αφαιρούνται
- **Χωρίς links** - Όλα τα URLs αφαιρούνται από τα μηνύματα
- **Καθαρό περιεχόμενο** - Μόνο essential πληροφορίες

### Process Isolation
- Κάθε action τρέχει σε ξεχωριστό process
- Background monitoring
- Safe process termination
- Resource cleanup

## 🔧 Configuration

### Bot Settings
```python
# Στο comprehensive_telegram_bot.py
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = YOUR_CHAT_ID
```

### Monitoring Settings
```python
# Monitoring intervals
check_interval = 10  # seconds
timeout_threshold = 300  # seconds
activity_threshold = 15.0  # CPU percentage
```

## 📊 Monitoring & Logging

### Log Files
- `telegram_bot.log` - Bot activity log
- `ai_smart_monitor.log` - AI monitoring log
- `auto_download_binance_candles.log` - Data download log

### Real-time Monitoring
- CPU usage monitoring
- Memory usage tracking
- Process monitoring
- Activity detection

## 🚨 Troubleshooting

### Bot Δεν Ξεκινάει
```bash
# Check dependencies
pip install python-telegram-bot psutil

# Check bot token
python -c "import telegram; bot = telegram.Bot('YOUR_TOKEN'); print(bot.get_me())"

# Check permissions
chmod +x start_comprehensive_bot.sh
```

### Processes Δεν Σταματούν
```bash
# Force stop all
./stop_comprehensive_bot.sh

# Manual cleanup
pkill -f "comprehensive_telegram_bot.py"
pkill -f "python"
```

### Memory Issues
```bash
# Check memory usage
free -h

# Restart system
sudo reboot
```

## 🔄 Updates & Maintenance

### Regular Maintenance
1. **Check logs** - Δες τα log files για errors
2. **Clean temp files** - Χρησιμοποίησε "Quick Cleanup"
3. **Update data** - Regular data updates
4. **Monitor resources** - Έλεγχος CPU/Memory usage

### Updates
```bash
# Pull latest changes
git pull

# Restart bot
./stop_comprehensive_bot.sh
./start_comprehensive_bot.sh
```

## 📞 Support

### Common Issues
- **Bot not responding**: Restart με `./start_comprehensive_bot.sh`
- **High CPU usage**: Χρησιμοποίησε "Emergency Stop"
- **Memory warnings**: Restart system
- **Process stuck**: Χρησιμοποίησε "Kill All Python"

### Debug Mode
Για debugging, enable debug mode από το "🛠️ Advanced Tools" menu.

---

## 🎉 Enjoy!

Το Comprehensive Telegram Bot σου δίνει πλήρη έλεγχο του trading system σου με ένα κλικ!

**Πάτα `/help` και ξεκίνα! 🚀**