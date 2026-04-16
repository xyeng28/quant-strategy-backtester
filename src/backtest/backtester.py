import pandas as pd
import os
import pytz
from datetime import datetime as dtt

from src.backtest.models.pca import fit_pca
from src.constants import PROJECT_ROOT
from src.data.data_utils import dl_ticker_hist
from src.backtest.strategies import sma_macd_rsi, pca_strategy
from src.backtest.portfolio import generate_portfolio, convert_multi_to_single_asset
from src.data.preprocessing import compute_returns, scale_data
from src.metrics.performance import calc_metrics
from src.metrics.trade import calc_trades, calc_trades_metrics, get_recent_trades


def compute_all_metrics(df: pd.DataFrame, strategy_id: str, initial_capital: float, ticker: str='') -> pd.DataFrame:
    """
    Run all metric calculations
    """
    metrics_dir = f'{PROJECT_ROOT}/results/metrics/{strategy_id}'
    if metrics_dir is not None:
        os.makedirs(metrics_dir, exist_ok=True)

    trades_df = calc_trades(df, strategy_id)
    trade_cols = ['strategy_id', 'entries', 'exits', 'profitable_trades',
                  'non_profitable_trades', 'total_trades', 'pct_profitable',
                  'avg_pnl_per_trade']
    trade_metrics_df = calc_trades_metrics(trades_df, ticker, strategy_id, metrics_dir)[trade_cols]
    print(trade_metrics_df)
    get_recent_trades(trades_df, ticker, strategy_id, metrics_dir)

    metrics_df = calc_metrics(df, ticker, initial_capital=initial_capital)
    metrics_df = pd.concat([metrics_df, trade_metrics_df], axis=1)
    print(f'\nmetrics_df: \n{metrics_df}')
    metrics_df.to_csv(f'{metrics_dir}/metrics_{strategy_id}_{ticker.lower().replace("-", "_")}.csv', index=False)
    return metrics_df


def backtest_sma_macd_rsi(sd: str, ed: str, ticker: str, strategy_params: dict, execution_params: dict) -> pd.DataFrame:
    print(f'Running SMA MACD RSI backtest for ticker {ticker} from {sd} to {ed}')
    hist_data = dl_ticker_hist(ticker, sd, ed)
    strategy_df = sma_macd_rsi(hist_data, strategy_params)
    df = strategy_df.copy()
    df = generate_portfolio(df, execution_params)

    date_str = dtt.now(pytz.timezone('America/New_York')).strftime('%Y_%m_%d')
    strategy_id = f'sma_macd_rsi_{date_str}'
    metrics_df = compute_all_metrics(df, strategy_id, execution_params['initial_capital'], ticker=ticker)
    return metrics_df

def backtest_pca(execution_params: dict):
    prices_df = pd.read_csv(f'{PROJECT_ROOT}/src/data/hist/commods/commods_prices.csv')
    cols = ['wheat', 'corn', 'oil', 'gas', 'coal']
    returns_df = compute_returns(prices_df, cols)
    returns_df = returns_df.set_index('date')

    pca_df = returns_df.copy()
    pca_df = pca_df[cols]
    scaled_X, scaler = scale_data(pca_df)

    pca, principal_components, residuals = fit_pca(scaled_X, n_components=2)
    signal_df, holding_df, weights_df, trade_df = pca_strategy(residuals, returns_df.index, cols)

    cols = pd.MultiIndex.from_product(
        [["signal", "holding", "weights", "trade"], returns_df.columns]
    )
    df = pd.DataFrame(index=returns_df.index, columns=cols)
    df['signal'] = signal_df
    df['holding'] = holding_df
    df['weights'] = weights_df
    df['trade'] = trade_df

    portfolio_df = convert_multi_to_single_asset(holding_df, trade_df, prices_df)
    portfolio_df = generate_portfolio(portfolio_df, execution_params)
    date_str = dtt.now(pytz.timezone('America/New_York')).strftime('%Y_%m_%d')
    strategy_id = f'pca_{date_str}'
    metrics_df = compute_all_metrics(portfolio_df, strategy_id, execution_params['initial_capital'])
    return metrics_df
