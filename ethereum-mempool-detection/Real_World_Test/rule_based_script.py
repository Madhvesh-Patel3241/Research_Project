"""
================================================================================
ADAPTIVE HEURISTIC ENGINE (SMART RULES) - Q1 JOURNAL REFERENCE IMPLEMENTATION
================================================================================
Based on: Daian et al. (2019) "Flash Boys 2.0" & Karame et al. (2012)
Improved with: Dynamic Median Thresholding & Multi-Variate Bot Detection
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
OUTPUT_CSV = "rule_based_optimized1.csv"
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
tx_tracker = defaultdict(dict)  # {sender: {nonce: {tx_data}}}
address_history = defaultdict(deque) # For frequency

# --- SMART RULES ENGINE ---
def analyze_smart_rules(tx, block_median_gas):
    sender = tx.get('from')
    nonce = tx.get('nonce')
    tx_hash = tx['hash'].hex()
    
    # 1. Get Values
    gas_price = tx.get('gasPrice', tx.get('maxFeePerGas', 0))
    gas_gwei = float(w3.from_wei(gas_price, 'gwei'))
    
    # 2. Update Frequency (Stateful)
    now = time.time()
    # Remove old timestamps (>60s)
    while address_history[sender] and address_history[sender][0] < now - 60:
        address_history[sender].popleft()
    address_history[sender].append(now)
    frequency = len(address_history[sender])

    # --- THE IMPROVED RULES ---
    
    # Rule 1: Confirmed Double Spend (Reference: Karame et al.)
    existing = tx_tracker.get(sender, {}).get(nonce)
    r1_conflict = False
    if existing and existing['hash'] != tx_hash:
        r1_conflict = True

    # Rule 2: Adaptive Aggressive RBF (Reference: Daian et al. + Improvement)
    # Improvement: Uses Median Multiplier (2.0x) instead of static 50 Gwei
   # Rule 2: Aggressive RBF (Sensitive Mode)
    if block_median_gas > 0:
    # We lower the floor to 2.0 Gwei so it works in today's quiet market
        if gas_gwei > (block_median_gas * 2.0) and gas_gwei > 2.0: 
            r2_aggressive = True

    # Rule 3: Multi-Variate Bot Detect (Reference: Torres et al. + Improvement)
    # Improvement: Checks Frequency AND Gas willingness
    r3_bot = False
    if frequency > 8 and gas_gwei > block_median_gas:
        r3_bot = True

    # --- INTERPRETATION ---
    interpretation = "Benign"
    if r1_conflict:
        interpretation = "CRITICAL: Nonce Conflict"
    elif r3_bot:
        interpretation = "High-Freq Bot Activity"
    elif r2_aggressive:
        interpretation = "Aggressive RBF / Speedup"

    return {
        'hash': tx_hash,
        'gas_gwei': gas_gwei,
        'rule_1_conflict': r1_conflict,
        'rule_2_aggressive': r2_aggressive,
        'rule_3_bot': r3_bot,
        'interpretation': interpretation
    }

# --- MAIN LOOP ---
results = []
print(f"\n🔍 Analyzing {TARGET_TRANSACTIONS} Transactions with ADAPTIVE RULES...")
print(f"{'Hash':<10} | {'Gas':<6} | {'Status':<25} | {'Verdict'}")
print("-" * 75)

while len(results) < TARGET_TRANSACTIONS:
    try:
        block = w3.eth.get_block('latest', full_transactions=True)
        
        # Calculate Dynamic Median for Rule 2
        gas_prices = [t.get('gasPrice', 0) for t in block.transactions]
        median_gwei = float(w3.from_wei(np.median(gas_prices), 'gwei')) if gas_prices else 0
            
        for raw_tx in block.transactions[:25]: # Sample 25 to avoid rate limits
            try:
                if isinstance(raw_tx, (str, bytes, HexBytes)):
                    try: tx = dict(w3.eth.get_transaction(raw_tx))
                    except: continue
                else: tx = dict(raw_tx)

                if tx['hash'].hex() in [r['hash'] for r in results]: continue

                # ANALYZE
                analysis = analyze_smart_rules(tx, median_gwei)
                results.append(analysis)
                
                # Update State
                sender = tx.get('from')
                nonce = tx.get('nonce')
                if sender not in tx_tracker: tx_tracker[sender]={}
                tx_tracker[sender][nonce] = {'hash': tx['hash'].hex()}

                # Print
                if analysis['interpretation'] != "Benign":
                    print(f"{analysis['hash'][:10]} | {analysis['gas_gwei']:<6.1f} | ⚠️ FLAG DETECTED           | {analysis['interpretation']}")
                elif len(results) % 20 == 0:
                    print(f"{analysis['hash'][:10]} | {analysis['gas_gwei']:<6.1f} | ✓ Normal                  | Benign")

                if len(results) >= TARGET_TRANSACTIONS: break
                
            except: continue
        time.sleep(3)
    except: time.sleep(2)

# --- SAVE ---
df = pd.DataFrame(results)
df.to_csv(OUTPUT_CSV, index=False)

print("\n" + "="*50)
print("ADAPTIVE RULE ANALYSIS COMPLETE")
print("="*50)
print(df['interpretation'].value_counts())
print(f"\n✓ Saved to {OUTPUT_CSV}")