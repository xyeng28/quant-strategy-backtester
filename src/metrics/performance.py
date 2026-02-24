import pandas as pd
import numpy as np
import glob
import os
from pandas.io.formats.style import Styler

from src.constants import PROJECT_ROOT

def calc_metrics(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    print(f'Calculating Metrics for ticker {ticker}')
    total_return = round((df['cum_ret'].iloc[-1] - 1) * 100, 2)
    print(f'total_return: {total_return}%')

    sharpe = round((df['daily_ret_c2c'].mean() / df['daily_ret_c2c'].std() * np.sqrt(252)), 2)
    print(f'sharpe: {sharpe}%')

    max_drawdown = round(((df['cum_ret'] / df['cum_ret'].cummax() - 1).min()), 2)
    print(f'max_drawdown: {max_drawdown}%')

    total_pnl = round(df['daily_pnl'].sum(), 2)
    print(f'total_pnl: ${total_pnl}')

    metrics_df = pd.DataFrame({
        'ticker': [ticker],
        'total_return': [total_return],
        'sharpe_ratio': [sharpe],
        'max_drawdown': [max_drawdown],
        'total_pnl': [total_pnl],
    })
    # print(f'\nmetrics_df: \n{metrics_df}')
    return metrics_df

def get_all_metrics_by_strategy(strategy_id:str) -> pd.DataFrame:
    print(f'Retrieving all Metrics by strategy {strategy_id}')
    f_dir = f'{PROJECT_ROOT}/results/metrics/{strategy_id}/'
    files = glob.glob(os.path.join(f_dir, 'metrics_*'))

    dfs = [pd.read_csv(f) for f in files]
    return pd.concat(dfs, ignore_index=True)

def style_metrics_df(df:pd.DataFrame) -> Styler:
    return df.style.format({'total_return': "${:,.2f}",
                          'max_drawdown': '{:.2%}',
                          'total_pnl': '${:,.2f}',
                          'pct_profitable': '{:}%',  # win rate
                          'avg_pnl_per_trade': '${:,.2f}',
                          })
