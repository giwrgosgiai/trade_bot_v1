# Trading Strategies Directory

## 📍 Σημαντική Σημείωση
Αυτός είναι ο **ΚΥΡΙΟΣ** φάκελος στρατηγικών που χρησιμοποιεί το σύστημα!

Το freqtrade configuration δείχνει εδώ: `"strategy_path": "../user_data/strategies/"`

## 🎯 Διαθέσιμες Στρατηγικές

### 1. NFI5MOHO_WIP
- **Αρχείο**: `NFI5MOHO_WIP.py`
- **Config**: `NFI5MOHO_WIP.json`
- **Τύπος**: Advanced multi-indicator strategy
- **Timeframe**: 15m (κύριο)
- **Status**: Ενεργή στο σύστημα

### 2. NeverMissATrend
- **Αρχείο**: `NeverMissATrend.py`
- **Config**: `NeverMissATrend.json`
- **Τύπος**: Linear regression trend following
- **Timeframe**: 1d (βέλτιστο)
- **Status**: Νέα προσθήκη - έτοιμη για testing
- **Performance**: 26.3% profit, Sharpe 1.8 (1d timeframe)

## 📊 Αποτελέσματα Backtesting

### NeverMissATrend Results
- **Φάκελος**: `nevermissatrend_results/`
- **Περιεχόμενα**:
  - CSV αποτελέσματα
  - HTML reports
  - Performance charts
  - Strategy league table

## 🔄 Συγχρονισμός
- **Κύριος φάκελος**: `/user_data/strategies/` (αυτός)
- **Backup φάκελος**: `/freqtrade/user_data/strategies/` (legacy)
- **Σύσταση**: Χρησιμοποιείτε πάντα τον κύριο φάκελο

## 🚀 Χρήση
```bash
# Backtesting
freqtrade backtesting -s NeverMissATrend -c user_data/config.json --timeframe=1d

# Live trading
freqtrade trade -s NFI5MOHO_WIP -c user_data/config.json

# Hyperopt
freqtrade hyperopt -s NeverMissATrend -c user_data/config.json --epochs 50
```

## 📈 Συστάσεις
1. **NFI5MOHO**: Χρήση για 15m timeframe, πολλαπλά pairs
2. **NeverMissATrend**: Χρήση για 1d timeframe, trending markets
3. **Παράλληλη λειτουργία**: Δυνατή με διαφορετικά configurations