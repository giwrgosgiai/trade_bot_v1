# Auto Backtesting System για Freqtrade

Ένα modular automated backtesting system με hang detection, retry mechanism και **Telegram Integration** για το Freqtrade.

## 🎯 Χαρακτηριστικά

✅ **Timeout Monitoring**: Ανιχνεύει εάν το backtesting έχει "κολλήσει" και το επανεκκινεί
✅ **Retry Mechanism**: Αυτόματα επαναλαμβάνει failed attempts
✅ **📱 Telegram Integration**: Live notifications και interactive control
✅ **🤖 Interactive Decisions**: Επιλογή από Telegram με buttons
✅ **Modular Design**: Καθαρός, maintainable κώδικας με type hints
✅ **Comprehensive Testing**: 80%+ test coverage με TDD approach
✅ **Configurable**: Εύκολη διαμόρφωση παραμέτρων

## 🆕 Τι Νέο με Telegram:

### **📱 Live Notifications**
- 🚀 Ξεκίνημα backtesting
- 📊 Progress updates
- ✅ Επιτυχημένη ολοκλήρωση
- ❌ Errors και failures
- ⏱️ Hang detection alerts

### **🤖 Interactive Control**
Όταν ανιχνεύει hang, σου στέλνει message με buttons:
- **⏳ Περίμενε άλλα 5 λεπτά**: Επέκτεινε το timeout
- **💀 Kill & Restart**: Σκότωσε και ξαναδοκίμασε
- **🛑 Abort εντελώς**: Σταμάτα το backtesting

## 📁 Δομή Project

```
user_data/
├── auto_backtest/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration management
│   ├── watchdog.py          # Timeout monitoring
│   ├── backtest_runner.py   # Main backtesting logic
│   ├── telegram_bot.py      # 🆕 Telegram integration
│   ├── main.py              # CLI entry point
│   ├── run_tests.py         # Test runner
│   └── tests/
│       ├── __init__.py
│       ├── test_config.py
│       ├── test_watchdog.py
│       └── test_backtest_runner.py
├── config.json              # Freqtrade configuration
└── ...
auto_backtest.py             # Standalone CLI wrapper
setup_telegram.py            # 🆕 Telegram setup helper
requirements.txt             # Dependencies
telegram_config.sh           # 🆕 Telegram credentials (after setup)
```

## 🚀 Εγκατάσταση

### 1. **Εγκατάσταση Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Setup Telegram Bot (Optional)**
```bash
python setup_telegram.py
```

Αυτό θα σε καθοδηγήσει για:
- Δημιουργία bot στον @BotFather
- Εύρεση Chat ID
- Test της σύνδεσης
- Αποθήκευση configuration

### 3. **Βεβαίωση Freqtrade**
Βεβαιώσου ότι το Freqtrade είναι εγκατεστημένο και configured.

## 💫 Χρήση

### **Βασική Χρήση (χωρίς Telegram)**
```bash
python auto_backtest.py --strategy MyStrategy --timerange 20250101-20250201
```

### **🤖 Με Telegram Notifications**
```bash
# Αφού τρέξεις setup_telegram.py
source telegram_config.sh

python auto_backtest.py \
    --telegram-enabled \
    --telegram-bot-token $TELEGRAM_BOT_TOKEN \
    --telegram-chat-id $TELEGRAM_CHAT_ID \
    --strategy PandasTaStrategy \
    --timerange 20250102-20250109 \
    --hang-timeout 120
```

### **📋 Παράμετροι CLI**

| Παράμετρος | Default | Περιγραφή |
|------------|---------|-----------|
| `--config` | `user_data/config.json` | Path στο freqtrade config |
| `--strategy` | `PandasTaStrategy` | Όνομα strategy |
| `--timerange` | `20250102-20250109` | Timerange για backtesting |
| `--breakdown` | `month` | Breakdown period |
| `--max-retries` | `10` | Μέγιστος αριθμός προσπαθειών |
| `--retry-wait` | `10` | Αναμονή μεταξύ retries (seconds) |
| `--hang-timeout` | `300` | Timeout για hang detection (seconds) |
| `--exchange` | `binance` | Exchange για data download |
| `--timeframe` | `5m` | Timeframe για data download |
| **🆕 `--telegram-enabled`** | `False` | **Enable Telegram notifications** |
| **🆕 `--telegram-bot-token`** | `None` | **Telegram bot token** |
| **🆕 `--telegram-chat-id`** | `None` | **Telegram chat ID** |

## 🔧 Programmatic Usage

### **Χωρίς Telegram**
```python
from user_data.auto_backtest import BacktestConfig, BacktestRunner

config = BacktestConfig(
    strategy="MyStrategy",
    timerange="20250101-20250201",
    max_retries=5,
    hang_timeout=600
)

runner = BacktestRunner(config)
success = runner.run()
```

### **🤖 Με Telegram**
```python
from user_data.auto_backtest import BacktestConfig, BacktestRunner

config = BacktestConfig(
    strategy="MyStrategy",
    timerange="20250101-20250201",
    max_retries=5,
    hang_timeout=600,
    telegram_enabled=True,
    telegram_bot_token="YOUR_BOT_TOKEN",
    telegram_chat_id="YOUR_CHAT_ID"
)

runner = BacktestRunner(config)
success = runner.run()
runner.cleanup()  # Important για Telegram cleanup
```

## 📱 Telegram Features

### **🔄 Workflow με Telegram**

1. **Start**: Στέλνει notification ότι ξεκίνησε
2. **Progress**: Live updates για κάθε attempt
3. **Hang Detection**: Αν κολλήσει → στέλνει buttons για επιλογή
4. **Your Choice**:
   - ⏳ **Wait** → Περιμένει άλλα 5 λεπτά
   - 💀 **Kill** → Restart το process
   - 🛑 **Abort** → Σταματά εντελώς
5. **Result**: Final notification (success/failure)

### **📷 Παράδειγμα Telegram Messages**

```
🚀 Backtesting Started

🚀 Strategy: PandasTaStrategy
📅 Timerange: 20250102-20250109
🔄 Max Retries: 10
⏰ Hang Timeout: 120s

🕐 10:30:25
```

```
🤔 Hang Detection

Process κόλλησε για 120s. Τι να κάνω;

⏰ Timeout: 60s

[⏳ Περίμενε άλλα 5 λεπτά] [💀 Kill & Restart] [🛑 Abort εντελώς]
```

## 🧪 Testing

```bash
# Εκτέλεση όλων των tests
cd user_data/auto_backtest
python run_tests.py

# Test με coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## 🔧 Troubleshooting

### **Telegram Issues**

**1. "Failed to send Telegram message"**
- Βεβαιώσου ότι το bot token είναι σωστό
- Βεβαιώσου ότι έχεις στείλει `/start` στο bot

**2. "Chat not found"**
- Βεβαιώσου ότι το Chat ID είναι σωστό
- Στείλε μήνυμα στο bot πρώτα

**3. "Telegram integration not available"**
```bash
pip install python-telegram-bot>=20.0.0
```

### **Συχνά Προβλήματα**

1. **Import Errors**: Βεβαιωθείτε ότι τρέχετε από το root directory
2. **Permission Errors**: `chmod +x auto_backtest.py setup_telegram.py`
3. **Freqtrade Not Found**: Βεβαιωθείτε ότι το freqtrade είναι στο PATH

## 🎯 Παραδείγματα Χρήσης

### **🔥 Για το πρόβλημα που κόλλησε:**
```bash
# Σκότωσε το κολλημένο process
pkill -9 freqtrade

# Τρέξε με το νέο system (2 λεπτά timeout)
source freqtrade-simple/bin/activate
python auto_backtest.py \
    --strategy PandasTaStrategy \
    --timerange 20250102-20250109 \
    --hang-timeout 120 \
    --max-retries 3
```

### **📱 Με Telegram Control:**
```bash
# Setup telegram (once)
python setup_telegram.py

# Load credentials
source telegram_config.sh

# Run με interactive control
python auto_backtest.py \
    --telegram-enabled \
    --telegram-bot-token $TELEGRAM_BOT_TOKEN \
    --telegram-chat-id $TELEGRAM_CHAT_ID \
    --strategy PandasTaStrategy \
    --timerange 20250102-20250109 \
    --hang-timeout 120
```

Τώρα θα παίρνεις live updates στο κινητό σου και μπορείς να αποφασίζεις τι να κάνεις όταν κολλήσει!

## 🤝 Συνεισφορά

1. Fork το repository
2. Δημιουργήστε feature branch
3. Γράψτε tests για νέα functionality
4. Βεβαιωθείτε ότι όλα τα tests pass
5. Υποβάλετε Pull Request

## 📄 License

Αυτό το project είναι open source και διαθέσιμο υπό τους όρους της MIT License.