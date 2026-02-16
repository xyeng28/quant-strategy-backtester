import pandas as pd
import os
import pytz
from data.data_utils import dl_ticker_hist
from src.backtester.strategies import sma_macd_rsi
from src.backtester.portfolio import generate_portfolio
from datetime import datetime as dtt
from src.metrics.performance import calc_metrics
from src.metrics.trade import calc_trades, calc_trades_metrics, get_recent_trades


def backtest_sma_macd_rsi(sd:str, ed:str, ticker:str, strategy_params:dict, execution_params:dict):
    hist_data = dl_ticker_hist(ticker, sd, ed)
    strategy_df = sma_macd_rsi(hist_data, strategy_params)
    df = strategy_df.copy()
    df = generate_portfolio(df, execution_params)

    date_str = dtt.now(pytz.timezone('America/New_York')).strftime('%Y_%m_%d')
    strategy_id = f'sma_macd_rsi_{date_str}'

    metrics_dir = f'results/metrics/{strategy_id}'
    if metrics_dir is not None:
        os.makedirs(metrics_dir, exist_ok=True)

    trades_df = calc_trades(df, strategy_id)
    trade_metrics_df = calc_trades_metrics(df, ticker, strategy_id, metrics_dir)[['strategy_id', 'entries', 'exits', 'profitable_trades',
       'non_profitable_trades', 'total_trades', 'pct_profitable',
       'avg_pnl_per_trade']]
    print(trade_metrics_df)
    get_recent_trades(trades_df, ticker, strategy_id, metrics_dir)

    metrics_df = calc_metrics(df, ticker, strategy_id)
    metrics_df = pd.concat([metrics_df, trade_metrics_df], axis=1)
    print(f'\nmetrics_df: \n{metrics_df}')
    metrics_df.to_csv(f'{metrics_dir}/metrics_{strategy_id}_{ticker.lower().replace("-", "_")}.csv', index=False)

    return metrics_df

