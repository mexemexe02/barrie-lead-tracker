import json
import os
import csv
from datetime import datetime, timedelta

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
LOG_PATH = os.path.join(BASE_DIR, 'trade_log.csv')
PENDING_PATH = os.path.join(BASE_DIR, 'pending_orders.json')
LAST_CHECK_PATH = os.path.join(BASE_DIR, 'last_check.txt')

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"auto_execute": True, "delay_minutes": 5}
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def get_last_check_time():
    if os.path.exists(LAST_CHECK_PATH):
        with open(LAST_CHECK_PATH, 'r') as f:
            return f.read().strip()
    return "1970-01-01T00:00:00Z"

def update_last_check_time(timestamp):
    with open(LAST_CHECK_PATH, 'w') as f:
        f.write(timestamp)

def load_pending():
    if os.path.exists(PENDING_PATH) and os.path.getsize(PENDING_PATH) > 0:
        with open(PENDING_PATH, 'r') as f:
            return json.load(f)
    return []

def save_pending(pending):
    with open(PENDING_PATH, 'w') as f:
        json.dump(pending, f, indent=2)

def log_trade(issuer, ticker, size, trade_type):
    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'issuer', 'ticker', 'size', 'type'])
        writer.writerow([datetime.now().isoformat(), issuer, ticker, size, trade_type])

def estimate_shares(size_str):
    # Simple estimation logic for the simulation
    try:
        if '-' in size_str:
            parts = size_str.split('-')
            clean_val = parts[0].replace('$', '').replace('K', '000').replace('M', '000000').strip()
            return int(float(clean_val) / 100) # Assume avg price of $100 for simplicity
        return 100
    except:
        return 10

def fetch_trades(last_check, config):
    # In a production environment, this would call Capitol Trades API.
    # For this task (cron job simulation), we simulate finding new trades.
    print(f"Checking for trades since {last_check}...")
    
    new_trades = []
    # Simulate a trade found only if it's the first run or certain condition met
    if last_check == "1970-01-01T00:00:00Z":
        new_trades.append({
            "issuer": "Apple Inc.",
            "ticker": "AAPL",
            "size": "$100K - $200K",
            "type": "Buy",
            "timestamp": datetime.now().isoformat()
        })
    return new_trades

def process_trades():
    config = load_config()
    last_check = get_last_check_time()
    new_trades = fetch_trades(last_check, config)
    
    if not new_trades:
        print("No new trades found.")
        return

    pending = load_pending()
    
    for trade in new_trades:
        ticker = trade['ticker']
        issuer = trade['annotated_person'] if 'annotated_person' in trade else trade['issuer']
        size = trade['size']
        trade_type = trade['type']
        
        log_trade(issuer, ticker, size, trade_type)
        shares = estimate_shares(size)
        
        execution_time = (datetime.now() + timedelta(minutes=config['delay_minutes'])).isoformat()
        
        order = {
            "ticker": ticker,
            "issuer": issuer,
            "shares": shares,
            "type": trade_type,
            "scheduled_time": execution_time,
            "status": "queued"
        }
        pending.append(order)
        print(f"Queued order for {ticker}: {shares} shares ({trade_type})")

    save_pending(pending)
    update_last_check_annotated_person_as_part_of_logic(datetime.now().isoformat())

def update_last_check_annotated_person_as_part_of_logic(timestamp):
    # Helper to fix the weirdly named function above 
    update_last_check_time(timestamp)

def execute_pending():
    config = load_config()
    if not config.get('auto_execute', False):
        print("Auto-execute is disabled. Waiting for approval.")
        return

    pending = load_pending()
    now = datetime.now()
    remaining = []
    executed_count = 0

    for order in pending:
        sched_time = datetime.fromisoformat(order['scheduled_time'])
        if now >= sched_time:
            print(f"EXECUTING: {order['type']} {order['shares']} shares of {order['ticker']}")
            order['status'] = 'executed'
            executed_count += 1
        else:
            order['status'] = 'pending'
            remaining.append(order)

    save_pending(remaining)
    if executed_count > 0:
        print(f"Successfully executed {executed_count} pending orders.")

if __name__ == "__main__":
    process_trades()
    execute_pending()
