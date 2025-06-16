# 🖥️ UI - Ενιαίος Φάκελος Διεπαφών Χρήστη

## 📁 Δομή Φακέλου

### 📊 `dashboards/` - Trading Dashboards (7 αρχεία)
Όλα τα dashboard και UI αρχεία για το trading σύστημα:

#### 🎯 Κύρια Dashboards
- **advanced_trading_ui.py** - Προηγμένο trading UI (17KB)
- **simple_trading_ui.py** - Απλό trading UI (12KB)
- **master_trading_dashboard.py** - Κεντρικό dashboard (17KB)
- **master_control_dashboard.py** - Control panel (21KB)
- **web_trades_dashboard.py** - Web trades monitor (18KB)

#### 🔧 Εξειδικευμένα
- **strategy_dashboard.py** - Strategy analysis (9.4KB)
- **start_dashboard.py** - Dashboard launcher (2KB)

### 🔌 `interfaces/` - Διεπαφές Συστήματος
Διεπαφές για integration με άλλα συστήματα (κενός προς το παρόν)

## 🚀 Χρήση Dashboards

### Advanced Trading UI
```bash
cd ui/dashboards/
python3 advanced_trading_ui.py
# Πρόσβαση: http://localhost:8001
```

### Simple Trading UI
```bash
cd ui/dashboards/
python3 simple_trading_ui.py
# Πρόσβαση: http://localhost:8000
```

### Master Trading Dashboard
```bash
cd ui/dashboards/
python3 master_trading_dashboard.py
# Πρόσβαση: http://localhost:5000
```

### Web Trades Dashboard
```bash
cd ui/dashboards/
python3 web_trades_dashboard.py
# Πρόσβαση: http://localhost:5001
```

### Master Control Dashboard
```bash
cd ui/dashboards/
streamlit run master_control_dashboard.py
# Πρόσβαση: http://localhost:8501
```

## 📋 Χαρακτηριστικά

### Advanced Trading UI
- 📊 Real-time trading data
- 📱 Telegram integration
- 🎯 Strategy analysis
- 📈 Performance metrics
- 🔔 Alert system

### Simple Trading UI
- 🎯 Βασικό interface
- 📊 Essential metrics
- 🚀 Fast loading
- 📱 Mobile friendly

### Master Trading Dashboard
- 🎛️ Central control
- 📊 Comprehensive stats
- 🔄 Auto-refresh
- 📈 Live charts

### Web Trades Dashboard
- 💹 Live trade monitoring
- 📊 Trade statistics
- 🎯 Performance tracking
- 📱 Responsive design

### Master Control Dashboard
- 🎛️ System control
- ⚙️ Configuration management
- 📊 System monitoring
- 🔧 Admin tools

## 🔗 Ports & Access

| Dashboard | Port | URL | Type |
|-----------|------|-----|------|
| Advanced Trading UI | 8001 | http://localhost:8001 | FastAPI |
| Simple Trading UI | 8000 | http://localhost:8000 | FastAPI |
| Master Trading | 5000 | http://localhost:5000 | Flask |
| Web Trades | 5001 | http://localhost:5001 | Flask |
| Master Control | 8501 | http://localhost:8501 | Streamlit |

## 📋 Σημειώσεις

- **Όλα τα UI** είναι πλέον σε έναν ενιαίο φάκελο
- **Εύκολη πρόσβαση** και διαχείριση
- **Διαφορετικά ports** για κάθε dashboard
- **Backward compatibility** με symlinks

## 🔧 Requirements

Βεβαιωθείτε ότι έχετε εγκαταστήσει:
```bash
pip install fastapi uvicorn flask streamlit
```

## 🚀 Quick Start

```bash
# Εκκίνηση όλων των dashboards
cd ui/dashboards/
./start_all_dashboards.sh
```