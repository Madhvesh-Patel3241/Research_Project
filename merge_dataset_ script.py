import pandas as pd
print("🔄 Merging Data...")
features = pd.read_csv("features_part7.csv")
labels = pd.read_csv("ground_truth.csv")
final_df = pd.merge(features, labels, on="tx_hash", how="inner")
final_df = final_df.rename(columns={'true_label': 'attack_type'})
final_df = final_df.drop(columns=['tx_hash', 'attack_category'])
final_df.to_csv("Final_Research_Dataset.csv", index=False)
print(f"✅ Created 'Final_Research_Dataset.csv' with {len(final_df)} samples.")