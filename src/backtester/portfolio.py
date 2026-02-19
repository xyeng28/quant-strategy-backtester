#decides how much capital to allocate
#position size
#dollar exposure
#risk scaling
import pandas as pd
import numpy as np

def calc_pnl(df:pd.DataFrame, initial_capital):
    # position shift 1 as today's return was earned by yesterday's position (entered at yesterday's close)
    # trade executed at close(t), cost incurred on close
    print(f'Calculating Pnl...')
    df['daily_ret_c2c'] = df['close_px'].pct_change()
    df.loc[df.index[0], 'daily_ret_c2c'] = 0
    df['daily_pnl'] = df['daily_ret_c2c'] * df['position'].shift(1) - df['trade_cost']
    df.loc[df.index[0], 'daily_pnl'] = 0
    df['cum_pnl'] = initial_capital + df['daily_pnl'].cumsum()
    return df

def calc_returns(df:pd.DataFrame, initial_capital):
    df['cum_ret'] = (1 + df['daily_ret_c2c']).cumprod()
    df['cum_ret_pct'] = (df['cum_pnl'] / initial_capital - 1) * 100
    print(df[['close_px', 'position', 'daily_ret_c2c', 'cum_ret', 'daily_pnl', 'cum_pnl', 'cum_ret_pct']])
    return df

def calc_posn_and_trades(df:pd.DataFrame, allocation:float, initial_capital:float, cost_per_shr:float):
    df['position'] = df['holding'] * (allocation * initial_capital)
    df.loc[df['trade'] == 'BUY', 'position_shrs'] = df['position'] // df['close_px']  # Can use / for fractional shares
    df['position_shrs'] = df['position_shrs'].replace(0, np.nan).ffill().fillna(0)
    df.loc[df['trade'] == 'SELL', 'position_shrs'] = 0
    # print(df[['date', 'long_entry', 'long_exit', 'holding', 'position', 'position_shrs']])
    # print(df[df['trade'] != ''][['date', 'long_entry', 'long_exit', 'holding', 'position', 'position_shrs', 'trade']])

    df['trade_shrs'] = 0
    df.loc[df['trade'] == 'BUY', 'trade_shrs'] = df['position_shrs']
    df['trade_cost'] = df['trade_shrs'] * cost_per_shr

    # df.loc[df['long_entry']==True,'trade'] = df['position']
    print(df[df['trade'] != ''])
    print(df)
    return df

def generate_portfolio(df:pd.DataFrame, execution_params:dict):
    allocation = execution_params['allocation']
    initial_capital = execution_params['initial_capital']
    cost_per_shr = execution_params['cost_per_shr']
    portfolio_df = df.copy()
    portfolio_df = calc_posn_and_trades(portfolio_df, allocation, initial_capital, cost_per_shr)
    portfolio_df = calc_pnl(portfolio_df, initial_capital)
    portfolio_df = calc_returns(portfolio_df, initial_capital)
    return portfolio_df

