import pandas as pd
import numpy as np

# Sample historical price data (replace with your actual data)
data = {
    'Date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
    'EURUSD': [1.12, 1.13, 1.14, 1.15, 1.16],
    'GBPUSD': [1.30, 1.31, 1.32, 1.33, 1.34],
    'USDJPY': [110, 111, 112, 113, 114]
}

# Convert data to DataFrame
df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)


# Calculate RSI for each currency pair
def calculate_rsi(data, window=14):
    delta = data.diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    relative_strength = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + relative_strength))
    return rsi


for col in df.columns:
    if col != 'USDJPY':
        df[col + '_RSI'] = calculate_rsi(df[col])

# Normalize RSI values
for col in df.columns:
    if '_RSI' in col:
        df[col] = (df[col] - 50) / 50

# Calculate average normalized RSI for USD pairs
usd_rsi_columns = [col for col in df.columns if 'USD' in col]
average_usd_rsi = df[usd_rsi_columns].mean().mean()
print(df)

print("Average Strength of USD:", average_usd_rsi)
