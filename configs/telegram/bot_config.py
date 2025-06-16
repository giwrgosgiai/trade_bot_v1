# Telegram Bot Configuration
# Αντικαταστήστε τις παρακάτω τιμές με τις δικές σας

# Bot Token από το @BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Telegram User IDs που επιτρέπεται να χρησιμοποιούν το bot
# Για να μάθετε το User ID σας, στείλτε /start στο @userinfobot
ALLOWED_USERS = [
    123456789,  # Αντικαταστήστε με το δικό σας User ID
    # 987654321,  # Προσθέστε περισσότερα User IDs αν χρειάζεται
]

# Dashboard Configuration
DASHBOARD_URL = "http://localhost:8503"
DASHBOARD_PORT = 8503

# System Paths
DASHBOARD_SCRIPT_PATH = "apps/monitoring/system_status_dashboard.py"
WORKING_DIRECTORY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Bot Settings
BOT_NAME = "System Dashboard Control Bot"
BOT_DESCRIPTION = "Έλεγχος και διαχείριση System Status Dashboard"

# Timeouts (σε δευτερόλεπτα)
API_TIMEOUT = 10
RESTART_DELAY = 3