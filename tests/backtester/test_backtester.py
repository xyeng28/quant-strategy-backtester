import pandas as pd
from src.backtester.backtester import backtest_sma_macd_rsi, compute_all_metrics
from unittest.mock import patch

@patch("os.makedirs")
@patch("pandas.DataFrame.to_csv")
@patch("src.backtester.backtester.calc_trades")
@patch("src.backtester.backtester.calc_trades_metrics")
@patch("src.backtester.backtester.get_recent_trades")
@patch("src.backtester.backtester.calc_metrics")
@patch("src.backtester.backtester.PROJECT_ROOT", "/mock_project")
def test_compute_all_metrics_when_valid_should_return_df(
    mock_calc_metrics,
    mock_get_recent_trades,
    mock_calc_trades_metrics,
    mock_calc_trades,
    mock_to_csv,
    mock_makedirs
):
    df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "long_entry": [True, False],
        "long_exit": [False, True],
        "position": [1, 0],
        "position_shrs": [1, 0],
        "trade_shrs": [1, 0],
        "holding": [1, 0],
        "trade": ["BUY", "SELL"],
        "close_px": [100, 101],
        "daily_ret_c2c": [0.01, 0.02],
        "daily_pnl": [0.0, 0.0],
        "trade_cost": [0.0, 0.0],
        "cum_ret": [0.0, 0.0],
        "avg_pnl_per_trade": [60.5, 60.5],
    })

    ticker = "TEST"
    strategy_id = "strategy_1"
    mock_calc_trades.return_value = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "long_entry": [True, False],
        "long_exit": [False, True],
        "position_shrs": [1, 0],
        "trade_shrs": [1, 0],
        "avg_pnl_per_trade": [60.5, 60.5],
    })

    mock_calc_trades_metrics.return_value = pd.DataFrame({
        "strategy_id": [strategy_id],
        "entries": [1],
        "exits": [0],
        "profitable_trades": [1],
        "non_profitable_trades": [0],
        "total_trades": [1],
        "pct_profitable": [100],
        "position": [0.0],
        "position_shrs": [193.0],
        "avg_pnl_per_trade": [60.5],
    })
    mock_calc_metrics.return_value = pd.DataFrame(
        [['QQQM','sma_macd_rsi_2026_02_15',62.13,0.63,-0.34,19481.02,322,321,181,141,322,56.21,60.5]],
        columns = ['ticker','strategy_id','total_return','sharpe_ratio','max_drawdown','total_pnl','entries','exits','profitable_trades','non_profitable_trades','total_trades','pct_profitable','avg_pnl_per_trade'
    ])

    mock_get_recent_trades.return_value = None
    result = compute_all_metrics(df, ticker, strategy_id)

    mock_makedirs.assert_called_once()
    mock_calc_trades.assert_called_once_with(df, strategy_id)
    mock_calc_trades_metrics.assert_called_once()
    mock_get_recent_trades.assert_called_once()
    mock_calc_metrics.assert_called_once_with(df, ticker)
    mock_to_csv.assert_called_once()

    expected_cols = [
        'ticker','strategy_id','total_return','sharpe_ratio','max_drawdown','total_pnl','entries','exits','profitable_trades','non_profitable_trades','total_trades','pct_profitable','avg_pnl_per_trade'
    ]
    assert all(col in result.columns for col in expected_cols)
    assert isinstance(result, pd.DataFrame)


@patch('src.backtester.backtester.compute_all_metrics')
@patch('src.backtester.backtester.generate_portfolio')
@patch('src.backtester.backtester.sma_macd_rsi')
@patch('src.backtester.backtester.dl_ticker_hist')
def test_backtest_sma_macd_rsi_when_valid_should_return_df(mock_dl, mock_sma, mock_gen_portfolio, mock_metrics):
    sd = "2022-01-01"
    ed = "2026-01-29"
    ticker = 'QQQM'
    execution_params = {
        'initial_capital': 100000,
        'allocation': 0.5,
        'cost_per_shr': 0.005
    }
    strategy_params = {
        "sma_fast_period": 8,
        "sma_slow_period": 20,
        "macd_fast_period": 12,
        "macd_slow_period": 26,
        "macd_signal_period": 9,
        "rsi_period": 7,
        "lookback_days": 5
    }
    mock_hist_data = pd.DataFrame({'close': [100, 101, 102]})
    mock_strategy_df = pd.DataFrame({'signal': [1, 0, -1]})
    mock_portfolio_df = pd.DataFrame({'portfolio_value': [10000, 10100, 10200]})
    mock_metrics_df = pd.DataFrame({'sharpe': [1.5]})

    mock_dl.return_value = mock_hist_data
    mock_sma.return_value = mock_strategy_df
    mock_gen_portfolio.return_value = mock_portfolio_df
    mock_metrics.return_value = mock_metrics_df

    backtest_sma_macd_rsi(sd, ed, ticker, strategy_params, execution_params)  # your function

    mock_dl.assert_called_once_with(ticker, sd, ed)
    mock_sma.assert_called_once()
    call_args = mock_sma.call_args[0]
    pd.testing.assert_frame_equal(call_args[0], mock_hist_data)
    mock_gen_portfolio.assert_called_once()
    call_args = mock_gen_portfolio.call_args[0]
    pd.testing.assert_frame_equal(call_args[0], mock_strategy_df)
    assert call_args[1] == execution_params

    mock_metrics.assert_called_once()
    call_args = mock_metrics.call_args[0]
    assert call_args[1] == ticker
    assert call_args[2].startswith('sma_macd_rsi_')
    assert len(call_args[2]) == len('sma_macd_rsi_2024_01_01')