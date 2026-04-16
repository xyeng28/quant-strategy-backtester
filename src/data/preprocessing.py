import pandas as pd
from sklearn.preprocessing import StandardScaler

def compute_returns(prices: pd.DataFrame, cols):
    returns_df = prices.copy()
    returns_df[cols] = (returns_df[cols] / returns_df[cols].shift(1)) - 1
    # returns_df[cols] = returns_df[cols].pct_change()
    returns_df.dropna(inplace=True)
    print(returns_df)
    return returns_df

def scale_data(data_df: pd.DataFrame):
    scaler = StandardScaler()
    scaled_X = scaler.fit_transform(data_df)
    print(scaled_X)
    return scaled_X, scaler

