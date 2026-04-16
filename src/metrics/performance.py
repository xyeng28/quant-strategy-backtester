import pandas as pd
import numpy as np
import glob
import os
from pandas.io.formats.style import Styler

from src.constants import PROJECT_ROOT

def calc_metrics(df: pd.DataFrame, ticker: str, initial_capital:float) -> pd.DataFrame:
    print(f'Calculating Metrics for ticker {ticker}')
    total_return = round((df['equity'].iloc[-1] / initial_capital - 1) * 100, 2)
    print(f'total_return: {total_return}%')

    ret = df['strategy_ret'].dropna()
    if len(ret) < 2 or np.isclose(ret.std(), 0):
        sharpe = np.nan
    else:
        sharpe = round((df['strategy_ret'].mean() / df['strategy_ret'].std()) * np.sqrt(252), 2)
    print(f'sharpe: {sharpe}')

    max_drawdown = round(((df['equity'] / df['equity'].cummax() - 1).min()) * 100, 2)
    print(f'max_drawdown: {max_drawdown}%')

    total_pnl = round(df['equity'].iloc[-1] - initial_capital, 2)
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
    df = pd.concat(dfs, ignore_index=True)
    df = df.sort_values(
        by=["sharpe_ratio", "total_return", "max_drawdown"],
        ascending=[False, False, True]
    )
    return df

def style_metrics_df(df:pd.DataFrame) -> Styler:
    return df.style.format({'total_return': "{:.2f}%",
                          'max_drawdown': '{:.2f}%',
                          'total_pnl': '${:,.2f}',
                          'pct_profitable': '{:.2f}%',
                          'avg_pnl_per_trade': '${:,.2f}',
                          })
