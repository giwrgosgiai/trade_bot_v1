#!/bin/bash

echo "🚀 Ξεκινάω System Status Dashboard..."
echo "======================================"

# Έλεγχος αν το port 8503 είναι ελεύθερο
if lsof -Pi :8503 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8503 είναι ήδη σε χρήση"
    echo "🔍 Ελέγχω τι τρέχει στο port 8503..."
    lsof -i :8503
    echo ""
    echo "❓ Θέλετε να σταματήσω την υπάρχουσα διεργασία; (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "🛑 Σταματάω την υπάρχουσα διεργασία..."
        pkill -f "port=8503"
        sleep 2
    else
        echo "❌ Ακύρωση εκκίνησης"
        exit 1
    fi
fi

# Ενεργοποίηση virtual environment αν υπάρχει
if [ -d "myenv" ]; then
    echo "🐍 Ενεργοποιώ virtual environment..."
    source myenv/bin/activate
fi

# Έλεγχος αν υπάρχει το Python script
if [ ! -f "apps/monitoring/system_status_dashboard.py" ]; then
    echo "❌ Δεν βρέθηκε το αρχείο apps/monitoring/system_status_dashboard.py"
    exit 1
fi

echo "📊 Ξεκινάω το System Status Dashboard..."
echo "🌐 Διαθέσιμο στο: http://localhost:8503"
echo "🔍 Πατήστε Ctrl+C για τερματισμό"
echo ""

# Εκκίνηση του dashboard
cd "$(dirname "$0")"
python3 apps/monitoring/system_status_dashboard.py