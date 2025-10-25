import pandas as pd

inputFile = r"electricityData\tibber_data.csv"
outputFile = r"electricityData\tibber_data_new.csv"  # change to same name if you want overwrite

# Read all as strings so we can safely replace characters
df = pd.read_csv(inputFile, dtype=str)

# Replace Unicode minus signs with ASCII minus across the whole DataFrame
df = df.applymap(lambda x: x.replace("\u2212", "-") if isinstance(x, str) else x)

# Save cleaned CSV
df.to_csv(outputFile, index=False)
print(f"Cleaned CSV saved to {outputFile}")
