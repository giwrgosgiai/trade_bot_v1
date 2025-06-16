# NFI5MOHO Hyperopt Setup

Αυτό το setup σου επιτρέπει να τρέξεις hyperopt για την στρατηγική NFI5MOHO_WIP με 1000 epochs και automatic early stopping μετά από 20 συνεχόμενα epochs χωρίς βελτίωση.

## 📁 Αρχεία που δημιουργήθηκαν

- `configs/hyperopt_config.json` - Configuration για το hyperopt
- `scripts/run_hyperopt_nfi5moho.py` - Python script που τρέχει το hyperopt με early stopping
- `scripts/download_data_for_hyperopt.py` - Script για κατέβασμα δεδομένων
- `run_hyperopt_nfi5moho.sh` - Bash script για εύκολη εκτέλεση
- `HYPEROPT_README.md` - Αυτό το αρχείο

## 🚀 Πώς να τρέξεις το Hyperopt

### Βήμα 1: Κατέβασμα δεδομένων (αν χρειάζεται)
```bash
python3 scripts/download_data_for_hyperopt.py
```

### Βήμα 2: Εκτέλεση Hyperopt
```bash
./run_hyperopt_nfi5moho.sh
```

Ή απευθείας:
```bash
python3 scripts/run_hyperopt_nfi5moho.py
```

## ⚙️ Παράμετροι Hyperopt

- **Strategy**: NFI5MOHO_WIP
- **Max Epochs**: 1000
- **Early Stopping**: 20 συνεχόμενα epochs χωρίς βελτίωση
- **Spaces**: buy, sell
- **Loss Function**: SharpeHyperOptLoss
- **Time Range**: 20230601-20240301
- **Timeframe**: 5m (με 1h informative)

## 📊 Pairs που χρησιμοποιούνται

- BTC/USDC
- ETH/USDC
- ADA/USDC
- DOT/USDC
- SOL/USDC
- MATIC/USDC
- LINK/USDC
- AVAX/USDC
- UNI/USDC

## 📈 Παρακολούθηση προόδου

Το script τρέχει σε batches των 50 epochs και ελέγχει για early stopping μετά από κάθε batch.

Θα δεις μηνύματα όπως:
- ✅ New best result found: 0.123456 (previous: 0.098765)
- ⏳ No improvement for 5 epochs (best: 0.123456)
- 🛑 Early stopping triggered after 20 epochs without improvement

## 📁 Αποτελέσματα

Τα αποτελέσματα αποθηκεύονται σε:
- **Database**: `user_data/hyperopt_nfi5moho.sqlite`
- **Logs**: `logs/hyperopt_nfi5moho.log`

## 🔍 Ανάλυση αποτελεσμάτων

Μετά το hyperopt, μπορείς να δεις τα αποτελέσματα με:

```bash
cd freqtrade
python -m freqtrade hyperopt-show --config ../configs/hyperopt_config.json --best
```

Ή για να δεις όλα τα αποτελέσματα:
```bash
cd freqtrade
python -m freqtrade hyperopt-list --config ../configs/hyperopt_config.json --profitable
```

## 🛠️ Προσαρμογές

Αν θέλεις να αλλάξεις παραμέτρους, επεξεργάσου το `scripts/run_hyperopt_nfi5moho.py`:

- `self.max_epochs = 1000` - Μέγιστος αριθμός epochs
- `self.early_stop_patience = 20` - Epochs χωρίς βελτίωση πριν σταματήσει
- `batch_size = 50` - Μέγεθος batch για έλεγχο early stopping

## ⚠️ Σημαντικές σημειώσεις

1. Το hyperopt μπορεί να διαρκέσει αρκετές ώρες ή ημέρες
2. Βεβαιώσου ότι έχεις αρκετό χώρο στο δίσκο για τα δεδομένα
3. Το early stopping θα σταματήσει το hyperopt αν δεν βρει καλύτερα αποτελέσματα για 20 συνεχόμενα epochs
4. Τα αποτελέσματα αποθηκεύονται αυτόματα στη βάση δεδομένων

## 🎯 Τι κάνει το Early Stopping

Το script ελέγχει μετά από κάθε batch αν το καλύτερο αποτέλεσμα έχει βελτιωθεί. Αν δεν έχει βελτιωθεί για 20 συνεχόμενα epochs, σταματάει αυτόματα για να εξοικονομήσει χρόνο.

Αυτό είναι χρήσιμο γιατί:
- Εξοικονομεί χρόνο υπολογισμού
- Αποφεύγει το overfitting
- Σταματάει όταν δεν υπάρχει περαιτέρω βελτίωση