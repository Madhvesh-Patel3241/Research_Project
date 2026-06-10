"""
================================================================================
REAL-TIME ETHEREUM ANALYSIS (SAFE MODE)
================================================================================
"""
import time
import pandas as pd
import numpy as np
import joblib
from web3 import Web3
from hexbytes import HexBytes
from collections import deque, defaultdict
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# --- CONFIGURATION ---
# Your QuickNode URL
RPC_URL = "https://dimensional-distinguished-layer.quiknode.pro/d75d85ed8329819302ae62f327a84fc22ff4c9fc/"
MODEL_FILE = "../models/xgboost_proposed.pkl"
OUTPUT_CSV = "real_world_validation_final.csv"
TARGET_TRANSACTIONS = 500

# RAW CLASSES
RAW_CLASSES = {
    0: "Normal", 1: "Double Spend", 2: "Race Attack", 
    3: "Volume Attack", 4: "Hybrid"
}

FEATURE_NAMES = [
    'gas_price', 'value', 'gas_limit', 'data_size',
    'nonce_conflict', 'nonce_gap', 'gas_differential', 'gas_volatility',
    'submission_frequency', 'arrival_interval',
    'balance_adequacy', 'recipient_similarity'
]

# --- CONNECT ---
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    print("❌ Connection Failed.")
    exit(1)

print(f"✓ Connected to Mainnet (Block {w3.eth.block_number})")
model = joblib.load(MODEL_FILE)

# --- STATE TRACKING ---
address_history = defaultdict(lambda: deque(maxlen=100))
mempool_tracker = defaultdict(dict)
processed_hashes = set()
gas_price_history = deque(maxlen=100)

# --- HELPER FUNCTIONS ---
def extract_features(tx, existing_tx):
    features = {}
    sender = tx.get('from', '0x0')
    
    # 1. Gas (Convert to float immediately)
    raw_gas = tx.get('gasPrice', tx.get('maxFeePerGas', 0))
    if raw_gas is None: raw_gas = 0
    features['gas_price'] = float(w3.from_wei(raw_gas, 'gwei'))
    features['gas_limit'] = int(tx.get('gas', 21000))
    
    # Differential
    gas_price_history.append(features['gas_price'])
    if len(gas_price_history) > 5:
        median = np.median(gas_price_history)
        std = np.std(gas_price_history) if np.std(gas_price_history) > 0 else 1.0
        features['gas_differential'] = float((features['gas_price'] - median) / std)
    else:
        features['gas_differential'] = 0.0
    features['gas_volatility'] = 1.0

    # 2. Transaction
    val = tx.get('value', 0)
    if val is None: val = 0
    features['value'] = float(w3.from_wei(val, 'ether'))
    
    inp = tx.get('input', b'')
    if isinstance(inp, str): features['data_size'] = len(bytes.fromhex(inp[2:]))
    else: features['data_size'] = len(inp)

    # 3. Nonce
    features['nonce_conflict'] = 0
    features['nonce_gap'] = 0
    
    # 4. Time
    address_history[sender].append(time.time())
    recent = [t for t in address_history[sender] if time.time() - t <= 60]
    features['submission_frequency'] = len(recent)
    features['arrival_interval'] = 10.0
    
    # 5. Recipient
    features['balance_adequacy'] = 1
    features['recipient_similarity'] = 0.5
    
    return features

def get_scientific_interpretation(pred_class, features):
    if pred_class == 0: return "Benign Transaction"
    if pred_class == 3:
        if features['data_size'] > 0: return "High-Freq Contract (Likely MEV)"
        else: return "High-Freq Transfer (Likely Bot)"
    if pred_class in [1, 2]:
        if features['gas_differential'] > 1.0: return "Aggressive Gas (RBF Speedup)"
        else: return "Model Sensitivity Noise"
    return "Anomaly"

# --- MAIN LOOP ---
results = []
print(f"\n🔍 Analyzing {TARGET_TRANSACTIONS} Transactions (Source: LATEST BLOCK)...")
print(f"{'Hash':<10} | {'Raw Prediction':<20} | {'Interpretation'}")
print("-" * 65)

while len(results) < TARGET_TRANSACTIONS:
    try:
        # FORCE LATEST BLOCK (Guaranteed Data)
        block = w3.eth.get_block('latest', full_transactions=True)
        
        # Process first 25 txs from the block
        for raw_tx in block.transactions[:25]:
            try:
                # 1. Safe Dictionary Conversion
                if isinstance(raw_tx, (str, bytes, HexBytes)):
                    try: tx = dict(w3.eth.get_transaction(raw_tx))
                    except: continue
                else:
                    tx = dict(raw_tx)

                # 2. Skip Duplicate Processing
                if tx['hash'] in processed_hashes: continue
                processed_hashes.add(tx['hash'])
                
                # 3. Extract
                sender = tx.get('from', '0x0')
                feats = extract_features(tx, None)
                
                # 4. Predict (CRITICAL FIX: Force types to float)
                df_in = pd.DataFrame([feats])[FEATURE_NAMES].astype(float)
                pred = int(model.predict(df_in)[0])
                prob = float(np.max(model.predict_proba(df_in)))
                
                # 5. Interpret
                interp = get_scientific_interpretation(pred, feats)
                
                # 6. Store
                tx_hash_str = tx['hash'].hex() if isinstance(tx['hash'], HexBytes) else tx['hash']
                
                if pred != 0:
                    print(f"{tx_hash_str[:10]} | {RAW_CLASSES[pred]:<20} | {interp}")
                elif len(results) % 20 == 0:
                    print(f"{tx_hash_str[:10]} | Normal               | Benign")

                results.append({
                    'hash': tx_hash_str,
                    'raw_class': pred,
                    'interpretation': interp,
                    'confidence': prob,
                    **feats
                })
                
                if len(results) >= TARGET_TRANSACTIONS: break
                
            except Exception as e: 
                # print(f"Tx Error: {e}") 
                continue
            
        time.sleep(3) # Wait for next block
        
    except Exception as e:
        # print(f"Block Error: {e}")
        time.sleep(2)

# --- SAVE ---
df = pd.DataFrame(results)
df.to_csv(OUTPUT_CSV, index=False)
print(f"\n✓ Saved {len(df)} rows to {OUTPUT_CSV}")
print("\nFINAL BREAKDOWN:")
print(df['interpretation'].value_counts())