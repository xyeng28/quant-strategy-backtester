import pandas as pd
import numpy as np
import pytest
from pandas import testing as pdt
from src.backtester.indicators import sma, ema, macd, rsi

def test_sma_when_valid_should_return_sma():
    data = pd.Series([1, 2, 3, 4, 5])
    window = 3

    expected = pd.Series([np.nan, np.nan, 2.0, 3.0, 4.0])
    result = sma(data, window)
    pdt.assert_series_equal(result, expected)

def test_sma_window_larger_than_series_should_return_none():
    data = pd.Series([1, 2])
    window = 5

    expected = pd.Series([np.nan, np.nan])
    result = sma(data, window)
    pdt.assert_series_equal(result, expected)

def test_sma_window_one_should_return_input_series():
    data = pd.Series([10, 20, 30])
    window = 1

    expected = pd.Series([10.0, 20.0, 30.0])
    result = sma(data, window)
    pdt.assert_series_equal(result, expected)

ema_test_data = [
    (3, pd.Series([1.0, 1.5, 2.25, 3.125, 4.0625])),
    (5, pd.Series([1.0, 1.3333, 1.8889, 2.5926, 3.3951])),
]
@pytest.mark.parametrize("span,expected", ema_test_data)
def test_ema_when_valid_should_return_ema(span,expected):
    data = pd.Series([1, 2, 3, 4, 5])

    result = ema(data, span)
    # EMA0 = 1
    # EMA1 = 0.5 * 2 + 0.5 * (2-1) = 1.5
    # EMA2 = 1.5 + 0.5 * (3-1.5) = 2.25
    # EMA3 = 2.25 + 0.5 * (4-2.25) = 3.125
    # EMA4 = 3.125 + 0.5 * (5-3.125) = 4.0625
    # Slow EMA
    # EMA0 = 1
    # EMA1 = 1 + 0.333 * (2-1) = 1.3333
    # EMA2 = 1.3333333 + 0.3333333*(3-1.3333333) = 1.8888889
    # EMA3 = 1.8888889 + 0.3333333*(4-1.8888889) = 2.5925926
    # EMA4 = 2.5925926 + 0.3333333*(5-2.5925926) = 3.3950616
    pdt.assert_series_equal(result, expected, rtol=1e-4, atol=1e-4)

def test_ema_window_one_should_return_series_itself():
    data = pd.Series([10, 20, 30])
    span = 1

    result = ema(data, span)
    expected = pd.Series([10.0, 20.0, 30.0])
    pdt.assert_series_equal(result, expected)

def test_ema_empty_series_should_return_empty():
    data = pd.Series([])
    span = 3

    result = ema(data, span)
    expected = pd.Series([], dtype=float)
    pdt.assert_series_equal(result, expected)

def test_macd_valid_series_should_return_dataframe_with_expected_vals():
    data = pd.Series([1, 2, 3, 4, 5])
    # EMA0   EMA1      MACD      Signal                                              Hist
    # 1      1         0         0                                                   0
    # 1.5    1.333333  0.166667  0.0 + 0.666667*(0.166667-0.0) = 0.111111            0.055556
    # 2.25   1.888889  0.361111  0.111111 + 0.666667*(0.361111-0.111111) = 0.277777  0.083334
    # 3.125  2.592593  0.532407  0.277777 + 0.666667*(0.532407-0.277777) = 0.447531  0.084876
    # 4.0625 3.395062  0.667438  0.447531 + 0.666667*(0.667438-0.447531) = 0.594135  0.073302
    result = macd(data, fast_period=3, slow_period=5, signal_period=2)
    exp = pd.DataFrame({
    'macd': [0.0, 0.166667, 0.361111, 0.532407, 0.667438],
    'macd_signal': [0.0, 0.111111, 0.277777, 0.447531, 0.594135],
    'macd_histogram': [0.0, 0.055556, 0.083334, 0.084876, 0.073302]
    })
    pdt.assert_frame_equal(result, exp, rtol=1e-4, atol=1e-4)

def test_rsi_valid_series_should_return_expected_values():
    data = pd.Series([1, 2, 3, 2, 1, 2, 3])
    exp = pd.Series([np.nan, np.nan, np.nan, 66.6667, 33.3333, 33.3333, 66.6667])
    result = rsi(data, period=3)
    pdt.assert_series_equal(result, exp, rtol=1e-2, atol=1e-2)

