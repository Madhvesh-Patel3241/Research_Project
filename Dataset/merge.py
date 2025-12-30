import pandas as pd

# Load the datasets
df1 = pd.read_csv("dataset_part5.csv")
df2 = pd.read_csv("dataset_part6.csv")
df3 = pd.read_csv("dataset_part7.csv")

# Combine them (row-wise)
merged = pd.concat([df1, df2, df3], ignore_index=True)

# Save to one file
merged.to_csv("dataset_merged_part567.csv", index=False)
