import time
import random
import csv
from web3 import Web3

# --- SETUP ---
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
if not w3.is_connected():
    print("❌ Failed to connect to Ganache. Restart with 40 accounts!")
    exit()

accounts = w3.eth.accounts
botnet = accounts[0:5]
merchant = accounts[5]
accomplice = accounts[6]
normal_users = accounts[10:]
botnet_state = {acc: 0 for acc in botnet}

# --- GROUND TRUTH LOGGING (THE Q1 REQUIREMENT) ---
with open("ground_truth.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["tx_hash", "true_label", "attack_category"])

def log_label(tx_hash, label, category):
    """Writes the 'Answer Key' to a file."""
    try:
        with open("ground_truth.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([tx_hash.hex(), label, category])
    except: pass

def get_attacker():
    now = time.time()
    available = [acc for acc in botnet if botnet_state[acc] < now]
    return random.choice(available) if available else None

def set_busy(acc, duration):
    botnet_state[acc] = time.time() + duration

# --- ATTACK & NORMAL LOGIC ---
def send_normal_tx():
    try:
        sender = random.choice(normal_users)
        tx = w3.eth.send_transaction({
            'from': sender, 'to': random.choice(normal_users),
            'value': w3.to_wei(random.uniform(0.1, 0.5), 'ether'),
            'gas': 21000, 'gasPrice': w3.to_wei(random.randint(10, 20), 'gwei')
        })
        log_label(tx, 0, "Normal") 
        print(f"✅ Normal Tx", end="\r")
    except: pass

def perform_legitimate_rbf():
    # Scenario: User updates transaction to SAME recipient (Not an attack)
    try:
        user = random.choice(normal_users)
        nonce = w3.eth.get_transaction_count(user, 'pending')
        friend = random.choice(normal_users)
        
        # Tx 1: Low Fee
        tx1 = w3.eth.send_transaction({
            'from': user, 'to': friend, 'value': w3.to_wei(0.1, 'ether'),
            'gas': 21000, 'gasPrice': w3.to_wei(5, 'gwei'), 'nonce': nonce
        })
        log_label(tx1, 0, "Normal_Stuck")
        time.sleep(0.5)

        # Tx 2: High Fee -> SAME Recipient
        tx2 = w3.eth.send_transaction({
            'from': user, 'to': friend, 'value': w3.to_wei(0.1, 'ether'),
            'gas': 21000, 'gasPrice': w3.to_wei(15, 'gwei'), 'nonce': nonce
        })
        log_label(tx2, 0, "Normal_RBF") 
        print(f"\n🛡️  Legitimate RBF (Same Recipient) Sent")
    except: pass

def perform_double_spend():
    # Scenario: Attacker replaces transaction to DIFFERENT recipient (Fraud)
    attacker = get_attacker()
    if not attacker: return
    try:
        nonce = w3.eth.get_transaction_count(attacker, 'pending')
        
        # Tx 1: Pay Merchant (The "Bait")
        tx1 = w3.eth.send_transaction({
            'from': attacker, 'to': merchant, 'value': w3.to_wei(1, 'ether'),
            'gas': 21000, 'gasPrice': w3.to_wei(10, 'gwei'), 'nonce': nonce
        })
        log_label(tx1, 0, "DS_Bait") 

        time.sleep(random.uniform(0.5, 1.0))

        # Tx 2: Pay Accomplice (The "Steal") -> DIFFERENT Recipient
        tx2 = w3.eth.send_transaction({
            'from': attacker, 'to': accomplice, 'value': w3.to_wei(1, 'ether'),
            'gas': 21000, 'gasPrice': w3.to_wei(20, 'gwei'), 'nonce': nonce
        })
        log_label(tx2, 1, "Double_Spend") 
        print(f"\n⚠️  Double Spend Attack Launched!")
        set_busy(attacker, 10)
    except: pass

def perform_volume_attack():
    attacker = get_attacker()
    if not attacker: return
    try:
        nonce = w3.eth.get_transaction_count(attacker, 'pending')
        burst = 10
        for i in range(burst):
            tx = w3.eth.send_transaction({
                'from': attacker, 'to': accomplice, 'value': 0,
                'gas': 21000, 'gasPrice': w3.to_wei(15, 'gwei'), 'nonce': nonce + i
            })
            log_label(tx, 3, "Volume_Attack")
        print(f"\n🌊 Volume Attack ({burst} txs)")
        set_busy(attacker, 15)
    except: pass

print("😈 Attacker Script Running (Q1 Logic)...")
while True:
    rand = random.random()
    if rand < 0.60: send_normal_tx()
    elif rand < 0.70: perform_legitimate_rbf()
    elif rand < 0.80: perform_double_spend()
    elif rand < 0.90: perform_volume_attack()
    time.sleep(random.uniform(0.5, 1.5))