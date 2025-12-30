import pandas as pd

df1 = pd.read_csv("dataset_final.csv") # Old Raw
df2 = pd.read_csv("dataset_merged_part567.csv")    # New Raw
df_combined = pd.concat([df1, df2])
df_combined.to_csv("dataset_combined_raw.csv", index=False)