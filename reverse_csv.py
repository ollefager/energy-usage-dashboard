import pandas as pd

# Input and output file paths
inputCsvPath = r'C:\Users\ollef\git\home-tools\electricityData\isolarcloud_hourly_data.csv'
outputCsvPath = r'C:\Users\ollef\git\home-tools\electricityData\isolarcloud_hourly_data_rev.csv'

# Read CSV
df = pd.read_csv(inputCsvPath)

# Reverse order of rows
dfReversed = df.iloc[::-1].reset_index(drop=True)

# Save to new CSV
dfReversed.to_csv(outputCsvPath, index=False)