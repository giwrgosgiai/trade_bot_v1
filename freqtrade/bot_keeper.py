#!/usr/bin/env python3
"""
🤖 FreqTrade Bot Keeper - Robust Auto-Restart System
Κρατάει τα bots πάντα ζωντανά με αυτόματο restart
"""

import subprocess
import time
import requests
import logging
import os
import signal
import sys
from datetime import datetime
from requests.auth import HTTPBasicAuth

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot_keeper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BotKeeper:
    def __init__(self):
        self.bots = [
            {
                'name': 'AI_Learning_Bot',
                'port': 8080,
                'config': 'user_data/config.json',
                'strategy': 'AILearningDayTradingStrategy',
                'process': None,
                'last_restart': None,
                'restart_count': 0
            },
            {
                'name': 'Altcoin_Profit_Bot',
                'port': 8081,
                'config': 'user_data/altcoin_config.json',
                'strategy': 'UltimateProfitAltcoinStrategy',
                'process': None,
                'last_restart': None,
                'restart_count': 0
            },
            {
                'name': 'Scalping_Bot',
                'port': 8082,
                'config': 'user_data/scalping_config.json',
                'strategy': 'UltraFastScalpingStrategy',
                'process': None,
                'last_restart': None,
                'restart_count': 0
            }
        ]

        self.auth = HTTPBasicAuth("freqtrade", "ruriu7AY")
        self.running = True

        # Handle shutdown gracefully
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def is_bot_healthy(self, bot):
        """Check if bot is responding to API calls"""
        try:
            response = requests.get(
                f"http://localhost:{bot['port']}/api/v1/ping",
                auth=self.auth,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    def start_bot(self, bot):
        """Start a FreqTrade bot"""
        try:
            # Kill any existing process
            if bot['process'] and bot['process'].poll() is None:
                bot['process'].terminate()
                time.sleep(2)
                if bot['process'].poll() is None:
                    bot['process'].kill()

            # Start new process
            cmd = [
                'python3', '-m', 'freqtrade', 'trade',
                '--config', bot['config'],
                '--strategy', bot['strategy'],
                '--dry-run'
            ]

            log_file = f"logs/{bot['name'].lower()}.log"

            with open(log_file, 'a') as f:
                bot['process'] = subprocess.Popen(
                    cmd,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    cwd='/home/giwrgosgiai/freqtrade'
                )

            bot['last_restart'] = datetime.now()
            bot['restart_count'] += 1

            logger.info(f"🚀 Started {bot['name']} (PID: {bot['process'].pid})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start {bot['name']}: {e}")
            return False

    def monitor_bot(self, bot):
        """Monitor a single bot and restart if needed"""
        # Check if process is still running
        if not bot['process'] or bot['process'].poll() is not None:
            logger.warning(f"⚠️ {bot['name']} process died, restarting...")
            return self.start_bot(bot)

        # Check if bot is responding to API
        if not self.is_bot_healthy(bot):
            logger.warning(f"⚠️ {bot['name']} not responding to API, restarting...")
            return self.start_bot(bot)

        return True

    def cleanup_old_processes(self):
        """Kill any orphaned FreqTrade processes"""
        try:
            result = subprocess.run(['pgrep', '-f', 'freqtrade'], capture_output=True, text=True)
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        try:
                            # Check if it's one of our managed processes
                            is_managed = any(
                                bot['process'] and str(bot['process'].pid) == pid
                                for bot in self.bots
                            )
                            if not is_managed:
                                logger.info(f"🧹 Killing orphaned process {pid}")
                                os.kill(int(pid), signal.SIGTERM)
                        except:
                            pass
        except:
            pass

    def get_status(self):
        """Get status of all bots"""
        status = []
        for bot in self.bots:
            is_running = bot['process'] and bot['process'].poll() is None
            is_healthy = self.is_bot_healthy(bot) if is_running else False

            status.append({
                'name': bot['name'],
                'port': bot['port'],
                'running': is_running,
                'healthy': is_healthy,
                'restart_count': bot['restart_count'],
                'last_restart': bot['last_restart']
            })
        return status

    def print_status(self):
        """Print current status of all bots"""
        print("\n" + "="*60)
        print(f"🤖 Bot Keeper Status - {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)

        for bot_status in self.get_status():
            status_icon = "✅" if bot_status['healthy'] else "❌"
            print(f"{status_icon} {bot_status['name']:<20} Port:{bot_status['port']} "
                  f"Restarts:{bot_status['restart_count']}")
        print("="*60)

    def run(self):
        """Main monitoring loop"""
        logger.info("🚀 Bot Keeper starting...")

        # Initial cleanup
        self.cleanup_old_processes()
        time.sleep(2)

        # Start all bots
        for bot in self.bots:
            self.start_bot(bot)
            time.sleep(5)  # Stagger startup

        # Monitoring loop
        check_count = 0
        while self.running:
            try:
                # Monitor each bot
                for bot in self.bots:
                    self.monitor_bot(bot)

                # Print status every 10 checks (5 minutes)
                check_count += 1
                if check_count % 10 == 0:
                    self.print_status()

                # Wait before next check
                time.sleep(30)  # Check every 30 seconds

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                time.sleep(10)

    def shutdown(self, signum=None, frame=None):
        """Graceful shutdown"""
        logger.info("🛑 Bot Keeper shutting down...")
        self.running = False

        for bot in self.bots:
            if bot['process'] and bot['process'].poll() is None:
                logger.info(f"🛑 Stopping {bot['name']}...")
                bot['process'].terminate()
                time.sleep(2)
                if bot['process'].poll() is None:
                    bot['process'].kill()

        sys.exit(0)

if __name__ == "__main__":
    # Create logs directory
    os.makedirs('logs', exist_ok=True)

    # Start bot keeper
    keeper = BotKeeper()
    keeper.run()