#!/bin/bash

# 🔍 Get Chat ID Script
# Βοηθά στην εύρεση του Chat ID μετά από μήνυμα στο bot

BOT_TOKEN="7295982134:AAF242CTc3vVc9m0qBT3wcF0wljByhlptMQ"

echo "🤖 Chat ID Finder"
echo "=================="
echo ""
echo "📱 ΟΔΗΓΙΕΣ:"
echo "1. Άνοιξε το Telegram"
echo "2. Βρες το bot: @GeorgeGnewbot"
echo "3. Στείλε οποιοδήποτε μήνυμα (π.χ. 'hello')"
echo "4. Πάτησε Enter εδώ για να βρω το Chat ID"
echo ""
read -p "Πάτησε Enter μετά που στείλεις μήνυμα στο bot..."

echo ""
echo "🔍 Αναζητώ το Chat ID..."

# Get updates from Telegram
response=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getUpdates")

# Extract chat ID using Python
chat_id=$(echo "$response" | python3 -c "
import json
import sys

try:
    data = json.load(sys.stdin)
    if data['ok'] and data['result']:
        # Get the latest message
        latest_message = data['result'][-1]
        chat_id = latest_message['message']['chat']['id']
        print(chat_id)
    else:
        print('NO_MESSAGES')
except Exception as e:
    print('ERROR')
")

if [ "$chat_id" = "NO_MESSAGES" ]; then
    echo "❌ Δεν βρέθηκαν μηνύματα!"
    echo "   Βεβαιώσου ότι έστειλες μήνυμα στο @GeorgeGnewbot"
    exit 1
elif [ "$chat_id" = "ERROR" ]; then
    echo "❌ Σφάλμα στην ανάλυση της απάντησης!"
    echo "   Raw response:"
    echo "$response"
    exit 1
else
    echo "✅ Chat ID βρέθηκε: $chat_id"

    # Update config file
    echo ""
    echo "🔧 Ενημερώνω το config file..."

    python3 -c "
import json

config_file = 'configs/telegram/telegram_config.json'

with open(config_file, 'r') as f:
    config = json.load(f)

config['chat_id'] = '$chat_id'

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print('✅ Config file ενημερώθηκε!')
"

    # Test the bot
    echo ""
    echo "🧪 Δοκιμάζω το bot..."

    test_response=$(curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
        -d "chat_id=$chat_id" \
        -d "text=🎉 Το Telegram Bot είναι έτοιμο! Chat ID: $chat_id" \
        -d "parse_mode=HTML")

    if echo "$test_response" | grep -q '"ok":true'; then
        echo "✅ Δοκιμαστικό μήνυμα στάλθηκε επιτυχώς!"
        echo "✅ Το Telegram Bot είναι πλήρως ρυθμισμένο!"
        echo ""
        echo "🎯 Μπορείς τώρα να χρησιμοποιήσεις:"
        echo "• ./telegram_alerts_manager.sh"
        echo "• ./telegram_scheduler.sh"
        echo "• ./telegram_trading_bot.sh"
        echo "• ./test_telegram.sh (για έλεγχο)"
    else
        echo "❌ Αποτυχία αποστολής δοκιμαστικού μηνύματος"
        echo "Response: $test_response"
    fi
fi