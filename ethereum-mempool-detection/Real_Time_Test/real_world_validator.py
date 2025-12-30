import time
import pandas as pd
import numpy as np
import joblib
from web3 import Web3
from collections import deque

# --- CONFIGURATION ---
# ⚠️ REPLACE THIS WITH YOUR FULL ALCHEMY/INFURA URL
INFURA_URL = "https://eth-mainnet.g.alchemy.com/v2/kvUWxVBda_CK84qvREfDq" 
MODEL_FILE = "./models/xgboost_proposed.pkl"

# Connect
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

if not w3.is_connected():
    print("❌ Connection Failed. Check your URL.")
    exit()

print(f"🌍 Connected to Mainnet! Block: {w3.eth.block_number}")

# Load Model
try:
    model = joblib.load(MODEL_FILE)
    print("🧠 XGBoost Model Loaded.")
except:
    print("❌ Model not found. Train and save 'xgboost_final_model.pkl' first.")
    exit()

# Setup State Tracking
address_history = {} 
mempool_tracker = {}
processed_hashes = set() # Avoid re-analyzing the same tx

FEATURES = [
    'gas_price', 'value', 'gas_limit', 'data_size', 
    'nonce_conflict', 'gas_differential', 'gas_volatility', 
    'submission_frequency', 'arrival_interval', 
    'balance_adequacy', 'recipient_similarity'
]

def get_submission_frequency(address):
    now = time.time()
    if address not in address_history:
        address_history[address] = deque()
    address_history[address].append(now)
    # 10s Window
    while address_history[address] and address_history[address][0] < now - 10:
        address_history[address].popleft()
    return len(address_history[address])

def extract_real_features(tx, existing_tx):
    f = {}
    # 1. Basic Features
    f['gas_price'] = tx.gasPrice
    f['value'] = tx.value
    f['gas_limit'] = tx.gas
    f['data_size'] = len(tx.input) if tx.input and tx.input != '0x' else 0

    # 2. Conflict/Nonce Logic
    if existing_tx:
        f['nonce_conflict'] = 1
        f['nonce_gap'] = 0 
        f['gas_differential'] = (tx.gasPrice - existing_tx.gasPrice)
        f['gas_volatility'] = tx.gasPrice / (existing_tx.gasPrice + 1)
        f['arrival_interval'] = 0.5 # Assume rapid replacement
        
        # Recipient Logic
        if tx['to'] == existing_tx['to']:
            f['recipient_similarity'] = 1
        else:
            f['recipient_similarity'] = 0
    else:
        f['nonce_conflict'] = 0
        f['nonce_gap'] = 0 
        f['gas_differential'] = 0
        f['gas_volatility'] = 1.0
        f['arrival_interval'] = 10.0 # Default 'safe' interval
        f['recipient_similarity'] = -1

    # 3. Frequency & Balance
    f['submission_frequency'] = get_submission_frequency(tx['from'])
    f['balance_adequacy'] = 1 # Optimization: Skip API call
    return f

# --- MAIN LOOP ---
print("\n🕵️  Scanning Pending Block... (Ctrl+C to stop)")
print(f"{'Tx Hash':<12} | {'Class':<10} | {'Prob':<6} | {'Status'}")
print("-" * 55)

seen_txs = 0
results = []

try:
    while True:
        try:
            # METHOD 2: POLL PENDING BLOCK (More Reliable than Filter)
            # This grabs ~100+ transactions currently waiting to be mined
            block = w3.eth.get_block('pending', full_transactions=True)
            
            for tx in block.transactions:
                tx_hash = tx.hash.hex()
                
                # Skip if already analyzed
                if tx_hash in processed_hashes:
                    continue
                
                processed_hashes.add(tx_hash)
                # Cleanup set to prevent memory leak
                if len(processed_hashes) > 10000:
                    processed_hashes.clear()

                sender = tx['from']
                nonce = tx.nonce
                
                # Tracker Check
                existing_tx = None
                if sender in mempool_tracker:
                    if nonce in mempool_tracker[sender]:
                        existing_tx = mempool_tracker[sender][nonce]

                # Extract & Predict
                features_dict = extract_real_features(tx, existing_tx)
                input_df = pd.DataFrame([features_dict])[FEATURES]
                
                pred_class = model.predict(input_df)[0]
                pred_prob = np.max(model.predict_proba(input_df))
                
                seen_txs += 1
                
                # Update Tracker
                if sender not in mempool_tracker:
                    mempool_tracker[sender] = {}
                mempool_tracker[sender][nonce] = tx

                # PRINTING LOGIC (Show activity)
                # Always print Suspicious, print every 10th Normal
                if pred_class != 0:
                    print(f"{tx_hash[:10]}.. | TYPE {pred_class}   | {pred_prob:.2f}   | ⚠️ SUSPICIOUS")
                elif seen_txs % 10 == 0:
                    print(f"{tx_hash[:10]}.. | Normal     | {pred_prob:.2f}   | OK")
                
                # Store
                results.append({
                    "hash": tx_hash,
                    "class": pred_class,
                    "prob": pred_prob
                })

        except Exception as e:
            pass # Ignore network blips
        
        # Wait 4 seconds (Average block time is 12s, so 4s is safe)
        time.sleep(4)

except KeyboardInterrupt:
    print(f"\n🛑 Stopped. Scanned {seen_txs} real transactions.")
    if results:
        df_res = pd.DataFrame(results)
        print("Summary:")
        print(df_res['class'].value_counts())
        df_res.to_csv("real_world_validation.csv", index=False)
        print("✅ Saved 'real_world_validation.csv'")