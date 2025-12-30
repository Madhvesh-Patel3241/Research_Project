import pandas as pd

# Load your final dataset
df = pd.read_csv("dataset_final_100k_balanced.csv")

print("--- DATASET HEALTH CHECK FOR Q1 JOURNAL ---")
print(f"Total Rows: {len(df)}")

# Count labels
counts = df['attack_type'].value_counts()
print("\nDistribution:")
print(counts)

# Calculate percentages
print("\nPercentages:")
print(df['attack_type'].value_counts(normalize=True) * 100)

print("\n--- Summary ---")
normal_count = counts.get(0, 0)
attack_count = len(df) - normal_count
print(f"Normal: {normal_count} ({normal_count/len(df)*100:.1f}%)")
print(f"Attack: {attack_count} ({attack_count/len(df)*100:.1f}%)")