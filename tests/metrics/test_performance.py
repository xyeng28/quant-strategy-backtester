import pandas as pd
import numpy as np
from pandas.io.formats.style import Styler
from unittest.mock import patch
import pandas.testing as pdt
from src.metrics.performance import calc_metrics, get_all_metrics_by_strategy, style_metrics_df

def test_calc_metrics_when_valid_should_return_df():
    df = pd.DataFrame(
        {'date': {0: pd.Timestamp('1990-01-03 00:00:00'), 1: pd.Timestamp('1990-01-04 00:00:00'), 2: pd.Timestamp('1990-01-05 00:00:00')}, 'ticker': {0: 'GLD', 1: 'GLD', 2: 'GLD'}, 'close_px': {0: 168.3300018310547, 1: 169.57000732421875, 2: 169.05999755859375}, 'high_px': {0: 169.00999450683594, 1: 169.72000122070312, 2: 170.92999267578125}, 'low_px': {0: 168.0, 1: 168.72999572753906, 2: 168.89999389648438}, 'open_px': {0: 168.86000061035156, 1: 168.89999389648438, 2: 170.6199951171875}, 'volume': {0: 9014400, 1: 6965600, 2: 8715600}, 'sma_fast': {0: np.nan, 1: np.nan, 2: np.nan}, 'sma_slow': {0: np.nan, 1: np.nan, 2: np.nan}, 'macd': {0: 0.0, 1: 0.09891781711851877, 2: 0.13460572310603425}, 'macd_signal': {0: 0.0, 1: 0.019783563423703757, 2: 0.042747995360169856}, 'macd_histogram': {0: 0.0, 1: 0.07913425369481501, 2: 0.0918577277458644}, 'rsi': {0: np.nan, 1: np.nan, 2: np.nan}, 'sma_cross_long': {0: False, 1: False, 2: False}, 'rsi_long_signal': {0: False, 1: False, 2: False}, 'macd_cross_long': {0: False, 1: True, 2: False}, 'rsi_recent': {0: False, 1: False, 2: False}, 'long_entry': {0: False, 1: False, 2: False}, 'long_exit': {0: True, 1: True, 2: True}, 'holding': {0: 0, 1: 0, 2: 0}, 'trade': {0: '', 1: '', 2: ''}, 'days_in_position': {0: 0, 1: 0, 2: 0}, 'position': {0: 0.0, 1: 0.0, 2: 0.0}, 'position_shrs': {0: 0.0, 1: 0.0, 2: 0.0}, 'trade_shrs': {0: 0, 1: 0, 2: 0}, 'trade_cost': {0: 0.0, 1: 0.0, 2: 0.0}, 'daily_ret_c2c': {0: 0.0, 1: 0.07366515057776857, 2: -0.0300766493835114}, 'daily_pnl': {0: 0.0, 1: 3.0, 2: -2.2}, 'cum_pnl': {0: 100000.0, 1: 100000.0, 2: 100000.0}, 'cum_ret': {0: 1.0, 1: 1.073665150577769, 2: 1.043366941103686}, 'cum_ret_pct': {0: 0.0, 1: 0.0, 2: 0.0}, 'trade_id': {0: np.nan, 1: np.nan, 2: np.nan}, 'strategy_id': {0: 'sma_macd_rsi_2026_02_19', 1: 'sma_macd_rsi_2026_02_19', 2: 'sma_macd_rsi_2026_02_19'}}
    )
    exp_df = pd.DataFrame({
        'ticker': ['GLD'],
        "total_return": [4.34],
        "sharpe_ratio": [4.32], #mean/std * 252 due to annualised = 0.00145295/0.005336 * 252
        "max_drawdown": [-0.03],
        "total_pnl": [0.8]
    })
    metrics_df = calc_metrics(df, 'GLD')
    pdt.assert_frame_equal(exp_df, metrics_df)


@patch("src.metrics.performance.pd.read_csv")
@patch("src.metrics.performance.glob.glob")
def test_get_all_metrics_by_strategy_when_valid_should_return_df(mock_glob, mock_read_csv):
    mock_glob.return_value = ["file1.csv", "file2.csv"]

    df1 = pd.DataFrame({
        "total_return": [1000],
        "max_drawdown": [0.1],
        "total_pnl": [500],
        "pct_profitable": [60],
        "avg_pnl_per_trade": [50]
    })
    df2 = pd.DataFrame({
        "total_return": [2000],
        "max_drawdown": [0.05],
        "total_pnl": [1000],
        "pct_profitable": [70],
        "avg_pnl_per_trade": [100]
    })
    mock_read_csv.side_effect = [df1, df2]

    exp_df = pd.DataFrame({
        "total_return": [1000, 2000],
        "max_drawdown": [0.1, 0.05],
        "total_pnl": [500, 1000],
        "pct_profitable": [60, 70],
        "avg_pnl_per_trade": [50, 100]
    })
    strategy_id = "test_strategy"

    combined_df = get_all_metrics_by_strategy(strategy_id)
    print(combined_df)
    assert mock_read_csv.call_count == 2
    mock_read_csv.assert_any_call("file1.csv")
    mock_read_csv.assert_any_call("file2.csv")

    pdt.assert_frame_equal(exp_df, combined_df)

def test_style_metrics_df_when_valid_should_return_styler():
    df = pd.DataFrame({
        "total_return": [1000],
        "max_drawdown": [0.1],
        "total_pnl": [500],
        "pct_profitable": [60],
        "avg_pnl_per_trade": [50]
    })

    styled = style_metrics_df(df)
    assert isinstance(styled, Styler)
    pdt.assert_frame_equal(styled.data, df)
