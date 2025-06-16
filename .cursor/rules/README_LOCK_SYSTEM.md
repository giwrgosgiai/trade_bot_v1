# 🔒 ΣΥΣΤΗΜΑ ΚΛΕΙΔΩΜΑΤΟΣ ΑΡΧΕΙΩΝ

## 📋 ΠΕΡΙΓΡΑΦΗ

Αυτό το σύστημα έχει σχεδιαστεί για να **ΑΠΟΤΡΕΠΕΙ ΑΠΟΛΥΤΑ** τη δημιουργία νέων αρχείων όταν υπάρχουν ήδη υφιστάμενα αρχεία που μπορούν να βελτιωθούν.

## 🎯 ΣΤΟΧΟΣ

- **ΔΙΑΤΗΡΗΣΗ** της δομής του project
- **ΑΠΟΦΥΓΗ** δημιουργίας περιττών αρχείων
- **ΒΕΛΤΙΩΣΗ** υπαρχόντων αρχείων αντί για δημιουργία νέων
- **ΚΑΘΑΡΗ** και οργανωμένη δομή φακέλων

## 🔐 ΕΠΙΠΕΔΑ ΑΣΦΑΛΕΙΑΣ

### 1. EMERGENCY_ABSOLUTE_LOCK.mdc
- **ΠΡΟΤΕΡΑΙΟΤΗΤΑ**: 9999 (Υψηλότερη)
- **ΣΚΟΠΟΣ**: Τελική ασφάλεια - Emergency protocol
- **ΕΝΕΡΓΟΠΟΙΗΣΗ**: Όταν όλα τα άλλα αποτύχουν

### 2. ULTIMATE_NO_NEW_FILES_LOCK.mdc
- **ΠΡΟΤΕΡΑΙΟΤΗΤΑ**: 1000
- **ΣΚΟΠΟΣ**: Υπερ-αυστηρός κανόνας με αλγόριθμο ελέγχου
- **ΧΑΡΑΚΤΗΡΙΣΤΙΚΑ**: Υποχρεωτικός αλγόριθμος πριν από κάθε ενέργεια

### 3. master_lock.mdc
- **ΣΚΟΠΟΣ**: Γενικός master κανόνας με κατηγοριοποίηση
- **ΧΑΡΑΚΤΗΡΙΣΤΙΚΑ**: Κλειδωμένες κατηγορίες αρχείων

### 4. strict_no_new_files.mdc
- **ΣΚΟΠΟΣ**: Αυστηρός κανόνας για συγκεκριμένες κατηγορίες
- **ΧΑΡΑΚΤΗΡΙΣΤΙΚΑ**: UI, Strategy, Telegram files

### 5. file_policy.mdc
- **ΣΚΟΠΟΣ**: Πολιτική τροποποίησης αρχείων
- **ΧΑΡΑΚΤΗΡΙΣΤΙΚΑ**: Συμπεριφορά και διαδικασίες

### 6. specific_files_lock.mdc
- **ΣΚΟΠΟΣ**: Κλείδωμα συγκεκριμένων αρχείων
- **ΧΑΡΑΚΤΗΡΙΣΤΙΚΑ**: Λίστα συγκεκριμένων αρχείων

## 🤖 ΑΛΓΟΡΙΘΜΟΣ AI

Κάθε φορά που το AI θέλει να κάνει κάτι, **ΠΡΕΠΕΙ** να ακολουθήσει αυτόν τον αλγόριθμο:

```python
def MANDATORY_ALGORITHM():
    # 1. ΑΝΑΖΗΤΗΣΗ υπαρχόντων αρχείων
    existing_files = search_for_existing_files()

    # 2. ΑΝ βρεθούν υπάρχοντα αρχεία
    if existing_files:
        selected_file = choose_best_file(existing_files)
        modify_existing_file(selected_file)
        return "SUCCESS"

    # 3. ΑΝ δεν βρεθούν αρχεία
    else:
        ask_user_which_file_to_modify()
        return "WAITING_FOR_USER"

    # 4. ΠΟΤΕ δημιουργία νέου αρχείου
    # create_new_file()  # ❌ ΑΠΑΓΟΡΕΥΕΤΑΙ
```

## 📋 ΥΠΑΡΧΟΝΤΑ ΑΡΧΕΙΑ ΓΙΑ ΤΡΟΠΟΠΟΙΗΣΗ

### 🎯 UI/Interface Files:
- `enhanced_trading_ui.py`
- `beautiful_scripts_ui.py`
- `live_trading_system.py`
- `beautiful_ui.sh`
- Αρχεία στο `ui/` directory

### 🎯 Strategy Files:
- Όλα στο `user_data/strategies/`
- Όλα στο `strategies/`
- Όλα στο `profitable_strategies/`

### 🎯 Telegram Files:
- Όλα στο `telegram/`
- Όλα στο `apps/telegram/`
- `telegram_*.sh` scripts

### 🎯 Trading Files:
- `live_trading_system.py`
- `trading_*.py` files
- `freqtrade_*.py` files

### 🎯 Monitoring Files:
- `*_monitor*.py` files
- `*_analyzer*.py` files
- `*_checker*.py` files

## ✅ ΕΠΙΤΡΕΠΟΜΕΝΕΣ ΕΝΕΡΓΕΙΕΣ

- **ΤΡΟΠΟΠΟΙΗΣΗ** υπαρχόντων αρχείων
- **ΒΕΛΤΙΩΣΗ** υπαρχόντων αρχείων
- **ΕΠΕΚΤΑΣΗ** υπαρχόντων αρχείων
- **ΔΙΟΡΘΩΣΗ** υπαρχόντων αρχείων
- **ΠΡΟΣΘΗΚΗ** νέων functions σε υπάρχοντα αρχεία

## ❌ ΑΠΑΓΟΡΕΥΜΕΝΕΣ ΕΝΕΡΓΕΙΕΣ

- **ΔΗΜΙΟΥΡΓΙΑ** νέων αρχείων
- **ΑΝΤΙΓΡΑΦΗ** αρχείων με νέα ονόματα
- **TEMPLATE** creation
- **BACKUP** creation
- **ALTERNATIVE** versions
- **DUPLICATE** files

## 🚨 ΜΗΝΥΜΑΤΑ ΣΦΑΛΜΑΤΟΣ

Αν το AI προσπαθήσει να δημιουργήσει νέο αρχείο:

```
🚨🚨🚨 EMERGENCY LOCK ACTIVATED 🚨🚨🚨

❌ ΚΡΙΣΙΜΟ ΣΦΑΛΜΑ: Προσπάθεια δημιουργίας νέου αρχείου!
🔒 ΚΛΕΙΔΩΜΕΝΟ ΣΥΣΤΗΜΑ: Δεν επιτρέπεται η δημιουργία νέων αρχείων!

🔍 ΑΝΑΖΗΤΗΣΗ ΥΠΑΡΧΟΝΤΩΝ ΑΡΧΕΙΩΝ...
📋 ΒΡΕΘΗΚΑΝ: [λίστα_υπαρχόντων_αρχείων]
🎯 ΠΡΟΤΕΙΝΟΜΕΝΟ: [επιλεγμένο_αρχείο_για_τροποποίηση]

✅ ΣΩΣΤΗ ΕΝΕΡΓΕΙΑ: Θα τροποποιήσω το υπάρχον αρχείο
❌ ΛΑΘΟΣ ΕΝΕΡΓΕΙΑ: Δημιουργία νέου αρχείου

🔒 ΚΛΕΙΔΩΜΕΝΟ - ΜΗ ΠΑΡΑΒΙΑΣΕΙΣ!
```

## 🔧 CONFIGURATION

Στο `.cursorrules` αρχείο:

```json
{
  "rules": [
    ".cursor/rules/EMERGENCY_ABSOLUTE_LOCK.mdc",
    ".cursor/rules/ULTIMATE_NO_NEW_FILES_LOCK.mdc",
    ".cursor/rules/master_lock.mdc",
    ".cursor/rules/strict_no_new_files.mdc",
    ".cursor/rules/file_policy.mdc",
    ".cursor/rules/specific_files_lock.mdc"
  ],
  "noNewFiles": true,
  "enforceExistingFileModification": true,
  "blockFileCreation": true,
  "mandatoryFileSearch": true,
  "ultimateFileLock": true
}
```

## 📞 ΣΕ ΠΕΡΙΠΤΩΣΗ ΠΡΟΒΛΗΜΑΤΟΣ

Αν το AI δεν ακολουθεί τους κανόνες:

1. **ΕΛΕΓΞΕ** αν όλοι οι κανόνες είναι ενεργοί
2. **ΕΠΙΒΕΒΑΙΩΣΕ** ότι το `.cursorrules` έχει τη σωστή σειρά
3. **ΡΩΤΑ** το AI να εξηγήσει γιατί θέλει να δημιουργήσει νέο αρχείο
4. **ΥΠΕΝΘΥΜΙΣΕ** τους κανόνες αν χρειάζεται

## 🎯 ΑΠΟΤΕΛΕΣΜΑΤΑ

Με αυτό το σύστημα:

- ✅ **ΚΑΘΑΡΗ** δομή project
- ✅ **ΟΡΓΑΝΩΜΕΝΑ** αρχεία
- ✅ **ΒΕΛΤΙΩΜΕΝΑ** υπάρχοντα αρχεία
- ✅ **ΑΠΟΦΥΓΗ** περιττών αρχείων
- ✅ **ΣΥΝΕΠΕΙΑ** στη δομή

## 🔒 ΤΕΛΙΚΗ ΣΗΜΕΙΩΣΗ

**ΑΥΤΟΙ ΟΙ ΚΑΝΟΝΕΣ ΕΙΝΑΙ ΑΠΟΛΥΤΟΙ ΚΑΙ ΜΗ ΠΑΡΑΒΙΑΣΙΜΟΙ!**

Κάθε AI που δουλεύει σε αυτό το project **ΠΡΕΠΕΙ** να τους ακολουθεί χωρίς εξαιρέσεις.