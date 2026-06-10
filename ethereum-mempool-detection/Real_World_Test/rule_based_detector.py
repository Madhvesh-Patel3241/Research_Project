"""
================================================================================
DETERMINISTIC HEURISTIC ENGINE FOR ETHEREUM MEMPOOL SECURITY
================================================================================
Purpose: Rule-based detection of Double Spending & RBF Anomalies for Q1 Journal.
Logic: Finite State Machine (FSM) tracking Nonce transitions.
"""

import time
import pandas as pd
import numpy as np
from web3 import Web3
from hexbytes import HexBytes
from collections import deque, defaultdict
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
# ⚠️ PASTE YOUR QUICKNODE URL HERE
RPC_URL = "https://dimensional-distinguished-layer.quiknode.pro/d75d85ed8329819302ae62f327a84fc22ff4c9fc/"
OUTPUT_CSV = "rule_based_analysis.csv"
TARGET_TRANSACTIONS = 500

# ============================================================================
# CONNECTION
# ============================================================================
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

print(f"✓ Connected to Mainnet (Block {w3.eth.block_number})")

# ============================================================================
# STATE TRACKING (THE MEMPOOL SIMULATOR)
# ============================================================================
# We must 'remember' transactions to detect conflicts
tx_tracker = defaultdict(dict)  # {sender: {nonce: {tx_data}}}
block_gas_history = deque(maxlen=10) # Track block averages

# ============================================================================
# THE 5-RULE ENGINE
# ============================================================================
def analyze_transaction(tx, block_median_gas):
    """
    Applies 5 Deterministic Rules to classify the transaction.
    """
    sender = tx.get('from')
    nonce = tx.get('nonce')
    tx_hash = tx['hash'].hex()
    
    # Get gas details
    gas_price = tx.get('gasPrice', tx.get('maxFeePerGas', 0))
    gas_gwei = float(w3.from_wei(gas_price, 'gwei'))
    
    # --- CHECK FOR EXISTING TX (The "Golden Rule") ---
    existing = tx_tracker.get(sender, {}).get(nonce)
    
    # Initialize Flags
    r1_conflict = False
    r2_redirect = False
    r3_aggressive = False
    r4_bot_burst = False
    r5_flashbot = False
    
    # RULE 1: NONCE CONFLICT (Direct Double Spend)
    if existing and existing['hash'] != tx_hash:
        r1_conflict = True
        
        # RULE 2: MALICIOUS REDIRECT (Different Recipient)
        if existing['to'] != tx.get('to'):
            r2_redirect = True
            
    # RULE 3: AGGRESSIVE RBF (Inference)
    # If gas is > 50% higher than block median, it's a "Speed Up" or "Attack"
    if block_median_gas > 0 and gas_gwei > (block_median_gas * 1.5):
        r3_aggressive = True
        
    # RULE 4: BOT BURST (High Frequency)
    # Check how many nonces we've seen for this sender recently
    if len(tx_tracker.get(sender, {})) > 4:
        r4_bot_burst = True
        
    # RULE 5: FLASHBOT / PRIVATE (Zero Gas)
    if gas_gwei == 0:
        r5_flashbot = True

    # --- SCIENTIFIC INTERPRETATION ---
    interpretation = "Benign"
    if r1_conflict and r2_redirect:
        interpretation = "CRITICAL: Malicious Double Spend"
    elif r1_conflict:
        interpretation = "RBF Replacement (Same Recipient)"
    elif r3_aggressive:
        interpretation = "Aggressive Gas Bidding (Likely RBF Winner)"
    elif r5_flashbot:
        interpretation = "Private Transaction (Flashbot)"
    elif r4_bot_burst:
        interpretation = "High-Frequency Bot Activity"

    return {
        'hash': tx_hash,
        'gas_gwei': gas_gwei,
        'rule_1_conflict': r1_conflict,
        'rule_2_redirect': r2_redirect,
        'rule_3_aggressive': r3_aggressive,
        'rule_4_bot': r4_bot_burst,
        'rule_5_flashbot': r5_flashbot,
        'interpretation': interpretation
    }

# ============================================================================
# MAIN LOOP
# ============================================================================
results = []
print(f"\n🔍 Analyzing {TARGET_TRANSACTIONS} Transactions via Rule Engine...")
print(f"{'Hash':<10} | {'Gas (Gwei)':<10} | {'Status':<30} | {'Interpretation'}")
print("-" * 85)

while len(results) < TARGET_TRANSACTIONS:
    try:
        # 1. Fetch Block
        block = w3.eth.get_block('latest', full_transactions=True)
        
        # Calculate Median Gas for Baseline (Rule 3)
        gas_prices = [t.get('gasPrice', 0) for t in block.transactions]
        if gas_prices:
            median_wei = np.median(gas_prices)
            median_gwei = float(w3.from_wei(median_wei, 'gwei'))
        else:
            median_gwei = 0
            
        # 2. Iterate
        for raw_tx in block.transactions[:25]: # Sample 25 to be safe
            try:
                # Type Conversion
                if isinstance(raw_tx, (str, bytes, HexBytes)):
                    try: tx = dict(w3.eth.get_transaction(raw_tx))
                    except: continue
                else:
                    tx = dict(raw_tx)

                # Skip if processed
                if tx['hash'].hex() in [r['hash'] for r in results]:
                    continue

                # ANALYZE
                analysis = analyze_transaction(tx, median_gwei)
                
                # STORE
                results.append(analysis)
                
                # UPDATE STATE (For Rule 1 & 4)
                sender = tx.get('from')
                nonce = tx.get('nonce')
                if sender not in tx_tracker: tx_tracker[sender] = {}
                tx_tracker[sender][nonce] = {'hash': tx['hash'].hex(), 'to': tx.get('to')}

                # PRINT INTERESTING ONES
                if analysis['interpretation'] != "Benign":
                    print(f"{analysis['hash'][:10]} | {analysis['gas_gwei']:<10.1f} | ⚠️ RULES TRIGGERED             | {analysis['interpretation']}")
                elif len(results) % 20 == 0:
                    print(f"{analysis['hash'][:10]} | {analysis['gas_gwei']:<10.1f} | ✓ Normal                       | Benign")

                if len(results) >= TARGET_TRANSACTIONS: break
                
            except Exception: continue
            
        time.sleep(3) # Wait for next block

    except Exception: time.sleep(2)

# ============================================================================
# SAVE & SUMMARY
# ============================================================================
df = pd.DataFrame(results)
df.to_csv(OUTPUT_CSV, index=False)

print("\n" + "="*50)
print("RULE-BASED ANALYSIS COMPLETE")
print("="*50)
print("Breakdown of Detected Behaviors:")
print(df['interpretation'].value_counts())
print(f"\n✓ Saved to {OUTPUT_CSV}")