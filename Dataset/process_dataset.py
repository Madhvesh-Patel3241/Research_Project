import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Configuration
INPUT_FILE = "dataset_final_q1.csv"
OUTPUT_FILE = "dataset_trained_ready.csv"

print(f"🚀 Loading Raw Data from {INPUT_FILE}...")
df = pd.read_csv(INPUT_FILE)

print(f"   Original Rows: {len(df)}")
print(f"   Original Columns: {df.columns.tolist()}")

# 2. Safety Check: Remove 'is_rbf' (Logic Helper) before training
# We want the model to learn RBF patterns naturally, not cheat.
if 'is_rbf' in df.columns:
    df = df.drop(columns=['is_rbf'])
    print("   ℹ️  Dropped 'is_rbf' column (Standard Practice).")

# 3. The "Sim2Real" Noise Injection
# This makes the perfect Ganache data look like messy Mainnet data
print("\n🧪 Injecting 'Sim2Real' Network Jitter...")
np.random.seed(42) # Reproducibility

# A. Timing Jitter (Network Latency)
# Adds random +/- 0.01s to 0.3s deviation
jitter_time = np.random.normal(loc=0.0, scale=0.15, size=len(df))
df['arrival_interval'] = df['arrival_interval'] + jitter_time
# Enforce physics: Time cannot be negative
df['arrival_interval'] = df['arrival_interval'].apply(lambda x: max(0.01, x))

# B. Gas Price Fluctuation (Market Volatility)
# Adds subtle percentage noise to gas values
jitter_gas = np.random.normal(loc=0.0, scale=0.02, size=len(df)) # 2% variance
df['gas_volatility'] = df['gas_volatility'] + jitter_gas

print("   ✅ Noise Added (Mean=0, Sigma=0.15s)")

# 4. Verification (Correlation Check)
# Ensure noise didn't break the data (Attack signals should still be strong)
print("\n🔍 Verifying Data Integrity...")
corr = df.corr()['attack_type'].sort_values(ascending=False)
print("   Feature Correlation with Attack Type (Should stay high):")
print(corr[['submission_frequency', 'nonce_conflict', 'arrival_interval']])

# 5. Save Final Dataset
df.to_csv(OUTPUT_FILE, index=False)
print(f"\n💾 Saved Final Dataset to: {OUTPUT_FILE}")
print("   (Use this file for 'train_model.py')")