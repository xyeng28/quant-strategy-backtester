import pandas as pd
import numpy as np
from src.metrics.trade import calc_trades, calc_trades_metrics, get_recent_trades
import pandas.testing as pdt
from unittest.mock import patch

def test_calc_trades_when_valid_should_return_df():
    df = pd.DataFrame(
        {'trade': ['BUY', 'HOLD', 'BUY']}
    )
    strategy_id = 'test_strategy'
    trades_df = calc_trades(df, strategy_id)
    exp_trades_df = pd.DataFrame({
        'trade': ['BUY', 'HOLD', 'BUY'],
        'trade_id': [1,1,2],
        'strategy_id': [strategy_id, strategy_id, strategy_id],
    })
    exp_trades_df['trade_id'] = exp_trades_df['trade_id'].astype("Int64")

    pdt.assert_frame_equal(exp_trades_df, trades_df)

def test_calc_trades_metrics_when_valid_should_return_df():
    df = pd.DataFrame({
        'trade': ['BUY', 'HOLD', 'SELL', 'BUY', 'SELL', 'BUY'],
        'trade_id': [1,1,1,2,2,3],
        'daily_pnl': [0, 5, 8, -1, 3, -2],
    })

    metrics_dir = 'test/test_metrics/'
    strategy_id = "test_strategy"
    ticker = "AAPL"
    entries = 3
    exits = 2
    profitable = 2
    non_profitable = 1
    total_trades = 3
    pct_profitable = 66.67
    avg_pnl_per_trade = 4.33
    expected_df = pd.DataFrame({
        'strategy_id': [strategy_id],
        'entries': [entries],
        'exits': [exits],
        'profitable_trades': [profitable],
        'non_profitable_trades': [non_profitable],
        'total_trades': [total_trades],
        'pct_profitable': [pct_profitable],
        'avg_pnl_per_trade': [avg_pnl_per_trade],
    })

    with patch("pandas.DataFrame.to_csv") as mock_to_csv:
        result_df = calc_trades_metrics(df, ticker, strategy_id, metrics_dir)
        mock_to_csv.assert_called_once()
    pdt.assert_frame_equal(result_df, expected_df)

def test_get_recent_trades_when_valid_should_return_df():
    data = [['sma_macd_rsi_2026_02_19', pd.Timestamp('1990-01-03 00:00:00'), False, True, 0.0, 0.0, '', 0, np.nan, 100000.0, 1.0], ['sma_macd_rsi_2026_02_19', pd.Timestamp('1990-01-04 00:00:00'), False, True, 0.0, 0.0, '', 0, np.nan, 100000.0, 1.0073665150577769], ['sma_macd_rsi_2026_02_19', pd.Timestamp('1990-01-05 00:00:00'), False, True, 0.0, 0.0, '', 0, np.nan, 100000.0, 1.0043366941103686], ['sma_macd_rsi_2026_02_19', pd.Timestamp('1990-01-06 00:00:00'), False, True, 0.0, 0.0, '', 0, np.nan, 100000.0, 0.9920394681677988], ['sma_macd_rsi_2026_02_19', pd.Timestamp('1990-01-07 00:00:00'), False, True, 0.0, 0.0, '', 0, np.nan, 100000.0, 0.9965543763753013], ['sma_macd_rsi_2026_02_19', pd.Timestamp('1990-01-10 00:00:00'), False, True, 0.0, 0.0, '', 0, np.nan, 100000.0, 0.9995841066746439], ['sma_macd_rsi_2026_02_19', pd.Timestamp('1990-01-11 00:00:00'), False, True, 0.0, 0.0, '', 0, np.nan, 100000.0, 1.0116437440370571], ['sma_macd_rsi_2026_02_19', pd.Timestamp('1990-01-12 00:00:00'), True, True, 50000.0, 292.0, 'BUY', 292, 1.0, 99998.54, 1.0143171367901975], ['sma_macd_rsi_2026_02_19', pd.Timestamp('1990-01-13 00:00:00'), True, True, 0.0, 0.0, 'SELL', 0, 1.0, 99828.69057619934, 1.0108715131654986], ['sma_macd_rsi_2026_02_19', pd.Timestamp('1990-01-14 00:00:00'), True, True, 50000.0, 294.0, 'BUY', 294, 2.0, 99827.22057619934, 1.0079605318322016], ['sma_macd_rsi_2026_02_19', pd.Timestamp('1990-01-18 00:00:00'), True, True, 0.0, 0.0, 'SELL', 0, 2.0, 99744.70782134622, 1.0062971398269078], ['sma_macd_rsi_2026_02_19', pd.Timestamp('1990-01-19 00:00:00'), True, True, 50000.0, 290.0, 'BUY', 290, 3.0, 99743.25782134623, 1.0222776686223989]]
    cols = ['strategy_id', 'date', 'long_entry', 'long_exit', 'position', 'position_shrs', 'trade', 'trade_shrs', 'trade_id', 'cum_pnl', 'cum_ret']
    trades_df = pd.DataFrame(
        data, columns=cols
    )

    metrics_dir = 'test/test_metrics/'
    strategy_id = "test_strategy"
    ticker = "AAPL"
    expected_df = trades_df.tail(10).iloc[-10:][
        ['strategy_id', 'date', 'long_entry', 'long_exit',
         'position', 'position_shrs', 'trade', 'trade_shrs', 'trade_id']
    ]

    with patch("pandas.DataFrame.to_csv") as mock_to_csv:
        result_df = get_recent_trades(trades_df, ticker, strategy_id, metrics_dir)
        mock_to_csv.assert_called_once()
    pdt.assert_frame_equal(result_df, expected_df)



