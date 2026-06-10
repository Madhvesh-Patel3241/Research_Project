import time
import pandas as pd
import numpy as np
import joblib
from web3 import Web3
from collections import deque, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json

# --- CONFIGURATION ---
INFURA_URL = "https://eth-mainnet.g.alchemy.com/v2/kvUWxVBda_CK84qvREfDq"
MODEL_FILE = "./models/xgboost_proposed.pkl"
BLOCKS_TO_ANALYZE = 50
SAVE_INTERVAL = 10
TXS_PER_BLOCK = 30  # Analyze first 30 txs per block

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

if not w3.is_connected():
    print("❌ Connection Failed. Check your Alchemy/Infura URL.")
    exit()

print(f"🌍 Connected to Ethereum Mainnet!")
print(f"📊 Experiment Setup: Analyzing {BLOCKS_TO_ANALYZE} blocks\n")

# Load Model
try:
    model = joblib.load(MODEL_FILE)
    print("🧠 XGBoost Model Loaded Successfully")
except Exception as e:
    print(f"❌ Model file not found: {e}")
    exit()

# Feature Configuration
FEATURES = [
    'gas_price', 'value', 'gas_limit', 'data_size', 
    'nonce_conflict', 'gas_differential', 'gas_volatility', 
    'submission_frequency', 'arrival_interval', 
    'balance_adequacy', 'recipient_similarity'
]

# Data Storage
experiment_data = {
    'transactions': [],
    'anomalies': [],
    'block_stats': [],
    'temporal_patterns': []
}

# State Tracking
address_history = defaultdict(deque)
mempool_tracker = defaultdict(dict)
processed_blocks = set()

def get_submission_frequency(address, timestamp):
    """Calculate transaction frequency for an address"""
    address_history[address].append(timestamp)
    cutoff = timestamp - 60
    while address_history[address] and address_history[address][0] < cutoff:
        address_history[address].popleft()
    return len(address_history[address])

def safe_divide(numerator, denominator, default=1.0):
    """Safe division with default value"""
    try:
        if denominator == 0 or denominator is None:
            return default
        return numerator / denominator
    except:
        return default

def extract_features(tx, existing_tx, block_timestamp):
    """Extract all features from a transaction"""
    features = {}
    
    # Basic transaction features - with safety checks
    try:
        features['gas_price'] = float(tx.get('gasPrice', 0)) / 1e9  # Gwei
    except:
        features['gas_price'] = 0.0
    
    try:
        features['value'] = float(tx.get('value', 0)) / 1e18  # ETH
    except:
        features['value'] = 0.0
    
    try:
        features['gas_limit'] = int(tx.get('gas', 0))
    except:
        features['gas_limit'] = 21000
    
    try:
        input_data = tx.get('input', '0x')
        features['data_size'] = len(input_data) if input_data and input_data != '0x' else 0
    except:
        features['data_size'] = 0
    
    # Conflict detection
    if existing_tx:
        features['nonce_conflict'] = 1
        try:
            gas_diff = float(tx.get('gasPrice', 0)) - float(existing_tx.get('gasPrice', 0))
            features['gas_differential'] = gas_diff / 1e9
        except:
            features['gas_differential'] = 0.0
        
        try:
            features['gas_volatility'] = safe_divide(
                float(tx.get('gasPrice', 1)),
                float(existing_tx.get('gasPrice', 1)),
                1.0
            )
        except:
            features['gas_volatility'] = 1.0
        
        features['arrival_interval'] = 0.5
        
        try:
            features['recipient_similarity'] = 1 if tx.get('to') == existing_tx.get('to') else 0
        except:
            features['recipient_similarity'] = 0
    else:
        features['nonce_conflict'] = 0
        features['gas_differential'] = 0.0
        features['gas_volatility'] = 1.0
        features['arrival_interval'] = 10.0
        features['recipient_similarity'] = -1
    
    # Address behavior
    try:
        features['submission_frequency'] = get_submission_frequency(
            tx.get('from', '0x0'), 
            block_timestamp
        )
    except:
        features['submission_frequency'] = 1
    
    features['balance_adequacy'] = 1
    
    return features

def analyze_block(block):
    """Analyze transactions in a block"""
    block_results = {
        'number': block.number,
        'timestamp': block.timestamp,
        'tx_count': len(block.transactions),
        'anomalies': [],
        'normal': [],
        'predictions': []
    }
    
    tx_processed = 0
    tx_limit = min(TXS_PER_BLOCK, len(block.transactions))
    
    for i, tx in enumerate(block.transactions[:tx_limit]):
        try:
            # Safety checks for transaction object
            if not isinstance(tx, dict):
                continue
            
            sender = tx.get('from')
            if not sender:
                continue
            
            nonce = tx.get('nonce')
            if nonce is None:
                continue
            
            # Check for existing transaction
            existing_tx = mempool_tracker[sender].get(nonce)
            
            # Extract features
            features_dict = extract_features(tx, existing_tx, block.timestamp)
            
            # Ensure all features are present
            for feat in FEATURES:
                if feat not in features_dict:
                    features_dict[feat] = 0.0
            
            input_df = pd.DataFrame([features_dict])[FEATURES]
            
            # Predict
            pred_class = int(model.predict(input_df)[0])
            pred_proba = model.predict_proba(input_df)[0]
            confidence = float(np.max(pred_proba))
            
            # Get transaction hash
            tx_hash = tx.get('hash')
            if tx_hash:
                if isinstance(tx_hash, bytes):
                    tx_hash = tx_hash.hex()
                elif hasattr(tx_hash, 'hex'):
                    tx_hash = tx_hash.hex()
                else:
                    tx_hash = str(tx_hash)
            else:
                tx_hash = f"tx_{block.number}_{i}"
            
            # Store transaction data
            tx_data = {
                'hash': tx_hash,
                'block': int(block.number),
                'from': sender,
                'to': tx.get('to', 'Contract Creation'),
                'nonce': int(nonce),
                'gas_price_gwei': float(features_dict['gas_price']),
                'value_eth': float(features_dict['value']),
                'predicted_class': pred_class,
                'confidence': confidence,
                'class_probabilities': [float(p) for p in pred_proba],
                'features': features_dict
            }
            
            experiment_data['transactions'].append(tx_data)
            block_results['predictions'].append(pred_class)
            tx_processed += 1
            
            # Categorize result
            if pred_class != 0:
                experiment_data['anomalies'].append(tx_data)
                block_results['anomalies'].append(tx_data)
                print(f"  ⚠️  {tx_hash[:12]}... | Class {pred_class} | Conf: {confidence:.3f}")
            else:
                block_results['normal'].append(tx_data)
            
            # Update tracker
            mempool_tracker[sender][nonce] = tx
            
        except Exception as e:
            print(f"  ⚠️ Tx {i} error: {str(e)[:50]}")
            continue
    
    return block_results, tx_processed

def generate_statistics():
    """Generate comprehensive statistics"""
    if len(experiment_data['transactions']) == 0:
        return {
            'total_transactions': 0,
            'total_anomalies': 0,
            'anomaly_rate': 0.0,
            'blocks_analyzed': len(experiment_data['block_stats']),
            'error': 'No transactions processed'
        }
    
    df = pd.DataFrame(experiment_data['transactions'])
    
    stats = {
        'total_transactions': len(df),
        'total_anomalies': len(experiment_data['anomalies']),
        'anomaly_rate': len(experiment_data['anomalies']) / len(df) * 100 if len(df) > 0 else 0,
        'blocks_analyzed': len(experiment_data['block_stats']),
        'class_distribution': df['predicted_class'].value_counts().to_dict(),
        'confidence_stats': {
            'mean': float(df['confidence'].mean()),
            'median': float(df['confidence'].median()),
            'std': float(df['confidence'].std()),
            'min': float(df['confidence'].min()),
            'max': float(df['confidence'].max())
        }
    }
    
    # Per-class statistics
    for class_id in df['predicted_class'].unique():
        class_df = df[df['predicted_class'] == class_id]
        stats[f'class_{int(class_id)}_count'] = len(class_df)
        stats[f'class_{int(class_id)}_avg_confidence'] = float(class_df['confidence'].mean())
    
    return stats

def create_visualizations():
    """Create publication-quality visualizations"""
    if len(experiment_data['transactions']) == 0:
        print("⚠️  No transactions to visualize")
        return
    
    df = pd.DataFrame(experiment_data['transactions'])
    
    sns.set_style("whitegrid")
    plt.rcParams['figure.dpi'] = 300
    
    fig = plt.figure(figsize=(15, 10))
    
    # 1. Class Distribution
    ax1 = plt.subplot(2, 3, 1)
    class_counts = df['predicted_class'].value_counts().sort_index()
    class_labels = ['Normal', 'Front-Running', 'Sandwich', 'Gas Manip']
    colors = ['green', 'orange', 'red', 'purple']
    ax1.bar(range(len(class_counts)), class_counts.values, 
            color=[colors[i] for i in class_counts.index])
    ax1.set_xlabel('Transaction Class')
    ax1.set_ylabel('Count')
    ax1.set_title('Classification Distribution (Real Data)')
    ax1.set_xticks(range(len(class_counts)))
    ax1.set_xticklabels([class_labels[i] for i in class_counts.index], rotation=45, ha='right')
    
    # 2. Confidence Distribution
    ax2 = plt.subplot(2, 3, 2)
    for class_id in sorted(df['predicted_class'].unique()):
        class_df = df[df['predicted_class'] == class_id]
        ax2.hist(class_df['confidence'], alpha=0.5, bins=20, 
                label=class_labels[int(class_id)])
    ax2.set_xlabel('Prediction Confidence')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Confidence Distribution by Class')
    ax2.legend()
    
    # 3. Gas Price vs Value
    ax3 = plt.subplot(2, 3, 3)
    normal = df[df['predicted_class'] == 0]
    anomalies = df[df['predicted_class'] != 0]
    
    if len(normal) > 0:
        ax3.scatter(normal['gas_price_gwei'], normal['value_eth'], 
                   alpha=0.3, s=10, label='Normal', c='blue')
    if len(anomalies) > 0:
        ax3.scatter(anomalies['gas_price_gwei'], anomalies['value_eth'], 
                   alpha=0.7, s=30, label='Anomaly', c='red', marker='x')
    
    ax3.set_xlabel('Gas Price (Gwei)')
    ax3.set_ylabel('Value (ETH)')
    ax3.set_title('Transaction Patterns (Real Mainnet)')
    ax3.legend()
    if df['value_eth'].max() > 0:
        ax3.set_yscale('log')
    
    # 4. Temporal Pattern
    ax4 = plt.subplot(2, 3, 4)
    block_anomalies = df.groupby('block')['predicted_class'].apply(lambda x: (x != 0).sum())
    ax4.plot(block_anomalies.index, block_anomalies.values, marker='o', linewidth=2, markersize=4)
    ax4.set_xlabel('Block Number')
    ax4.set_ylabel('Anomaly Count')
    ax4.set_title('Temporal Anomaly Distribution')
    ax4.grid(True, alpha=0.3)
    
    # 5. Anomaly Rate by Block
    ax5 = plt.subplot(2, 3, 5)
    block_total = df.groupby('block').size()
    block_anomaly_rate = (block_anomalies / block_total * 100).fillna(0)
    ax5.bar(range(len(block_anomaly_rate)), block_anomaly_rate.values, color='coral')
    ax5.set_xlabel('Block Index')
    ax5.set_ylabel('Anomaly Rate (%)')
    ax5.set_title('Anomaly Rate per Block')
    ax5.axhline(y=block_anomaly_rate.mean(), color='red', linestyle='--', label=f'Mean: {block_anomaly_rate.mean():.1f}%')
    ax5.legend()
    
    # 6. Class Proportion Pie
    ax6 = plt.subplot(2, 3, 6)
    class_matrix = df['predicted_class'].value_counts().sort_index()
    wedges, texts, autotexts = ax6.pie(
        class_matrix.values, 
        labels=[class_labels[i] for i in class_matrix.index], 
        autopct='%1.1f%%', 
        colors=[colors[i] for i in class_matrix.index]
    )
    ax6.set_title('Class Proportion')
    
    plt.tight_layout()
    plt.savefig('real_world_experiment_results.png', dpi=300, bbox_inches='tight')
    print("\n📊 Visualization saved: real_world_experiment_results.png")

def save_results():
    """Save all results"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save complete data
    with open(f'experiment_results_{timestamp}.json', 'w') as f:
        json.dump(experiment_data, f, indent=2, default=str)
    
    # Save transactions
    if len(experiment_data['transactions']) > 0:
        df = pd.DataFrame(experiment_data['transactions'])
        df.to_csv(f'real_world_transactions_{timestamp}.csv', index=False)
        
        # Save anomalies
        if len(experiment_data['anomalies']) > 0:
            anomaly_df = pd.DataFrame(experiment_data['anomalies'])
            anomaly_df.to_csv(f'detected_anomalies_{timestamp}.csv', index=False)
    
    # Save statistics
    stats = generate_statistics()
    with open(f'experiment_statistics_{timestamp}.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"\n💾 Results saved with timestamp: {timestamp}")
    return stats

# Main Experiment Loop
print(f"🚀 Starting Real-World Experiment\n{'='*60}\n")

try:
    blocks_analyzed = 0
    total_txs_processed = 0
    start_time = time.time()
    
    while blocks_analyzed < BLOCKS_TO_ANALYZE:
        try:
            block = w3.eth.get_block('latest', full_transactions=True)
            
            if block.number in processed_blocks:
                time.sleep(3)
                continue
            
            processed_blocks.add(block.number)
            blocks_analyzed += 1
            
            print(f"\n📦 Block {block.number} ({blocks_analyzed}/{BLOCKS_TO_ANALYZE})")
            print(f"   Total Transactions: {len(block.transactions)}")
            
            # Analyze block
            block_results, tx_count = analyze_block(block)
            experiment_data['block_stats'].append(block_results)
            total_txs_processed += tx_count
            
            print(f"   Processed: {tx_count} | Anomalies: {len(block_results['anomalies'])}")
            
            # Periodic save
            if blocks_analyzed % SAVE_INTERVAL == 0:
                save_results()
                print(f"\n✓ Checkpoint saved at {blocks_analyzed} blocks")
            
            time.sleep(2)
            
        except Exception as e:
            print(f"   ⚠️ Block Error: {str(e)[:100]}")
            time.sleep(5)
            continue
    
    # Final analysis
    print(f"\n{'='*60}")
    print(f"✅ Experiment Complete!")
    print(f"⏱️  Duration: {time.time() - start_time:.1f} seconds")
    print(f"{'='*60}\n")
    
    stats = save_results()
    
    if stats.get('total_transactions', 0) > 0:
        print("\n📈 EXPERIMENT SUMMARY")
        print(f"{'='*60}")
        print(f"Total Transactions Analyzed: {stats['total_transactions']}")
        print(f"Blocks Analyzed: {stats['blocks_analyzed']}")
        print(f"Anomalies Detected: {stats['total_anomalies']}")
        print(f"Anomaly Rate: {stats['anomaly_rate']:.2f}%")
        print(f"\nClass Distribution:")
        class_names = {0: 'Normal', 1: 'Front-Running', 2: 'Sandwich', 3: 'Gas Manipulation'}
        for class_id, count in sorted(stats['class_distribution'].items()):
            pct = count/stats['total_transactions']*100
            print(f"  {class_names.get(int(class_id), f'Class {class_id}')}: {count} ({pct:.1f}%)")
        print(f"\nConfidence Statistics:")
        print(f"  Mean: {stats['confidence_stats']['mean']:.3f}")
        print(f"  Median: {stats['confidence_stats']['median']:.3f}")
        print(f"  Std Dev: {stats['confidence_stats']['std']:.3f}")
        print(f"{'='*60}")
        
        create_visualizations()
        print("\n✅ Experiment complete! Data ready for paper.")
    else:
        print("\n⚠️  No transactions were processed. Check model or data issues.")
    
except KeyboardInterrupt:
    print(f"\n\n🛑 Stopped by user at {blocks_analyzed} blocks")
    save_results()
    if len(experiment_data['transactions']) > 0:
        create_visualizations()

print("\n🎓 Results ready for academic publication!")