# 🚀 Complete Trading System - Organized Structure

## 📁 **ΟΡΓΑΝΩΣΗ ΑΡΧΕΙΩΝ**

```
freqtrade/                              # Κύριο directory
├── enhanced_trading_ui.py              # 🎨 UI Dashboard
├── start_trading_system.sh             # 🚀 Startup Script
├── trading_data_persistent.json        # 💾 UI Data
├── tradesv3.sqlite                     # 📊 Main Database
├── tradesv3.dryrun.sqlite              # 📊 Dry Run Database
├── user_data/                          # 📂 User Configuration
│   ├── config.json                     # ⚙️ Main Config
│   ├── strategies/                     # 📈 Trading Strategies
│   │   └── UltimateProfitStrategy.py   # 💰 Main Strategy
│   ├── data/                           # 📊 Market Data
│   ├── backtest_results/               # 📈 Backtest Results
│   └── logs/                           # 📝 Strategy Logs
├── logs/                               # 📝 System Logs
└── freqtrade/                          # 🤖 Bot Core
```

## ✅ **ΥΠΟΧΡΕΩΤΙΚΑ ΑΡΧΕΙΑ ΓΙΑ ΛΕΙΤΟΥΡΓΙΑ**

### 1. **🤖 FREQTRADE BOT**
- `freqtrade/` - Κύριο bot directory
- `user_data/config.json` - Κύρια διαμόρφωση
- `tradesv3.sqlite` - Database για trades

### 2. **📈 STRATEGY**
- `user_data/strategies/UltimateProfitStrategy.py` - Κύρια στρατηγική

### 3. **🎨 UI DASHBOARD**
- `enhanced_trading_ui.py` - Professional UI
- `trading_data_persistent.json` - UI data storage

### 4. **🚀 STARTUP**
- `start_trading_system.sh` - Complete system startup

## 🔗 **ΣΥΝΔΕΣΕΙΣ ΜΕΤΑΞΥ ΑΡΧΕΙΩΝ**

### **Config → Strategy**
```json
"strategy": "UltimateProfitStrategy"
"strategy_path": "user_data/strategies/"
```

### **Config → Database**
```json
"db_url": "sqlite:///tradesv3.sqlite"
```

### **Config → API**
```json
"api_server": {
  "enabled": true,
  "listen_port": 8080
}
```

### **UI → Freqtrade API**
```python
FREQTRADE_API_URL = "http://127.0.0.1:8080"
```

## 🎯 **ΕΚΚΙΝΗΣΗ ΣΥΣΤΗΜΑΤΟΣ**

### **Αυτόματη Εκκίνηση (Συνιστάται)**
```bash
cd freqtrade
./start_trading_system.sh
```

### **Χειροκίνητη Εκκίνηση**
```bash
# Terminal 1: Start Freqtrade Bot
cd freqtrade
python -m freqtrade trade --config user_data/config.json

# Terminal 2: Start UI Dashboard
cd freqtrade
python enhanced_trading_ui.py
```

## 📊 **ΠΡΟΣΒΑΣΗ**

- **📈 Trading Dashboard**: http://localhost:5001
- **🔧 Freqtrade API**: http://localhost:8080
- **📊 API Docs**: http://localhost:8080/docs

## ⚙️ **ΔΙΑΜΟΡΦΩΣΗ**

### **Dry Run Mode (Προεπιλογή)**
```json
"dry_run": true,
"dry_run_wallet": 500
```

### **Live Trading (Προσοχή!)**
```json
"dry_run": false,
"exchange": {
  "key": "YOUR_API_KEY",
  "secret": "YOUR_SECRET"
}
```

## 📈 **ΣΤΡΑΤΗΓΙΚΗ: UltimateProfitStrategy**

- **Timeframe**: 5m
- **Budget**: €500
- **Target**: 15%+ monthly return
- **Risk**: 0.5% max per trade
- **Features**: AI Learning, Smart Money Flow, Fee-Aware

## 🔧 **TROUBLESHOOTING**

### **Strategy Not Found**
```bash
# Check if strategy exists
ls -la user_data/strategies/UltimateProfitStrategy.py
```

### **Database Issues**
```bash
# Check database
sqlite3 tradesv3.sqlite ".tables"
```

### **API Connection Issues**
```bash
# Check if Freqtrade API is running
curl http://localhost:8080/api/v1/ping
```

### **UI Not Loading**
```bash
# Check if UI is running
curl http://localhost:5001
```

## 📝 **LOGS**

- **Freqtrade**: `logs/freqtrade.log`
- **Strategy**: `user_data/logs/`
- **System**: Console output

## 🎯 **PERFORMANCE TARGETS**

- **Monthly Return**: 15%+ (€75+ on €500)
- **Win Rate**: 80%+
- **Max Drawdown**: <5%
- **Trades/Month**: 20-40
- **Avg Trade**: 2-5% profit

## 🛡️ **SAFETY FEATURES**

- ✅ Dry run mode by default
- ✅ Stop loss: 0.5%
- ✅ Position limits: Max 5 open
- ✅ Fee calculation
- ✅ Risk management

## 📞 **SUPPORT**

Για προβλήματα ή ερωτήσεις:
1. Έλεγχος logs
2. Επαλήθευση διαμόρφωσης
3. Restart συστήματος

---

**🎯 Το σύστημα είναι έτοιμο για χρήση!**