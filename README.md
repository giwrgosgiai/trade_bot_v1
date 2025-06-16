# 🚀 FreqTrade NFI5MOHO Trading Bot

Ένα προηγμένο σύστημα αυτοματοποιημένου trading με FreqTrade, που χρησιμοποιεί τη στρατηγική NFI5MOHO_WIP για cryptocurrency trading.

## 📊 Χαρακτηριστικά

- **🤖 Αυτοματοποιημένο Trading**: Χρήση FreqTrade με βελτιστοποιημένη στρατηγική
- **📱 Telegram Integration**: Πλήρης έλεγχος μέσω Telegram bot
- **📈 Real-time Monitoring**: Live dashboard για παρακολούθηση conditions
- **🔧 Strategy Optimization**: Hyperopt optimization με 600 epochs
- **💰 Risk Management**: Dry run mode με 3000 USDC virtual wallet
- **📊 Analytics Dashboard**: Real-time strategy condition monitoring

## 🛠️ Τεχνολογίες

- **FreqTrade**: Core trading engine
- **Python 3.11**: Backend development
- **Flask**: Web dashboard
- **Telegram Bot API**: Remote control
- **Binance API**: Exchange integration
- **SQLite**: Trade data storage

## 🚀 Γρήγορη Εκκίνηση

### Προαπαιτούμενα
```bash
# Python 3.11+
python3 --version

# FreqTrade installation
pip install freqtrade
```

### Εγκατάσταση
```bash
# Clone το repository
git clone <repository-url>
cd trade_bot_v1

# Εκκίνηση του bot
freqtrade trade --config user_data/config.json --strategy NFI5MOHO_WIP --dry-run

# Εκκίνηση dashboard
python3 apps/monitoring/strategy_monitor.py
```

## 📊 Dashboard URLs

- **Strategy Monitor**: http://localhost:8504
- **FreqTrade API**: http://localhost:8080
- **HTML Dashboard**: file:///.../nfi5moho_dashboard.html

## 🎯 Στρατηγική NFI5MOHO_WIP

### Buy Conditions (5/5 required):
- ✅ RSI Slow Declining
- ✅ RSI Fast < 35
- ✅ RSI > 24
- ✅ Price < SMA15 × 0.98
- ✅ CTI < 0.75

### Trading Pairs:
- BTC/USDC, ETH/USDC, BNB/USDC
- SOL/USDC, LINK/USDC, INJ/USDC
- OP/USDC, ARB/USDC, DOGE/USDC, PEPE/USDC

## 📱 Telegram Bot

### Διαθέσιμες Εντολές:
- `/start` - Εκκίνηση bot
- `/status` - Bot status
- `/trades` - Πρόσφατες συναλλαγές
- `/profit` - Κέρδη/ζημίες
- `/help` - Βοήθεια

## 🔧 Configuration

### Κύρια Ρυθμίσεις:
```json
{
  "max_open_trades": 3,
  "stake_currency": "USDC",
  "dry_run": true,
  "dry_run_wallet": 3000,
  "strategy": "NFI5MOHO_WIP"
}
```

## 📈 Performance

### Hyperopt Results:
- **Best Epoch**: 32/139
- **Win Rate**: 85.7% (12 wins, 2 losses)
- **Total Profit**: 14.38 USDC (2.88%)
- **Avg Profit per Trade**: 0.62%
- **Max Drawdown**: 0.89%

## 🛡️ Ασφάλεια

- **Dry Run Mode**: Προεπιλεγμένα ενεργό για ασφάλεια
- **API Authentication**: Προστασία με username/password
- **Telegram Authorization**: Περιορισμένη πρόσβαση
- **No Sensitive Data**: Κλειδιά API εκτός repository

## 📁 Δομή Project

```
trade_bot_v1/
├── apps/
│   ├── monitoring/          # Dashboards & monitoring
│   ├── telegram/           # Telegram bot integration
│   └── trading/            # Trading utilities
├── user_data/
│   ├── strategies/         # Trading strategies
│   ├── config.json        # Main configuration
│   └── logs/              # Log files
├── scripts/
│   ├── core/              # Core scripts
│   ├── monitoring/        # System monitoring
│   └── utilities/         # Helper scripts
└── docs/                  # Documentation
```

## 🔄 Scripts Launcher

```bash
# Εκτέλεση master launcher
./run_scripts.sh

# Ή απευθείας
python3 scripts/master_launcher.py
```

### Διαθέσιμες Κατηγορίες:
1. **🔧 Core** - Βασικά FreqTrade scripts
2. **📊 Monitoring** - Παρακολούθηση και έλεγχος
3. **📈 Optimization** - Βελτιστοποίηση και backtesting
4. **🛠️ Utilities** - Βοηθητικά scripts

## 📊 Live Monitoring

Το σύστημα παρέχει real-time monitoring με:
- **Condition Tracking**: Live έλεγχος buy/sell conditions
- **Performance Metrics**: Win rate, profit/loss tracking
- **Strategy Analysis**: Detailed condition breakdown
- **WebSocket Updates**: Real-time data streaming

## 🤝 Contributing

1. Fork το repository
2. Δημιούργησε feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit τις αλλαγές (`git commit -m 'Add AmazingFeature'`)
4. Push στο branch (`git push origin feature/AmazingFeature`)
5. Άνοιξε Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Contact

George Giailoglou - [@georgegiailoglou](https://github.com/georgegiailoglou)

Project Link: [https://github.com/georgegiailoglou/trade_bot_v1](https://github.com/georgegiailoglou/trade_bot_v1)

## ⚠️ Disclaimer

Αυτό το software είναι για εκπαιδευτικούς σκοπούς. Το trading κρυπτονομισμάτων ενέχει ρίσκο. Χρησιμοποιήστε το με δική σας ευθύνη και πάντα σε dry run mode μέχρι να είστε σίγουροι για τη στρατηγική σας.