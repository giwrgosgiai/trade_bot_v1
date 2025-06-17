#!/bin/bash

# 🚀 Git-Based Deployment Script
# Deployment μέσω GitHub repository

# Χρώματα
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🚀 Git Deployment for trade_bot_v1${NC}"
echo "===================================="
echo ""

# Repository URL
REPO_URL="https://github.com/giwrgosgiai/trade_bot_v1.git"

echo -e "${BLUE}📋 Repository: ${REPO_URL}${NC}"
echo ""

# Check git status
echo -e "${YELLOW}🔍 Checking git status...${NC}"
git status --porcelain

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Git repository error${NC}"
    exit 1
fi

# Check for uncommitted changes
UNCOMMITTED=$(git status --porcelain | wc -l)
if [ $UNCOMMITTED -gt 0 ]; then
    echo -e "${YELLOW}⚠️ You have uncommitted changes:${NC}"
    git status --short
    echo ""
    read -p "Do you want to commit and push these changes? (y/n): " commit_changes

    if [[ $commit_changes == [yY] ]]; then
        echo -e "${GREEN}📝 Adding and committing changes...${NC}"
        git add .
        read -p "Enter commit message (or press Enter for default): " commit_msg
        if [ -z "$commit_msg" ]; then
            commit_msg="Update project for deployment $(date '+%Y-%m-%d %H:%M')"
        fi
        git commit -m "$commit_msg"

        echo -e "${GREEN}📤 Pushing to GitHub...${NC}"
        git push origin main

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Successfully pushed to GitHub${NC}"
        else
            echo -e "${RED}❌ Failed to push to GitHub${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠️ Continuing with current committed state${NC}"
    fi
fi

# Check if we're ahead of origin
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
if [ $AHEAD -gt 0 ]; then
    echo -e "${YELLOW}⚠️ Your local branch is $AHEAD commits ahead of origin${NC}"
    read -p "Push to GitHub? (y/n): " push_changes

    if [[ $push_changes == [yY] ]]; then
        echo -e "${GREEN}📤 Pushing to GitHub...${NC}"
        git push origin main

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Successfully pushed to GitHub${NC}"
        else
            echo -e "${RED}❌ Failed to push to GitHub${NC}"
            exit 1
        fi
    fi
fi

echo ""
echo -e "${GREEN}✅ Repository is ready for deployment!${NC}"
echo ""

# Server deployment instructions
echo -e "${CYAN}🖥️ Server Deployment Instructions:${NC}"
echo "====================================="
echo ""
echo -e "${YELLOW}1. Connect to your server:${NC}"
echo "   ssh username@your-server-ip"
echo ""
echo -e "${YELLOW}2. Clone the repository (first time only):${NC}"
echo "   git clone $REPO_URL"
echo "   cd trade_bot_v1"
echo ""
echo -e "${YELLOW}3. For updates (subsequent deployments):${NC}"
echo "   cd trade_bot_v1"
echo "   git pull origin main"
echo ""
echo -e "${YELLOW}4. Install/Update dependencies:${NC}"
echo "   pip install -r requirements.txt"
echo "   # or"
echo "   pip install -e ."
echo ""
echo -e "${YELLOW}5. Configure the bot:${NC}"
echo "   cp config-private.json.example user_data/config.json"
echo "   nano user_data/config.json"
echo "   # Add your API keys and settings"
echo ""
echo -e "${YELLOW}6. Test the setup:${NC}"
echo "   freqtrade --version"
echo "   freqtrade list-strategies"
echo ""
echo -e "${YELLOW}7. Run the bot:${NC}"
echo "   # Dry run first"
echo "   freqtrade trade --config user_data/config.json --strategy NFI5MOHO_WIP --dry-run"
echo ""
echo "   # Live trading (when ready)"
echo "   freqtrade trade --config user_data/config.json --strategy NFI5MOHO_WIP"
echo ""
echo -e "${YELLOW}8. Run in background (optional):${NC}"
echo "   # Using screen"
echo "   screen -S freqtrade"
echo "   freqtrade trade --config user_data/config.json --strategy NFI5MOHO_WIP"
echo "   # Press Ctrl+A, then D to detach"
echo ""
echo "   # Using nohup"
echo "   nohup freqtrade trade --config user_data/config.json --strategy NFI5MOHO_WIP > freqtrade.log 2>&1 &"
echo ""

# One-liner for server
echo -e "${CYAN}📋 One-liner for server (copy-paste):${NC}"
echo "======================================"
echo ""
echo -e "${GREEN}# First time setup:${NC}"
echo "git clone $REPO_URL && cd trade_bot_v1 && pip install -e . && cp config-private.json.example user_data/config.json"
echo ""
echo -e "${GREEN}# For updates:${NC}"
echo "cd trade_bot_v1 && git pull origin main && pip install -e ."
echo ""

# Security reminder
echo -e "${RED}🔒 Security Reminder:${NC}"
echo "===================="
echo "• Never commit API keys or sensitive data to GitHub"
echo "• Use environment variables or config files that are in .gitignore"
echo "• The config-private.json.example is safe - it's just a template"
echo "• Always configure your real settings in user_data/config.json on the server"
echo ""

echo -e "${GREEN}🎉 Git deployment ready!${NC}"
echo "Your project is now available at: $REPO_URL"