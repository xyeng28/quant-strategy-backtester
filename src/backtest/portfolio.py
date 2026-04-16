#decides how much capital to allocate
#position size
#dollar exposure
#risk scaling
import pandas as pd
import numpy as np


def calc_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Position is shifted by 1 so that today's return is earned by yesterday's position.
    Trades are executed at next day's open, with transaction costs applied at entry.
    :param df:
    :param initial_capital:
    :return:
    """
    print(f'Calculating Returns...')
    df['daily_ret_o2c'] = (df['close_px'] - df['open_px']) / df['open_px']
    df.loc[df.index[0], 'daily_ret_o2c'] = 0
    df['daily_pnl'] = df['position_shrs'].shift(1) * (df['close_px'] - df['open_px']) - df['trade_cost']
    df.loc[df.index[0], 'daily_pnl'] = 0
    return df


def calc_pnl(df: pd.DataFrame, initial_capital: float) -> pd.DataFrame:
    """
    Equity is the total value of trading acct over time = starting capital + accumulated pnl
    :param df:
    :param initial_capital:
    :return:
    """
    print(f'Calculating Pnl...')
    df['strategy_ret'] = df['daily_pnl'] / initial_capital
    df.loc[df.index[0], 'strategy_ret'] = 0
    df['equity'] = initial_capital + df['daily_pnl'].cumsum()
    df['cum_pnl'] = df['equity'] - initial_capital
    df['cum_ret_pct'] = (df['equity'] / initial_capital - 1) * 100

    df['cum_ret'] = (1 + df['strategy_ret']).cumprod()
    df['port_val'] = df['cum_ret'] * initial_capital
    df['dd'] = df['cum_ret'] / df['cum_ret'].cummax() - 1
    # print(df[['close_px', 'position', 'daily_ret_o2c', 'cum_ret', 'daily_pnl', 'cum_pnl', 'cum_ret_pct']])
    return df


def calc_posn_and_trades(df: pd.DataFrame, allocation: float, initial_capital: float, cost_per_shr: float) -> pd.DataFrame:
    # Can use / for fractional shares
    print(f'Calculating Positions and Trades...')
    df['position'] = df['holding'] * (allocation * initial_capital)
    df['position_shrs'] = np.nan
    df.loc[df['trade'] == 'BUY', 'position_shrs'] = df['position'] // df['close_px']
    df.loc[df['holding'] == 0, 'position_shrs'] = 0
    df['position_shrs'] = df['position_shrs'].ffill().fillna(0)
    df.loc[df['trade'] == 'SELL', 'position_shrs'] = 0
    # print(df[['trade', 'holding', 'position', 'position_shrs']].head(30))
    # print(df[['trade', 'holding', 'position', 'position_shrs']].value_counts())

    df['trade_shrs'] = 0
    df.loc[df['trade'] == 'BUY', 'trade_shrs'] = df['position_shrs']
    df['trade_cost'] = df['trade_shrs'] * cost_per_shr
    # print(df[df['trade'] != ''])
    # print(df)
    return df


def generate_portfolio(df: pd.DataFrame, execution_params: dict) -> pd.DataFrame:
    allocation = execution_params['allocation']
    initial_capital = execution_params['initial_capital']
    cost_per_shr = execution_params['cost_per_shr']
    portfolio_df = df.copy()
    portfolio_df = calc_posn_and_trades(portfolio_df, allocation, initial_capital, cost_per_shr)
    portfolio_df = calc_returns(portfolio_df)
    portfolio_df = calc_pnl(portfolio_df, initial_capital)
    return portfolio_df
