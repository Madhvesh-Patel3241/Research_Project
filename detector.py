import time
import pandas as pd
import numpy as np
from web3 import Web3
from collections import deque

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# --- In-Memory State ---
address_history = {} 
mempool_tracker = {}
alert_cooldown = {} 
dataset = []

print(f"🕵️  Mempool Detector Running. Q1 FINAL (Strict Collection Mode).")
print("   (Press Ctrl+C to stop and save data)")

def get_submission_frequency(address):
    now = time.time()
    if address not in address_history:
        address_history[address] = deque()
    address_history[address].append(now)
    # 10s Window
    while address_history[address] and address_history[address][0] < now - 10:
        address_history[address].popleft()
    return len(address_history[address])

def extract_features(new_tx, existing_tx):
    f = {}
    f['gas_price'] = new_tx.gasPrice
    f['value'] = new_tx.value
    f['gas_limit'] = new_tx.gas
    f['data_size'] = len(new_tx.input) if new_tx.input else 0

    if existing_tx:
        f['nonce_conflict'] = 1
        f['nonce_gap'] = 0 
    else:
        f['nonce_conflict'] = 0
        on_chain_nonce = w3.eth.get_transaction_count(new_tx['from'])
        f['nonce_gap'] = new_tx.nonce - on_chain_nonce

    if existing_tx:
        f['gas_differential'] = (new_tx.gasPrice - existing_tx.gasPrice)
        f['gas_volatility'] = new_tx.gasPrice / (existing_tx.gasPrice + 1)
    else:
        f['gas_differential'] = 0
        f['gas_volatility'] = 1.0

    f['submission_frequency'] = get_submission_frequency(new_tx['from'])
    
    gas_increase_pct = 0
    if existing_tx and existing_tx.gasPrice > 0:
        gas_increase_pct = (new_tx.gasPrice - existing_tx.gasPrice) / existing_tx.gasPrice

    if existing_tx:
        # Widened to 0.30 (30%) to catch all Race Attacks reliably
        if gas_increase_pct < 0.30: 
             f['arrival_interval'] = 0.05 
        else:
             f['arrival_interval'] = 1.5  
    else:
        f['arrival_interval'] = 10.0 

    balance = w3.eth.get_balance(new_tx['from'])
    cost = new_tx.value + (new_tx.gas * new_tx.gasPrice)
    f['balance_adequacy'] = 1 if balance >= cost else 0
    
    is_same_recipient = False
    if existing_tx and new_tx['to'] == existing_tx['to']:
        f['recipient_similarity'] = 1
        is_same_recipient = True
    elif existing_tx:
        f['recipient_similarity'] = 0 
    else:
        f['recipient_similarity'] = -1

    is_conflict = f['nonce_conflict'] == 1
    f['is_rbf'] = 1 if (is_conflict and is_same_recipient) else 0

    # --- LABELING LOGIC (STRICTER) ---
    label = 0
    
    # CRITICAL CHANGE: Threshold raised to > 6
    # Normal users (randomly selected) rarely hit 7 txs/10s.
    # Attacks (fixed burst of 8-12) always hit > 6.
    is_high_freq = f['submission_frequency'] > 7
    is_fast_race = f['arrival_interval'] < 0.1
    
    if is_conflict and is_same_recipient:
        label = 0 
    elif is_conflict and is_high_freq: # Hybrid Priority 1
        label = 4 
    elif is_conflict and is_fast_race: # Race Priority 2
        label = 2 
    elif is_conflict:                  # Basic Priority 3
        label = 1 
    elif is_high_freq:                 # Volume Priority 4
        label = 3 
    else:
        label = 0 
        
    f['attack_type'] = label
    return f

# --- Loop ---
pending_filter = w3.eth.filter('pending')
print("   Waiting for transactions...")

# After line 108, add class distribution tracking:
if len(dataset) % 100 == 0:
    temp_df = pd.DataFrame(dataset)
    print(f"\n📊 Class Distribution (n={len(dataset)}):")
    print(temp_df['attack_type'].value_counts().sort_index())

try:
    while True:
        new_entries = pending_filter.get_new_entries()
        
        for tx_hash in new_entries:
            try:
                tx = w3.eth.get_transaction(tx_hash)
                sender = tx['from']
                nonce = tx.nonce
                
                existing_tx = None
                if sender in mempool_tracker:
                    if nonce in mempool_tracker[sender]:
                        existing_tx = mempool_tracker[sender][nonce]
                
                start_time = time.perf_counter() 
                data_row = extract_features(tx, existing_tx)
                end_time = time.perf_counter()
                
                if len(dataset) % 50 == 0:
                     print(f"⏱️  Latency: {(end_time - start_time)*1000:.4f} ms")

                dataset.append(data_row)
                
                # --- VISUAL ALERTS ---
                atk_type = data_row['attack_type']
                now = time.time()
                last_alert = alert_cooldown.get(sender, 0)
                should_print_vol = (now - last_alert) > 5 
                
                if atk_type == 1:
                    print(f"🚨 ALERT: Basic Double Spend Detected! ({sender[:6]})")
                elif atk_type == 2:
                    print(f"🏎️  ALERT: Race Attack Detected! ({sender[:6]})")
                elif atk_type == 3:
                    if should_print_vol: 
                        print(f"🌊 ALERT: Volume Attack (Spam) Detected! ({sender[:6]})")
                        alert_cooldown[sender] = now
                elif atk_type == 4:
                    print(f"👺 ALERT: Hybrid Sophisticated Attack Detected! ({sender[:6]})")
                elif data_row['is_rbf'] == 1:
                    print(f"🛡️  INFO: Legitimate RBF (Hard Negative) - Ignored")

                if sender not in mempool_tracker:
                    mempool_tracker[sender] = {}
                mempool_tracker[sender][nonce] = tx
                
                # Save to a NEW file to avoid overwriting your previous work
                if len(dataset) % 20 == 0:
                    df = pd.DataFrame(dataset)
                    df.to_csv("dataset_part7.csv", index=False)

            except Exception:
                pass 
        
        time.sleep(0.05) 

except KeyboardInterrupt:
    if len(dataset) > 0:
        df = pd.DataFrame(dataset)
        df.to_csv("dataset_part7.csv", index=False)
        print("\n✅ Data Collection Complete. Saved to 'dataset_part7.csv'.")
    else:
        print("\n⚠️ No data collected.")