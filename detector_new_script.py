import time
import pandas as pd
from web3 import Web3
from collections import deque

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
address_history = {}
mempool_tracker = {}
dataset = []

print("🕵️  Mempool Observer Running...")

def get_frequency(address):
    now = time.time()
    if address not in address_history: address_history[address] = deque()
    address_history[address].append(now)
    while address_history[address] and address_history[address][0] < now - 60:
        address_history[address].popleft()
    return len(address_history[address])

def extract_features(tx, existing_tx):
    f = {}
    f['tx_hash'] = tx.hash.hex() 
    
    # Basic Features
    f['gas_price'] = tx.gasPrice
    f['value'] = tx.value
    f['gas_limit'] = tx.gas
    f['data_size'] = len(tx.input)
    
    # Nonce Features
    f['nonce_conflict'] = 1 if existing_tx else 0
    if existing_tx:
        f['nonce_gap'] = 0
    else:
        on_chain = w3.eth.get_transaction_count(tx['from'])
        f['nonce_gap'] = tx.nonce - on_chain

    # Gas Economics
    if existing_tx:
        f['gas_differential'] = tx.gasPrice - existing_tx.gasPrice
        f['gas_volatility'] = tx.gasPrice / (existing_tx.gasPrice + 1)
    else:
        f['gas_differential'] = 0
        f['gas_volatility'] = 0

    # Behavioral
    f['submission_frequency'] = get_frequency(tx['from'])
    f['balance_adequacy'] = 1
    f['arrival_interval'] = 0.5 if existing_tx else 10.0
    
    # The "Double Spend" Detector Feature
    if existing_tx:
        f['recipient_similarity'] = 1 if tx['to'] == existing_tx['to'] else 0
    else:
        f['recipient_similarity'] = -1 

    return f

tx_filter = w3.eth.filter('pending')
try:
    while True:
        for tx_hash in tx_filter.get_new_entries():
            try:
                tx = w3.eth.get_transaction(tx_hash)
                sender = tx['from']
                existing = mempool_tracker.get(sender, {}).get(tx.nonce)
                
                row = extract_features(tx, existing)
                dataset.append(row)
                
                if sender not in mempool_tracker: mempool_tracker[sender] = {}
                mempool_tracker[sender][tx.nonce] = tx
                
                if len(dataset) % 100 == 0:
                    print(f"📊 Collected {len(dataset)} features...")
                    pd.DataFrame(dataset).to_csv("features_part7.csv", index=False)
            except: pass
        time.sleep(0.1)
except KeyboardInterrupt:
    pd.DataFrame(dataset).to_csv("features_part7.csv", index=False)
    print("✅ Features Saved.")