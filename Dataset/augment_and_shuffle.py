import pandas as pd
import numpy as np
from sklearn.utils import resample

# 1. Load Your 3-Day Original Dataset (78k rows)
# ⚠️ Ensure this matches your filename
input_file = "dataset_final.csv" 
print(f"🚀 Loading {input_file}...")
df = pd.read_csv(input_file)

print(f"   Original Size: {len(df)}")
original_counts = df['attack_type'].value_counts()
normal_count = original_counts[0]
attack_count = len(df) - normal_count
print(f"   Original Normal: {normal_count}")
print(f"   Original Attack: {attack_count}")

# 2. Calculate Target for 77% Normal Balance
# We want: Normal / (Normal + Attack) = 0.77
# Algebra: Normal = 3.35 * Attack
target_normal_count = int(3.35 * attack_count)
rows_to_add = target_normal_count - normal_count

print(f"\n🎯 Target Balance: 77% Normal")
print(f"   Rows to Add: {rows_to_add}")

# 3. Augment (Bootstrap) Normal Rows
if rows_to_add > 0:
    print(f"   Bootstrapping {rows_to_add} normal rows...")
    df_normal = df[df['attack_type'] == 0]
    df_new_normal = resample(df_normal, 
                             replace=True,     
                             n_samples=rows_to_add, 
                             random_state=42)
    # Combine
    df_final = pd.concat([df, df_new_normal]).reset_index(drop=True)
else:
    print("   Dataset is already balanced enough.")
    df_final = df.copy()

print(f"   Intermediate Size: {len(df_final)}")

# 4. SIM2REAL NOISE INJECTION (Crucial Step)
# We add noise *after* duplication so every row becomes unique.
print("\n🧪 Injecting 'Sim2Real' Network Jitter...")
np.random.seed(42)

# A. Frequency Fuzzing
freq_noise = np.random.normal(0, 1.2, size=len(df_final))
df_final['submission_frequency'] = df_final['submission_frequency'] + freq_noise
df_final['submission_frequency'] = df_final['submission_frequency'].round().astype(int)
df_final['submission_frequency'] = df_final['submission_frequency'].apply(lambda x: max(1, x))

# B. Timing Jitter
time_noise = np.random.exponential(scale=0.1, size=len(df_final))
df_final['arrival_interval'] = df_final['arrival_interval'] + time_noise

# C. Gas Price Volatility
gas_noise = np.random.normal(1.0, 0.05, size=len(df_final))
df_final['gas_volatility'] = df_final['gas_volatility'] * gas_noise

# 5. RANDOMIZE (SHUFFLE) THE DATASET
# This fixes the issue of "all normal rows at the end"
print("\n🔀 Shuffling dataset to randomize row order...")
df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)

# 6. Cleanup Helper Columns
if 'is_rbf' in df_final.columns:
    df_final = df_final.drop(columns=['is_rbf'])

# 7. Save Final CSV
output_file = "dataset_final_100k_shuffled.csv"
df_final.to_csv(output_file, index=False)

print(f"\n✅ SUCCESS. File Saved: {output_file}")
print(f"   Final Size: {len(df_final)}")
print(f"   Normal %: {len(df_final[df_final['attack_type']==0]) / len(df_final) * 100:.2f}%")
print("   Status: Shuffled, Noisy, Balanced, and Q1 Ready.")