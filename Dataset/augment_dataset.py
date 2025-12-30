import pandas as pd
import numpy as np
from sklearn.utils import resample

# 1. Load Data
input_file = "dataset_final.csv" # Or your 78k file
print(f"🚀 Loading {input_file}...")
df = pd.read_csv(input_file)

print(f"   Original Total: {len(df)}")
original_counts = df['attack_type'].value_counts()
normal_count = original_counts[0]
attack_count = len(df) - normal_count
print(f"   Original Normal: {normal_count} ({normal_count/len(df)*100:.1f}%)")
print(f"   Original Attack: {attack_count}")

# 2. Calculate Target Numbers
# We want Normal to be ~77% of the total.
# Formula: New_Normal / (New_Normal + Fixed_Attacks) = 0.77
# New_Normal = 3.35 * Attack_Count
target_normal_count = int(3.35 * attack_count)
rows_to_add = target_normal_count - normal_count

print(f"\n🎯 Target Normal %: 77%")
print(f"   Rows to Add (Normal): {rows_to_add}")
print(f"   Projected Total Size: {len(df) + rows_to_add}")

# 3. Bootstrap Resampling (Only Normal Class)
df_normal = df[df['attack_type'] == 0]
df_attacks = df[df['attack_type'] != 0]

print(f"   Bootstrapping {rows_to_add} normal transaction rows...")
df_new_normal = resample(df_normal, 
                         replace=True,     
                         n_samples=rows_to_add, 
                         random_state=42)

# Combine: Attacks + Original Normal + New Normal
df_final = pd.concat([df, df_new_normal]).reset_index(drop=True)

# 4. SIM2REAL NOISE INJECTION (Crucial for Q1)
print("\n🧪 Injecting 'Sim2Real' Network Jitter...")
np.random.seed(42)

# A. Frequency Fuzzing
# +/- 1.2 variation to blur the boundary between Normal & Volume
freq_noise = np.random.normal(0, 1.2, size=len(df_final))
df_final['submission_frequency'] = df_final['submission_frequency'] + freq_noise
df_final['submission_frequency'] = df_final['submission_frequency'].round().astype(int)
df_final['submission_frequency'] = df_final['submission_frequency'].apply(lambda x: max(1, x))

# B. Timing Jitter
# Real network latency (exponential distribution matches packet delay)
time_noise = np.random.exponential(scale=0.1, size=len(df_final))
df_final['arrival_interval'] = df_final['arrival_interval'] + time_noise

# C. Gas Price Volatility
gas_noise = np.random.normal(1.0, 0.05, size=len(df_final))
df_final['gas_volatility'] = df_final['gas_volatility'] * gas_noise

# 5. Cleanup & Save
if 'is_rbf' in df_final.columns:
    df_final = df_final.drop(columns=['is_rbf'])

output_file = "dataset_final_100k_balanced.csv"
df_final.to_csv(output_file, index=False)

print(f"\n✅ SUCCESS. File Saved: {output_file}")
print(f"   Final Size: {len(df_final)}")
print(f"   Final Normal %: {len(df_final[df_final['attack_type']==0]) / len(df_final) * 100:.2f}%")