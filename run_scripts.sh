#!/bin/bash

# 🚀 Quick Script Launcher
# Γρήγορη πρόσβαση στο Master Script Launcher

echo "🚀 FreqTrade Scripts Launcher"
echo "============================="

# Έλεγχος αν υπάρχει ο φάκελος scripts
if [ ! -d "scripts" ]; then
    echo "❌ Ο φάκελος scripts δεν βρέθηκε!"
    echo "Παρακαλώ εκτελέστε από το root directory του project."
    exit 1
fi

# Εκτέλεση του master launcher
python3 scripts/master_launcher.py