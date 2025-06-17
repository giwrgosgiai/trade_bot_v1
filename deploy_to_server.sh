#!/bin/bash

# 🚀 FreqTrade Project Deployment Script
# Αντιγραφή του project σε απομακρυσμένο server

echo "🚀 FreqTrade Project Deployment"
echo "================================="

# Χρώματα για καλύτερη εμφάνιση
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Ρυθμίσεις
PROJECT_DIR="/Users/georgegiailoglou/Documents/GitHub/trade_bot_v1"
EXCLUDE_FILES="--exclude='logs/' --exclude='*.log' --exclude='__pycache__/' --exclude='.git/' --exclude='*.sqlite' --exclude='backups/' --exclude='*.pyc' --exclude='freqtrade/logs/' --exclude='user_data/logs/' --exclude='data/databases/' --exclude='.DS_Store'"

echo -e "${CYAN}📋 Επιλογές Deployment:${NC}"
echo "1. rsync - Συγχρονισμός (προτεινόμενο)"
echo "2. scp - Απλή αντιγραφή"
echo "3. tar + scp - Συμπίεση και αντιγραφή"
echo "4. Git clone - Μέσω repository"
echo ""

read -p "Επίλεξε μέθοδο (1-4): " method

case $method in
    1)
        echo -e "${GREEN}📦 Χρήση rsync${NC}"
        echo ""
        echo -e "${YELLOW}Παράδειγμα εντολής:${NC}"
        echo "rsync -avz --progress $EXCLUDE_FILES . username@server_ip:/path/to/destination/"
        echo ""
        echo -e "${BLUE}Συγκεκριμένα παραδείγματα:${NC}"
        echo "# Για local network:"
        echo "rsync -avz --progress $EXCLUDE_FILES . pi@192.168.1.100:/home/pi/trade_bot/"
        echo ""
        echo "# Για remote server:"
        echo "rsync -avz --progress $EXCLUDE_FILES . user@example.com:/opt/trade_bot/"
        echo ""
        echo -e "${CYAN}Πλεονεκτήματα rsync:${NC}"
        echo "✅ Συγχρονίζει μόνο τα αλλαγμένα αρχεία"
        echo "✅ Γρήγορο για επόμενες ενημερώσεις"
        echo "✅ Διατηρεί permissions"
        echo "✅ Progress bar"
        ;;

    2)
        echo -e "${GREEN}📦 Χρήση scp${NC}"
        echo ""
        echo -e "${YELLOW}Παράδειγμα εντολής:${NC}"
        echo "scp -r . username@server_ip:/path/to/destination/"
        echo ""
        echo -e "${BLUE}Συγκεκριμένα παραδείγματα:${NC}"
        echo "# Για local network:"
        echo "scp -r . pi@192.168.1.100:/home/pi/trade_bot/"
        echo ""
        echo "# Για remote server:"
        echo "scp -r . user@example.com:/opt/trade_bot/"
        echo ""
        echo -e "${RED}⚠️ Προσοχή:${NC} Το scp αντιγράφει όλα τα αρχεία κάθε φορά"
        ;;

    3)
        echo -e "${GREEN}📦 Χρήση tar + scp${NC}"
        echo ""
        echo -e "${YELLOW}Βήματα:${NC}"
        echo "1. Δημιουργία archive:"
        echo "   tar --exclude='logs' --exclude='*.log' --exclude='__pycache__' --exclude='.git' --exclude='*.sqlite' --exclude='backups' -czf trade_bot_v1.tar.gz ."
        echo ""
        echo "2. Αντιγραφή στον server:"
        echo "   scp trade_bot_v1.tar.gz username@server_ip:/path/to/destination/"
        echo ""
        echo "3. Αποσυμπίεση στον server:"
        echo "   ssh username@server_ip 'cd /path/to/destination && tar -xzf trade_bot_v1.tar.gz'"
        echo ""
        echo -e "${CYAN}Πλεονεκτήματα:${NC}"
        echo "✅ Μικρότερο μέγεθος αρχείου"
        echo "✅ Μία μόνο μεταφορά"
        echo "✅ Καλό για αργές συνδέσεις"
        ;;

    4)
        echo -e "${GREEN}📦 Χρήση Git${NC}"
        echo ""
        echo -e "${YELLOW}Προαπαιτούμενα:${NC}"
        echo "• Το project πρέπει να είναι σε Git repository"
        echo "• Ο server πρέπει να έχει πρόσβαση στο repository"
        echo ""
        echo -e "${BLUE}Εντολές στον server:${NC}"
        echo "git clone https://github.com/yourusername/trade_bot_v1.git"
        echo "# ή"
        echo "git clone git@github.com:yourusername/trade_bot_v1.git"
        echo ""
        echo -e "${CYAN}Για ενημερώσεις:${NC}"
        echo "cd trade_bot_v1"
        echo "git pull origin main"
        ;;

    *)
        echo -e "${RED}❌ Μη έγκυρη επιλογή${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${CYAN}🔧 Μετά την αντιγραφή στον server:${NC}"
echo "=================================="
echo "1. Σύνδεση στον server:"
echo "   ssh username@server_ip"
echo ""
echo "2. Μετάβαση στον φάκελο:"
echo "   cd /path/to/trade_bot_v1"
echo ""
echo "3. Εγκατάσταση dependencies:"
echo "   pip install -r requirements.txt"
echo "   # ή"
echo "   pip install -e ."
echo ""
echo "4. Ρύθμιση configuration:"
echo "   cp config-private.json.example user_data/config.json"
echo "   nano user_data/config.json"
echo ""
echo "5. Έναρξη bot:"
echo "   freqtrade trade --config user_data/config.json --strategy YourStrategy"

echo ""
echo -e "${GREEN}✅ Deployment Guide Completed!${NC}"
echo ""
echo -e "${YELLOW}💡 Συμβουλές:${NC}"
echo "• Χρησιμοποίησε SSH keys για ασφαλή σύνδεση"
echo "• Κάνε backup πριν από κάθε deployment"
echo "• Δοκίμασε πρώτα σε test environment"
echo "• Χρησιμοποίησε screen/tmux για να τρέχει το bot στο background"