#!/usr/bin/env python3
"""
Auto Downloader for Trading Data (Freqtrade format)
Διαβάζει pairs από το config_backtest.json και κατεβάζει όλα τα timeframes.
Υποστηρίζει resume, retry, logging, και daemon mode (συνεχή λειτουργία).
"""
import os
import json
import time
from datetime import datetime, timedelta
import requests
from pathlib import Path
from tqdm import tqdm
import logging
import argparse
import threading

# --- CONFIG ---
CONFIG_PATH = 'config_backtest.json'
DATA_DIR = 'user_data/data/binance'
TIMEFRAMES = ['5m', '15m', '30m', '1h', '4h', '1d']
API_URL = 'https://api.binance.com/api/v3/klines'
LOG_FILE = 'auto_download_binance_candles.log'
RETRY_LIMIT = 5
RETRY_WAIT = 10  # seconds
SCHEDULE_MINUTES = 60  # κάθε πόσα λεπτά να τρέχει σε daemon mode

TELEGRAM_TOKEN = "7295982134:AAF242CTc3vVc9m0qBT3wcF0wljByhlptMQ"
# User: George Adam, Id: 930268785, Username: @GeorgeeAdams, Lang: el
TELEGRAM_CHAT_ID = 930268785

OFFSET_FILE = "telegram_offset.txt"

# --- LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- HELPERS ---
def load_pairs_from_config(config_path: str):
    with open(config_path, 'r') as f:
        config = json.load(f)
    pairs = config['exchange']['pair_whitelist']
    return pairs

def timeframe_to_api(tf: str) -> str:
    return tf.replace('m', 'm').replace('h', 'h').replace('d', 'd')

def freqtrade_pair(pair: str) -> str:
    return pair.replace('/', '_')

def get_last_candle_time(filepath: str) -> int:
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        if not data:
            return None
        last = data[-1][0]  # Binance: [open_time, open, high, low, close, volume, ...]
        return last
    except Exception as e:
        logger.warning(f"Could not read {filepath}: {e}")
        return None

def fetch_klines(symbol: str, interval: str, start_time: int, end_time: int, limit=1000):
    url = API_URL
    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': start_time,
        'endTime': end_time,
        'limit': limit
    }
    for attempt in range(RETRY_LIMIT):
        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.warning(f"  ⚠️  Error fetching {symbol} {interval} (attempt {attempt+1}): {e}")
            time.sleep(RETRY_WAIT)
    logger.error(f"  ❌ Failed to fetch {symbol} {interval} after {RETRY_LIMIT} attempts.")
    return []

def save_freqtrade_json(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f)

def format_symbol(pair: str) -> str:
    return pair.replace('/', '')

def ms_since_epoch(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)

def send_telegram_message(message: str):
    # Remove any external references and links from message
    cleaned_message = message.replace("binance", "exchange").replace("Binance", "Exchange")
    # Remove any URLs or links
    import re
    cleaned_message = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', cleaned_message)

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": cleaned_message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code == 200:
            logger.info("Telegram notification sent.")
        else:
            logger.warning(f"Telegram error: {resp.text}")
    except Exception as e:
        logger.warning(f"Telegram send error: {e}")

def download_all_pairs(pairs, timeframes, data_dir, days_back=730):
    now = datetime.utcnow()
    start_dt = now - timedelta(days=days_back)
    start_time = ms_since_epoch(start_dt)
    end_time = ms_since_epoch(now)
    logger.info(f"Pairs: {pairs}")
    logger.info(f"Timeframes: {timeframes}")
    logger.info(f"Κατέβασμα δεδομένων από {start_dt.date()} έως {now.date()}")

    summary = []
    for pair in pairs:
        symbol = format_symbol(pair)
        for tf in timeframes:
            interval = timeframe_to_api(tf)
            out_path = os.path.join(data_dir, f"{freqtrade_pair(pair)}-{tf}.json")
            logger.info(f"➡️  {pair} {tf} -> {out_path}")
            last_candle = get_last_candle_time(out_path)
            fetch_start = last_candle + 1 if last_candle else start_time
            all_candles = []
            if last_candle:
                with open(out_path, 'r') as f:
                    all_candles = json.load(f)
            pbar = tqdm(total=(end_time - fetch_start)//(60*1000), desc=f"{pair} {tf}")
            success = False
            try:
                while fetch_start < end_time:
                    if 'm' in tf:
                        step = 1000 * 60 * int(tf.replace('m',''))
                    elif 'h' in tf:
                        step = 1000 * 60 * 60 * int(tf.replace('h',''))
                    elif 'd' in tf:
                        step = 1000 * 60 * 60 * 24 * int(tf.replace('d',''))
                    else:
                        step = 1000 * 60 * 5
                    fetch_end = min(fetch_start + step * 1000, end_time)
                    candles = fetch_klines(symbol, interval, fetch_start, fetch_end)
                    if not candles:
                        break
                    if all_candles and candles[0][0] <= all_candles[-1][0]:
                        candles = [c for c in candles if c[0] > all_candles[-1][0]]
                    if not candles:
                        break
                    all_candles.extend(candles)
                    fetch_start = candles[-1][0] + 1
                    pbar.update(len(candles))
                    time.sleep(0.2)
                pbar.close()
                if all_candles:
                    save_freqtrade_json(all_candles, out_path)
                    logger.info(f"  ✅ Αποθηκεύτηκαν {len(all_candles)} candles.")
                    success = True
                else:
                    logger.warning(f"  ❌ Δεν βρέθηκαν δεδομένα.")
            except Exception as e:
                logger.error(f"  ❌ Exception: {e}")
            summary.append((pair, tf, success))
    # --- Send Telegram summary ---
    ok = sum(1 for _,_,s in summary if s)
    fail = sum(1 for _,_,s in summary if not s)
    msg = f"<b>Data Update Complete</b>\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M')}\nPairs: {len(pairs)}\nTimeframes: {len(timeframes)}\nSuccess: {ok}\nFail: {fail}"
    send_telegram_message(msg)

def get_last_offset():
    try:
        with open(OFFSET_FILE, 'r') as f:
            return int(f.read().strip())
    except Exception:
        return None

def set_last_offset(offset):
    try:
        with open(OFFSET_FILE, 'w') as f:
            f.write(str(offset))
    except Exception:
        pass

def check_for_update_command():
    """Ελέγχει αν υπάρχει νέο μήνυμα 'update Data' ή '/help' στο bot και το εκτελεί."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    last_offset = get_last_offset()
    params = {"timeout": 10}
    if last_offset is not None:
        params["offset"] = last_offset + 1
    try:
        resp = requests.get(url, params=params, timeout=15)
        updates = resp.json()
        if updates.get("ok") and updates.get("result"):
            for update in updates["result"]:
                update_id = update.get("update_id")
                msg = update.get("message")
                if not msg or "text" not in msg:
                    continue
                text = msg["text"].strip().lower()
                chat = msg["chat"]
                if str(chat["id"]) != str(TELEGRAM_CHAT_ID):
                    continue
                if text == "update data":
                    logger.info("Received 'update Data' command from Telegram. Starting update...")
                    send_telegram_message("Ξεκινάει update δεδομένων...")
                    threading.Thread(target=download_all_pairs, args=(load_pairs_from_config(CONFIG_PATH), TIMEFRAMES, DATA_DIR), daemon=True).start()
                elif text == "/help":
                    help_msg = (
                        "<b>🤖 Data Bot - Βοήθεια</b>\n"
                        "\n"
                        "<b>Διαθέσιμες εντολές:</b>\n"
                        "• <b>update Data</b> - Κατεβάζει και ενημερώνει τα δεδομένα\n"
                        "• <b>/help</b> - Εμφανίζει αυτό το μήνυμα βοήθειας\n"
                        "\n"
                        "<b>Status:</b> Bot ενεργός και λειτουργικός ✅"
                    )
                    send_telegram_message(help_msg)
                    logger.info("Sent /help message to user.")
                # Ενημέρωσε το offset ώστε να μην απαντήσει ξανά στο ίδιο μήνυμα
                if update_id is not None:
                    set_last_offset(update_id)
            return True
    except Exception as e:
        logger.warning(f"Error checking for update/help command: {e}")
    return False

def main():
    parser = argparse.ArgumentParser(description="Auto download trading data for Freqtrade.")
    parser.add_argument('--mode', choices=['once', 'daemon', 'listen'], default='once', help='Run once, as daemon, or listen for Telegram command')
    parser.add_argument('--interval', type=int, default=1440, help='Schedule interval in minutes (daemon mode, default 1 day)')
    parser.add_argument('--test-telegram', action='store_true', help='Send a test Telegram message and exit')
    args = parser.parse_args()

    if args.test_telegram:
        send_telegram_message("<b>Test message</b>\nΤο Telegram bot λειτουργεί σωστά! 🟢")
        print("Test message sent to Telegram.")
        return

    pairs = load_pairs_from_config(CONFIG_PATH)
    timeframes = TIMEFRAMES
    data_dir = DATA_DIR

    if args.mode == 'once':
        download_all_pairs(pairs, timeframes, data_dir)
    elif args.mode == 'daemon':
        logger.info(f"Ξεκινάει σε daemon mode (κάθε {args.interval} λεπτά)")
        while True:
            start = time.time()
            download_all_pairs(pairs, timeframes, data_dir)
            elapsed = time.time() - start
            sleep_time = max(0, args.interval * 60 - elapsed)
            logger.info(f"Αναμονή {sleep_time/60:.1f} λεπτά για το επόμενο run...")
            time.sleep(sleep_time)
    elif args.mode == 'listen':
        logger.info("Listening for 'update Data' command on Telegram...")
        last_check = 0
        while True:
            if time.time() - last_check > 10:
                check_for_update_command()
                last_check = time.time()
            time.sleep(2)

if __name__ == "__main__":
    main()