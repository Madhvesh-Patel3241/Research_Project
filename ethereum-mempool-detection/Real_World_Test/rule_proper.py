"""
================================================================================
STATISTICAL HEURISTIC ENGINE (Z-SCORE / 3-SIGMA)
================================================================================
Methodology: Uses dynamic statistical thresholds (Mean + 3*StdDev) to detect 
statistically significant outliers, mirroring financial anomaly detection.
Reference: "Three-Sigma Rule of Thumb" (Pukelsheim, 1994).
"""

import time
import pandas as pd
import numpy as np
from web3 import Web3
from hexbytes import HexBytes
from collections import deque, defaultdict
import warnings
warnings.filterwarnings('ignore')

# --- CONFIG ---
RPC_URL = "https://dimensional-distinguished-layer.quiknode.pro/d75d85ed8329819302ae62f327a84fc22ff4c9fc/"
OUTPUT_CSV = "rule_based_zscore.csv"
TARGET_TRANSACTIONS = 500

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
    print("❌ Connection Failed.")
    exit(1)

print(f"✓ Connected (Block {w3.eth.block_number})")

# --- STATE ---
tx_tracker = defaultdict(dict)  
address_history = defaultdict(deque)

# --- Z-SCORE ENGINE ---
def analyze_z_score_rules(tx, block_stats):
    sender = tx.get('from')
    tx_hash = tx['hash'].hex()
    
    # 1. Get Transaction Gas
    gas_price = tx.get('gasPrice', tx.get('maxFeePerGas', 0))
    gas_gwei = float(w3.from_wei(gas_price, 'gwei'))
    
    # 2. Get Block Stats (The Dynamic Baseline)
    mean_gas = block_stats['mean']
    std_gas = block_stats['std']
    
    # --- RULE 1: STATISTICAL GAS OUTLIER (Z-Score > 3) ---
    # Logic: Is this gas price 3 standard deviations above the average?
    # This automatically adapts to market volatility.
    r1_outlier = False
    z_score = 0.0
    if std_gas > 0:
        z_score = (gas_gwei - mean_gas) / std_gas
        if z_score > 3.0: # 3-Sigma Rule (Top 0.3% probability)
            r1_outlier = True
            
    # --- RULE 2: BURST DETECTION ---
    now = time.time()
    while address_history[sender] and address_history[sender][0] < now - 60:
        address_history[sender].popleft()
    address_history[sender].append(now)
    
    r2_burst = False
    if len(address_history[sender]) > 10: # >10 tx/min is inhuman
        r2_burst = True

    # --- INTERPRETATION ---
    interpretation = "Benign"
    if r1_conflict := False: # Placeholder for conflict (rare in mined blocks)
        pass
    
    if r1_outlier and r2_burst:
        interpretation = "CRITICAL: High-Freq + Gas Anomaly (Bot)"
    elif r1_outlier:
        interpretation = f"Statistical Gas Outlier (Z={z_score:.1f})"
    elif r2_burst:
        interpretation = "High-Frequency Burst"

    return {
        'hash': tx_hash,
        'gas_gwei': gas_gwei,
        'z_score': z_score,
        'flag_outlier': r1_outlier,
        'flag_burst': r2_burst,
        'interpretation': interpretation
    }

# --- MAIN LOOP ---
results = []
print(f"\n🔍 Analyzing {TARGET_TRANSACTIONS} Transactions using 3-SIGMA RULES...")
print(f"{'Hash':<10} | {'Gas':<6} | {'Z-Score':<6} | {'Verdict'}")
print("-" * 75)

while len(results) < TARGET_TRANSACTIONS:
    try:
        block = w3.eth.get_block('latest', full_transactions=True)
        
        # 1. CALCULATE BLOCK STATISTICS (DYNAMIC)
        gas_prices = [float(w3.from_wei(t.get('gasPrice', 0), 'gwei')) for t in block.transactions]
        if not gas_prices: continue
        
        block_stats = {
            'mean': np.mean(gas_prices),
            'std': np.std(gas_prices)
        }
            
        # 2. ANALYZE TRANSACTIONS
        for raw_tx in block.transactions[:25]:
            try:
                if isinstance(raw_tx, (str, bytes, HexBytes)):
                    try: tx = dict(w3.eth.get_transaction(raw_tx))
                    except: continue
                else: tx = dict(raw_tx)

                if tx['hash'].hex() in [r['hash'] for r in results]: continue

                analysis = analyze_z_score_rules(tx, block_stats)
                results.append(analysis)
                
                # Print
                if analysis['interpretation'] != "Benign":
                    print(f"{analysis['hash'][:10]} | {analysis['gas_gwei']:<6.1f} | {analysis['z_score']:<6.1f} | ⚠️ {analysis['interpretation']}")
                elif len(results) % 20 == 0:
                    print(f"{analysis['hash'][:10]} | {analysis['gas_gwei']:<6.1f} | {analysis['z_score']:<6.1f} | ✓ Benign")

                if len(results) >= TARGET_TRANSACTIONS: break
                
            except: continue
        time.sleep(3)
    except: time.sleep(2)

# --- SAVE ---
df = pd.DataFrame(results)
df.to_csv(OUTPUT_CSV, index=False)

print("\n" + "="*50)
print("STATISTICAL ANALYSIS COMPLETE")
print("="*50)
print(df['interpretation'].value_counts())
print(f"\n✓ Saved to {OUTPUT_CSV}")