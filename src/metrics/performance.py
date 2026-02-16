import pandas as pd
import numpy as np
import glob
import os

def calc_metrics(df:pd.DataFrame, ticker:str, strategy_id:str):
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
        'strategy_id': [strategy_id],
        'total_return': [total_return],
        'sharpe_ratio': [sharpe],
        'max_drawdown': [max_drawdown],
        'total_pnl': [total_pnl],
    })

    # print(f'\nmetrics_df: \n{metrics_df}')
    # metrics_df.to_csv(f'metrics/strategy_id/metrics_{strategy_id}_{ticker.lower().replace("-","_")}', index=False)
    return metrics_df

def get_all_metrics_by_strategy(strategy_id:str):
    f_dir = f'results/metrics/{strategy_id}/'
    files = glob.glob(os.path.join(f_dir, 'metrics_*'))

    dfs = [pd.read_csv(f) for f in files]
    all_metrics_df = pd.concat(dfs, ignore_index=True)
    all_metrics_df = all_metrics_df.style.format({'total_return': "${:,.2f}",
                                          'max_drawdown': '{:.2%}',
                                          'total_pnl': '${:,.2f}',
                                          'pct_profitable': '{:}%',  # win rate
                                          'avg_pnl_per_trade': '${:,.2f}',
                                          })
    return all_metrics_df
