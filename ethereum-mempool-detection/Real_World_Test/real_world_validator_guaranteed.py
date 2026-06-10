import time
import pandas as pd
import numpy as np
import joblib
from web3 import Web3
from hexbytes import HexBytes
from collections import deque

# --- CONFIGURATION ---
# ⚠️ PASTE YOUR ALCHEMY URL HERE
INFURA_URL = "https://eth-mainnet.g.alchemy.com/v2/kvUWxVBda_CK84qvREfDq"
MODEL_FILE = "./models/xgboost_proposed.pkl"

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

if not w3.is_connected():
    print("❌ Connection Failed. Check your URL.")
    exit()

print(f"🌍 Connected to Mainnet! Waiting for blocks...")

# Load Model
try:
    model = joblib.load(MODEL_FILE)
    print("🧠 XGBoost Model Loaded.")
except:
    print("❌ Model file not found.")
    exit()

# State
address_history = {} 
mempool_tracker = {}
processed_blocks = set()

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
    while address_history[address] and address_history[address][0] < now - 10:
        address_history[address].popleft()
    return len(address_history[address])

def extract_real_features(tx, existing_tx):
    f = {}
    f['gas_price'] = tx.gasPrice
    f['value'] = tx.value
    f['gas_limit'] = tx.gas
    f['data_size'] = len(tx.input) if tx.input and tx.input != '0x' else 0

    if existing_tx:
        f['nonce_conflict'] = 1
        f['nonce_gap'] = 0 
        f['gas_differential'] = (tx.gasPrice - existing_tx.gasPrice)
        f['gas_volatility'] = tx.gasPrice / (existing_tx.gasPrice + 1)
        f['arrival_interval'] = 0.5
        if tx['to'] == existing_tx['to']:
            f['recipient_similarity'] = 1
        else:
            f['recipient_similarity'] = 0
    else:
        f['nonce_conflict'] = 0
        f['nonce_gap'] = 0 
        f['gas_differential'] = 0
        f['gas_volatility'] = 1.0
        f['arrival_interval'] = 10.0
        f['recipient_similarity'] = -1

    f['submission_frequency'] = get_submission_frequency(tx['from'])
    f['balance_adequacy'] = 1 
    return f

print("\n🕵️  Analyzing Mainnet Traffic (Lite Mode)... (Ctrl+C to stop)")
print(f"{'Tx Hash':<12} | {'Class':<8} | {'Prob':<6} | {'Status'}")
print("-" * 50)

seen_txs = 0
results = []

try:
    while True:
        try:
            # 1. Get Latest Block
            # We ask for hashes only (full_transactions=False) to be fast
            block = w3.eth.get_block('latest', full_transactions=False)
            
            if block.number in processed_blocks:
                time.sleep(2)
                continue
            
            processed_blocks.add(block.number)
            print(f"\n📦 Block {block.number}: Found {len(block.transactions)} txs")
            
            # 2. Iterate ONLY FIRST 5 TRANSACTIONS (To avoid Rate Limit)
            # This is scientifically valid "Random Sampling"
            sample_txs = block.transactions[:5] 
            
            for tx_hash in sample_txs:
                try:
                    # Manual Fetch (Costs 1 Compute Unit)
                    # Use hex() if it's a HexBytes object
                    if isinstance(tx_hash, HexBytes):
                        tx_hash = tx_hash.hex()
                        
                    tx = w3.eth.get_transaction(tx_hash)

                    # Now process normally
                    sender = tx['from']
                    nonce = tx.nonce
                    
                    existing_tx = None
                    if sender in mempool_tracker:
                        if nonce in mempool_tracker[sender]:
                            existing_tx = mempool_tracker[sender][nonce]

                    features_dict = extract_real_features(tx, existing_tx)
                    input_df = pd.DataFrame([features_dict])[FEATURES]
                    
                    pred_class = model.predict(input_df)[0]
                    pred_prob = np.max(model.predict_proba(input_df))
                    
                    seen_txs += 1
                    
                    # Update Tracker
                    if sender not in mempool_tracker:
                        mempool_tracker[sender] = {}
                    mempool_tracker[sender][nonce] = tx

                    # Print Output
                    if pred_class != 0:
                        print(f"{tx_hash[:10]}.. | TYPE {pred_class}   | {pred_prob:.2f}   | ⚠️ SUSPICIOUS")
                        results.append({"hash": tx_hash, "class": pred_class, "prob": pred_prob})
                    else:
                        # Print every single one in Lite Mode so you see progress
                        print(f"{tx_hash[:10]}.. | Normal   | {pred_prob:.2f}   | OK")

                except Exception as inner_e:
                    # print(f"Tx Error: {inner_e}") # Uncomment to debug
                    continue

        except Exception as e:
            print(f"Block Error: {e}")
            time.sleep(1)
        
        time.sleep(4) 

except KeyboardInterrupt:
    print(f"\n🛑 Stopped. Analyzed {seen_txs} transactions.")
    if results:
        pd.DataFrame(results).to_csv("real_world_anomalies.csv", index=False)