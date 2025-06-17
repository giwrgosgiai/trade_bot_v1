#!/bin/bash

# 🚀 Quick Deployment Script
# Γρήγορη αντιγραφή στον server με rsync

# Χρώματα
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🚀 Quick Deploy to Server${NC}"
echo "=========================="

# Ρυθμίσεις - ΑΛΛΑΞΕ ΑΥΤΕΣ ΤΙΣ ΤΙΜΕΣ
SERVER_USER="your_username"
SERVER_IP="192.168.1.100"  # ή το domain name
SERVER_PATH="/home/your_username/trade_bot_v1"

echo -e "${YELLOW}📋 Current Settings:${NC}"
echo "Server: $SERVER_USER@$SERVER_IP"
echo "Path: $SERVER_PATH"
echo ""

read -p "Θέλεις να συνεχίσεις με αυτές τις ρυθμίσεις; (y/n): " confirm

if [[ $confirm != [yY] ]]; then
    echo -e "${RED}❌ Deployment cancelled${NC}"
    echo ""
    echo -e "${YELLOW}💡 Για να αλλάξεις τις ρυθμίσεις, επεξεργάσου το αρχείο:${NC}"
    echo "nano quick_deploy.sh"
    exit 1
fi

echo -e "${GREEN}📦 Starting deployment...${NC}"

# Rsync command με εξαιρέσεις
rsync -avz --progress \
    --exclude='logs/' \
    --exclude='*.log' \
    --exclude='__pycache__/' \
    --exclude='.git/' \
    --exclude='*.sqlite' \
    --exclude='backups/' \
    --exclude='*.pyc' \
    --exclude='freqtrade/logs/' \
    --exclude='user_data/logs/' \
    --exclude='data/databases/' \
    --exclude='.DS_Store' \
    --exclude='*.egg-info/' \
    . $SERVER_USER@$SERVER_IP:$SERVER_PATH/

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo ""
    echo -e "${CYAN}🔧 Next Steps:${NC}"
    echo "1. Connect to server: ssh $SERVER_USER@$SERVER_IP"
    echo "2. Go to project: cd $SERVER_PATH"
    echo "3. Install deps: pip install -r requirements.txt"
    echo "4. Configure: cp config-private.json.example user_data/config.json"
    echo "5. Run bot: freqtrade trade --config user_data/config.json --strategy YourStrategy"
else
    echo -e "${RED}❌ Deployment failed!${NC}"
    echo ""
    echo -e "${YELLOW}💡 Possible issues:${NC}"
    echo "• Check SSH connection: ssh $SERVER_USER@$SERVER_IP"
    echo "• Verify server path exists: mkdir -p $SERVER_PATH"
    echo "• Check SSH keys are set up"
fi