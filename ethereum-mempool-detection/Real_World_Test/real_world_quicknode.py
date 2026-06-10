import time
import pandas as pd
import numpy as np
import joblib
from web3 import Web3
from hexbytes import HexBytes
from collections import deque

# --- CONFIGURATION ---
# PASTE YOUR ALCHEMY/QUICKNODE URL HERE
RPC_URL = "https://dimensional-distinguished-layer.quiknode.pro/d75d85ed8329819302ae62f327a84fc22ff4c9fc/"
MODEL_FILE = "../models/xgboost_proposed.pkl"

# --- CONNECT ---
try:
    if RPC_URL.startswith('wss'):
        from web3 import WebSocketProvider
        w3 = Web3(WebSocketProvider(RPC_URL))
    else:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
except:
    w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    print("❌ Connection Failed. Check your URL.")
    exit()

print(f"🌍 Connected! Block: {w3.eth.block_number}")

# Load Model
try:
    model = joblib.load(MODEL_FILE)
    print("🧠 XGBoost Model Loaded.")
except:
    print("❌ Model not found.")
    exit()

# State
address_history = {} 
mempool_tracker = {}
processed_items = set()

# --- THE FIX: ADD 'nonce_gap' (Total 12 Features) ---
FEATURES = [
    'gas_price', 'value', 'gas_limit', 'data_size', 
    'nonce_conflict', 'nonce_gap', 'gas_differential', 'gas_volatility', 
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
    # 1. Basic
    f['gas_price'] = tx.get('gasPrice', tx.get('maxFeePerGas', 0))
    f['value'] = tx['value']
    f['gas_limit'] = tx['gas']
    inp = tx.get('input', b'')
    f['data_size'] = len(inp)

    # 2. Nonce / Conflict
    if existing_tx:
        f['nonce_conflict'] = 1
        f['nonce_gap'] = 0 
        f['gas_differential'] = (f['gas_price'] - existing_tx.get('gasPrice', 0))
        # Avoid div by zero
        old_price = existing_tx.get('gasPrice', 0)
        f['gas_volatility'] = f['gas_price'] / (old_price + 1) if old_price else 1.0
        f['arrival_interval'] = 0.5
        
        if tx.get('to') == existing_tx.get('to'):
            f['recipient_similarity'] = 1
        else:
            f['recipient_similarity'] = 0
    else:
        f['nonce_conflict'] = 0
        f['nonce_gap'] = 0 # Assume 0 gap for real-time speed (API saving)
        f['gas_differential'] = 0
        f['gas_volatility'] = 1.0
        f['arrival_interval'] = 10.0
        f['recipient_similarity'] = -1

    f['submission_frequency'] = get_submission_frequency(tx['from'])
    f['balance_adequacy'] = 1 
    return f

print("\n🕵️  Scanning REAL Transactions... (Ctrl+C to stop)")
print(f"{'Source':<8} | {'Tx Hash':<12} | {'Class':<8} | {'Prob':<6} | {'Status'}")
print("-" * 65)

seen_txs = 0
results = []

try:
    while True:
        try:
            # 1. Fetch Block
            block = w3.eth.get_block('latest', full_transactions=True)
            source_tag = "LATEST"
            
            # 2. Process Sample (First 5 txs)
            for tx_data in block.transactions[:5]:
                try:
                    # Handle Hash vs Object
                    if isinstance(tx_data, (str, bytes, HexBytes)):
                        tx = w3.eth.get_transaction(tx_data)
                    else:
                        tx = tx_data
                    
                    # Deduplicate
                    if tx['hash'] in processed_items:
                        continue
                    processed_items.add(tx['hash'])
                    if len(processed_items) > 5000: processed_items.clear()

                    # Tracker
                    sender = tx['from']
                    nonce = tx['nonce']
                    existing_tx = None
                    if sender in mempool_tracker and nonce in mempool_tracker[sender]:
                        existing_tx = mempool_tracker[sender][nonce]

                    # Extract
                    features_dict = extract_real_features(tx, existing_tx)
                    
                    # PREDICT (Now with 12 features!)
                    input_df = pd.DataFrame([features_dict])[FEATURES]
                    
                    pred_class = model.predict(input_df)[0]
                    pred_prob = np.max(model.predict_proba(input_df))
                    seen_txs += 1
                    
                    # Update Tracker
                    if sender not in mempool_tracker: mempool_tracker[sender] = {}
                    mempool_tracker[sender][nonce] = tx

                    # Print
                    tx_hash = tx['hash'].hex()
                    if pred_class != 0:
                        print(f"{source_tag:<8} | {tx_hash[:10]}.. | TYPE {pred_class}   | {pred_prob:.2f}   | ⚠️ SUSPICIOUS")
                        results.append({"hash": tx_hash, "class": pred_class, "prob": pred_prob})
                    else:
                        print(f"{source_tag:<8} | {tx_hash[:10]}.. | Normal   | {pred_prob:.2f}   | OK")

                except Exception:
                    continue
            
            time.sleep(3)

        except Exception as e:
            # print(f"Block error: {e}")
            time.sleep(2)

except KeyboardInterrupt:
    print(f"\n🛑 Stopped. Analyzed {seen_txs} transactions.")
    if results:
        pd.DataFrame(results).to_csv("real_world_validation.csv", index=False)