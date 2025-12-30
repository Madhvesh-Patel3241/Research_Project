import time
import random
import secrets
from web3 import Web3

# ⚠️ Ensure this matches your Ganache settings
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545')) 

if not w3.is_connected():
    print("❌ Failed to connect to Ganache.")
    exit()

# Setup Accounts
accounts = w3.eth.accounts
if len(accounts) < 40:
    print("⚠️  WARNING: Please restart Ganache with 40 Accounts!")

# --- CONFIGURATION ---
botnet_pool = accounts[0:5]
merchant = accounts[5]
accomplice = accounts[6]
normal_users = accounts[10:] 

botnet_state = {acc: 0 for acc in botnet_pool}

print(f"😈 Polymorphic Botnet Started. Mode: Clean & Slow (Q1 Precision).")
print(f"   Nodes: {len(botnet_pool)} | Protocol: 11s Cooldown Enforced.")

def get_available_attacker():
    now = time.time()
    available = [acc for acc in botnet_pool if botnet_state[acc] < now]
    if not available: return None 
    return random.choice(available)

def set_busy(attacker, duration):
    botnet_state[attacker] = time.time() + duration

def check_and_refill(account):
    try:
        balance = w3.eth.get_balance(account)
        if balance < w3.to_wei(50, 'ether'):
            whale = normal_users[random.randint(0, len(normal_users)-1)]
            w3.eth.send_transaction({'from': whale, 'to': account, 'value': w3.to_wei(1000, 'ether')})
    except: pass

def get_dynamic_prices(multiplier=1.15):
    base_gwei = random.randint(10, 60)
    attack_gwei = int(base_gwei * multiplier)
    if attack_gwei <= base_gwei * 1.10: 
        attack_gwei = int(base_gwei * 1.12) + 1
    return w3.to_wei(base_gwei, 'gwei'), w3.to_wei(attack_gwei, 'gwei')

# --- NORMAL TRAFFIC (Slowed Down) ---
def send_legitimate_tx():
    try:
        sender = random.choice(normal_users)
        w3.eth.send_transaction({
            'from': sender, 'to': random.choice(normal_users),
            'value': w3.to_wei(random.uniform(0.1, 0.5), 'ether'),
            'gas': 21000, 'gasPrice': w3.to_wei(random.randint(10, 25), 'gwei')
        })
        print(f"✅ Normal Tx", end="\r")
    except: pass

def send_smart_contract_tx():
    try:
        sender = random.choice(normal_users)
        random_data = secrets.token_hex(random.randint(4, 128)) 
        w3.eth.send_transaction({
            'from': sender, 'to': random.choice(normal_users),
            'value': w3.to_wei(random.uniform(0, 0.1), 'ether'),
            'data': "0x" + random_data,
            'gas': random.randint(50000, 150000),
            'gasPrice': w3.to_wei(random.randint(15, 40), 'gwei')
        })
        print(f"🤖 Contract Tx", end="\r")
    except: pass

def perform_legitimate_rbf():
    try:
        user = random.choice(normal_users)
        nonce = w3.eth.get_transaction_count(user, 'pending')
        friend = random.choice(normal_users)
        low_price = w3.to_wei(10, 'gwei')
        w3.eth.send_transaction({'from': user, 'to': friend, 'value': 0, 'gas': 21000, 'gasPrice': low_price, 'nonce': nonce})
        time.sleep(0.5)
        high_price = w3.to_wei(15, 'gwei')
        w3.eth.send_transaction({'from': user, 'to': friend, 'value': 0, 'gas': 21000, 'gasPrice': high_price, 'nonce': nonce})
        print(f"\n🔵 Legitimate RBF (Hard Negative) Sent")
    except: pass

# --- ATTACKS (With 11s Reset) ---
def perform_basic_double_spend():
    attacker = get_available_attacker()
    if not attacker: return 
    try:
        check_and_refill(attacker)
        nonce = w3.eth.get_transaction_count(attacker, 'pending')
        price_a, price_b = get_dynamic_prices(random.uniform(1.5, 1.8)) 
        val = random.uniform(1.5, 2.5) 
        
        w3.eth.send_transaction({'from': attacker, 'to': merchant, 'value': w3.to_wei(val, 'ether'), 'gas': 21000, 'gasPrice': price_a, 'nonce': nonce})
        time.sleep(random.uniform(0.5, 1.0)) 
        w3.eth.send_transaction({'from': attacker, 'to': accomplice, 'value': w3.to_wei(val, 'ether'), 'gas': 21000, 'gasPrice': price_b, 'nonce': nonce})
        
        print(f"\n⚠️  Attack: Basic Double Spend ({attacker[:6]}...)")
        set_busy(attacker, 15) 
    except: pass

def perform_race_attack():
    attacker = get_available_attacker()
    if not attacker: return 
    try:
        check_and_refill(attacker)
        nonce = w3.eth.get_transaction_count(attacker, 'pending')
        price_a, price_b = get_dynamic_prices(random.uniform(1.15, 1.20)) 
        val = random.uniform(1.0, 3.0)
        
        w3.eth.send_transaction({'from': attacker, 'to': merchant, 'value': w3.to_wei(val, 'ether'), 'gas': 21000, 'gasPrice': price_a, 'nonce': nonce})
        time.sleep(0.02) 
        w3.eth.send_transaction({'from': attacker, 'to': accomplice, 'value': w3.to_wei(val, 'ether'), 'gas': 21000, 'gasPrice': price_b, 'nonce': nonce})
        
        print(f"\n⚠️  Attack: Race Condition ({attacker[:6]}...)")
        set_busy(attacker, 15)
    except: pass

def perform_volume_attack():
    attacker = get_available_attacker()
    if not attacker: return 
    try:
        check_and_refill(attacker)
        nonce = w3.eth.get_transaction_count(attacker, 'pending')
        burst = random.randint(8, 12)
        for i in range(burst): 
            w3.eth.send_transaction({
                'from': attacker, 'to': accounts[8], 'value': w3.to_wei(0.01, 'ether'), 
                'gas': 21000, 'gasPrice': w3.to_wei(random.randint(10, 30), 'gwei'), 
                'nonce': nonce + i
            })
        print(f"\n⚠️  Attack: Volume Spam ({burst} txs) ({attacker[:6]}...)")
        set_busy(attacker, 15) 
    except: pass

def perform_hybrid_attack():
    attacker = get_available_attacker()
    if not attacker: return 
    try:
        check_and_refill(attacker)
        nonce = w3.eth.get_transaction_count(attacker, 'pending')
        
        # 1. Spam Phase (Guarantees Volume Frequency)
        spam_count = random.randint(10, 15)
        for i in range(spam_count):
            w3.eth.send_transaction({'from': attacker, 'to': accounts[9], 'value': 0, 'nonce': nonce + i, 'gasPrice': w3.to_wei(10, 'gwei')})
        
        # 2. Stabilization
        time.sleep(0.5)

        # 3. Double Spend Phase
        conflict = nonce + spam_count
        p_a, p_b = get_dynamic_prices(1.25)
        w3.eth.send_transaction({'from': attacker, 'to': merchant, 'value': w3.to_wei(5, 'ether'), 'nonce': conflict, 'gasPrice': p_a})
        time.sleep(0.1) 
        w3.eth.send_transaction({'from': attacker, 'to': accomplice, 'value': w3.to_wei(5, 'ether'), 'nonce': conflict, 'gasPrice': p_b})
        
        print(f"\n⚠️  Attack: Hybrid Sophisticated ({attacker[:6]}...)")
        set_busy(attacker, 20)
    except: pass

while True:
    rand = random.random()
    # 80% Normal (Slowed down to prevent False Positives)
    if rand < 0.40:
        send_legitimate_tx()
        time.sleep(random.uniform(0.8, 1.5)) # Clean timing
    elif rand < 0.70:
        send_smart_contract_tx()
        time.sleep(random.uniform(1.0, 2.5)) # Clean timing
    elif rand < 0.80:
        perform_legitimate_rbf()
        time.sleep(11) # Reset Detector Window
        
    # 20% Attacks (Mandatory 11s Cooldown to clear 10s Window)
    elif rand < 0.85:
        perform_basic_double_spend()
        time.sleep(11) 
    elif rand < 0.90:
        perform_race_attack()
        time.sleep(11)
    elif rand < 0.95:
        perform_volume_attack()
        time.sleep(11)
    else:
        perform_hybrid_attack()
        time.sleep(11)