import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression

def compute_returns(prices: pd.DataFrame):
    # prices.set_index('Date', inplace=True)
    returns_df = prices.copy()
    cols = ['Wheat','Corn','Oil','Gas','Coal']
    returns_df[cols] = (returns_df[cols] / returns_df[cols].shift(1)) - 1
    # returns_df[cols] = returns_df[cols].pct_change()
    # print(returns_df)
    return returns_df

def pre_processing(returns_df):
    returns_df.dropna(inplace=True)
    return returns_df

def pca_signal(returns_df, principal_components):
    """
    PCA is centered around the mean 0. PC1 = 0 -> neutral.
    PC1 > 0 -> movement aligned with positive direction of PC1
    PC1 < 0 -> movement aligned with negative direction of PC1
    :param returns_df:
    :param principal_components:
    :return:
    """
    returns_df['pc1'] = principal_components[:, 0] #take all rows, take column 0 (PC1) -> Assign 1D array to each row
    returns_df['pc2'] = principal_components[:, 1]

    returns_df['signal'] = 0
    returns_df['side'] = ''
    returns_df.loc[returns_df['pc1'] > 0, 'signal'] = 1
    returns_df.loc[returns_df['pc1'] > 0, 'side'] = 'LONG'
    returns_df.loc[returns_df['pc1'] < 0, 'signal'] = -1
    returns_df.loc[returns_df['pc1'] < 0, 'side'] = 'SHORT'
    return returns_df

def regression_signal(returns_df, y_pred):
    """
    y_pred is the predicted returns of the y. Eg. Wheat. If pred return > 0 -> expect price to go up.
    If pred return < 0 -> expect price to go down.
    :param returns_df:
    :param principal_components:
    :return:
    """
    returns_df['y_pred'] = y_pred
    returns_df['signal'] = 0
    returns_df.loc[returns_df['y_pred'] > 0, 'signal'] = 1
    returns_df.loc[returns_df['y_pred'] > 0, 'side'] = 'LONG'
    returns_df.loc[returns_df['y_pred'] < 0, 'signal'] = -1
    returns_df.loc[returns_df['y_pred'] < 0, 'side'] = 'SHORT'
    return returns_df

def backtest(returns_df):
    # print(returns_df)
    returns_df['daily_ret'] = 0.0
    cols = ['Wheat','Corn','Oil','Gas','Coal']
    # print(returns_df[cols].mean(axis=1))
    returns_df['daily_ret'] = returns_df['signal'] * returns_df[cols].mean(axis=1)
    print(returns_df)
    return returns_df

def metrics(returns_df):
    """
    Sharpe ratio measures risk adjusted returns
    :param returns_df:
    :return:
    """
    returns_df['cum_ret'] = (1 + returns_df['daily_ret']).cumprod()
    print(returns_df)

    if returns_df['daily_ret'].std() == 0:
        sharpe_ratio = 0
    else:
        sharpe_ratio = round(returns_df['daily_ret'].mean() / returns_df['daily_ret'].std() * np.sqrt(252), 2)
    max_dd = (returns_df['cum_ret'] / returns_df['cum_ret'].cummax() - 1).min()
    total_cum_ret = returns_df['cum_ret'].iloc[-1] - 1
    print(f'\nsharpe ratio: {sharpe_ratio}')
    print(f'\nmax drawdown: {max_dd:.2%}')
    print(f'\nTotal cumulative return: {total_cum_ret:.2%}')
    metrics_df = pd.DataFrame({
        'Sharpe Ratio': [sharpe_ratio],
        'Max Drawdown': [max_dd],
        'Total Cumulative Return': [total_cum_ret],
    })
    print(f'\nmetrics_df:\n{metrics_df}')
    return metrics_df

def plot_portfolio_val(returns_df, initial_capital):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    returns_df['port_val'] = returns_df['cum_ret'] * initial_capital
    returns_df['dd'] = returns_df['cum_ret'] / returns_df['cum_ret'].cummax() - 1
    ax1.plot(returns_df['Date'], returns_df['port_val'], label='Portfolio Value', color='blue')
    ax1.set_title(f'PCA Strategy Portfolio Value')
    ax1.set_ylabel('Portfolio Value ($)')
    ax1.legend()
    # ax1.grid(True)

    ax2.plot(returns_df['Date'], returns_df['dd'], label='Drawdown', color='red')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Drawdown (%)')
    ax2.set_title(f'PCA Strategy Drawdown')
    ax2.legend()
    # ax2.grid(True)

    plt.tight_layout()
    plt.show()

def pca(returns_df):
    """
    PC1 represents the dominant factor driving co-movement among the commodities. If all prices tend to move together, PC1 captures that shared movement.
    PC2 is orthogonal to PC1 and explains the next largest variance, capturing patterns not explained by PC1.
    :return:
    """
    pca_df = returns_df.copy()
    cols = ['Wheat','Corn','Oil','Gas','Coal']
    pca_df = pca_df[cols]
    scaler = StandardScaler()
    scaled_X = scaler.fit_transform(pca_df)
    print(scaled_X)

    pca = PCA(n_components=2)
    principal_components = pca.fit_transform(scaled_X)
    print(f'principal components:\n{principal_components}')
    print(f'PCA components:\n{pca.components_}')
    print(f'PCA n components:\n{pca.n_components_}')
    return principal_components

def regression(returns_df: pd.DataFrame):
    """
    r squared = 1 -> perfect fit, explains all variability in y
    r squared = 0 -> explains none of the variability, same as just predicting the mean by using the average of (wheat) daily returns
    r squared < 0 -> model is worse than predicting the mean
    :param returns_df:
    :return:
    """
    y = returns_df['Wheat']
    X = returns_df[['Corn','Oil','Gas','Coal']]
    model = LinearRegression()
    model.fit(X, y)
    print(f'model coefficients: {model.coef_}')
    print(f'model intercept: {model.intercept_}')
    r_square = model.score(X, y)
    y_pred = model.predict(X)
    print(f'r square: {r_square}')
    print(f'predicted values: {y_pred}')
    return r_square, y_pred

if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    # strategy = 'PCA'
    strategy = 'REGRESSION'

    prices_df = pd.read_csv('src/data/commods/commods_prices.csv')
    returns_df = pre_processing(returns_df=compute_returns(prices_df))

    if strategy == 'PCA':
        principal_components = pca(returns_df)
        returns_df = pca_signal(returns_df, principal_components)
    else:
        r_square, y_pred = regression(returns_df)
        returns_df = regression_signal(returns_df, y_pred)
    returns_df = backtest(returns_df)
    metrics(returns_df)
    plot_portfolio_val(returns_df, initial_capital= 100000)
    # print(prices)
    # compute_returns(prices)
    pd.reset_option('display.max_columns')
