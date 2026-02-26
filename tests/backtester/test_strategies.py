import pandas as pd
import pytest
from src.backtester.strategies import confirm_signal_lb, sma_macd_rsi, generate_signals_sma_macd_rsi
from unittest.mock import patch


@pytest.fixture
def strategy_params():
    return {
        "sma_fast_period": 8,
        "sma_slow_period": 20,
        "macd_fast_period": 12,
        "macd_slow_period": 26,
        "macd_signal_period": 9,
        "rsi_period": 7,
        "lookback_days": 5
    }


@pytest.fixture
def mock_rsi():
    return pd.Series([40, 55, 60])


@pytest.fixture
def mock_smas():
    with patch("src.backtester.strategies.sma") as mock_func:
        mock_func.side_effect = [
            pd.Series([False, True, False]),
            pd.Series([False, False, True])
        ]
        yield mock_func


@pytest.fixture
def mock_macd():
    with patch("src.backtester.strategies.macd") as mock_func:
        mock_func.return_value = pd.DataFrame({
            "macd": [0.1, 0.2, 0.3],
            "macd_signal": [0.05, 0.15, 0.25]
        })
        yield mock_func  # yield the mock so test can check call_count, etc.


signal_confirm_test_data = [
    ([False, False, True, False, False], [False, False, True, True, False]),
    ([False, False, False, False, False], [False, False, False, False, False]),
    ([True, True, True, True, True], [True, True, True, True, True]),
]


@pytest.mark.parametrize("input_data,expected_data", signal_confirm_test_data)
def test_confirm_signal_lb_when_signal_should_return_series(input_data, expected_data):
    df = pd.DataFrame({"signal": input_data})
    result = confirm_signal_lb(df, "signal", lookback_days=2)

    expected = pd.Series(expected_data, name="signal")
    pd.testing.assert_series_equal(result, expected)


def test_confirm_signal_when_lookback_gt_input_should_return_series():
    df = pd.DataFrame({"signal": [False, True, False]})
    result = confirm_signal_lb(df, "signal", lookback_days=10)

    expected = pd.Series([False, True, True], name="signal")
    pd.testing.assert_series_equal(result, expected)


def test_confirm_signal_when_min_periods_should_return_series():
    df = pd.DataFrame({"signal": [False, True, False]})
    result = confirm_signal_lb(df, "signal", lookback_days=2)

    expected = pd.Series([False, True, True], name="signal")
    pd.testing.assert_series_equal(result, expected)


@patch("src.backtester.strategies.generate_signals_sma_macd_rsi")
@patch("src.backtester.strategies.confirm_signal_lb")
@patch("src.backtester.strategies.cross_up")
def test_confirm_signal_lb_when_valid_should_return_df(mock_cross_up, mock_confirm,
                                                             mock_generate, strategy_params,
                                                             mock_smas, mock_macd, mock_rsi):
    df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=6),
        "ticker": ["TEST"] * 6,
        "close_px": [10, 11, 12, 11, 13, 14],
        "sma_cross_long": [False, True, False, False, True, False],
        "macd_cross_long": [False, False, True, False, False, True],
        "rsi": [False, True, False, False, True, False],
        "rsi_long_signal": [False, True, False, False, True, False],
    })

    mock_confirm.return_value = pd.Series([False, True, True])
    mock_cross_up.side_effect = [
        pd.Series([False, True, False]),
        pd.Series([False, False, True])
    ]
    mock_generate.side_effect = lambda df, holding_period: df

    sma_macd_rsi_df = sma_macd_rsi(df, strategy_params)

    assert mock_smas.call_count == 2
    assert mock_cross_up.call_count == 2
    mock_macd.assert_called_once()
    mock_confirm.assert_called_once()
    mock_generate.assert_called_once()

    assert "long_entry" in sma_macd_rsi_df.columns
    assert "long_exit" in sma_macd_rsi_df.columns


@pytest.mark.parametrize("long_entry,long_exit,holding_period, exp_holdings, exp_trades, exp_days_in_position", [
    ([True, False, False], [False, False, True], 2, [1, 1, 0], ['BUY', 'HOLD', 'SELL'], [1, 2, 0]),
    ([True, False, False], [False, True, False], 5, [1, 0, 0], ['BUY', 'SELL', ''], [1, 0, 0]),
    ([True, False, False, False], [False, False, False, False], 3, [1, 1, 1, 0], ['BUY', 'HOLD', 'HOLD', 'SELL'],
     [1, 2, 3, 0]),
])
def test_generate_signals_sma_macd_rsi_when_valid_periods_should_return_df(long_entry, long_exit,
                                                                           holding_period, exp_holdings, exp_trades,
                                                                           exp_days_in_position):
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=len(long_entry)),
        "long_entry": long_entry,
        "long_exit": long_exit
    })
    result_df = generate_signals_sma_macd_rsi(df.copy(), holding_period=holding_period)
    assert result_df['holding'].tolist() == exp_holdings
    assert result_df['trade'].tolist() == exp_trades
    assert result_df['days_in_position'].tolist() == exp_days_in_position
