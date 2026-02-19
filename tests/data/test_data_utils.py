import pytest
import os
from unittest.mock import patch, MagicMock
import pandas as pd
from pathlib import Path
from src.data.data_utils import get_tickers, dl_ticker_hist

@patch("pandas.read_csv")
def test_get_tickers(mock_read_csv):
    mock_df = pd.DataFrame({"symbol": ["SPY", "QQQM", "GLD"]})
    mock_read_csv.return_value = mock_df

    tickers = get_tickers()
    assert tickers == ["SPY", "QQQM", "GLD"]
    mock_read_csv.assert_called_once_with('data/tickers.csv')

@patch("src.data.data_utils.fetch_ticker_hist")
def test_dl_ticker_hist(mock_fetch):
    cols = pd.MultiIndex.from_tuples([
        ('Open', 'USD'), ('High', 'USD'), ('Low', 'USD'), ('Close', 'USD'), ('Volume', '')
    ])
    data = [
        [100, 110, 90, 105, 1000],
        [106, 112, 101, 110, 1200]
    ]
    mock_df = pd.DataFrame(data, columns=cols, index=pd.date_range("2023-01-01", periods=2))
    mock_fetch.return_value = mock_df

    ticker = "AAPL"
    sd = "2023-01-01"
    ed = "2023-01-02"

    hist_df = dl_ticker_hist(ticker, sd, ed)

    expected_cols = ['date', 'ticker', 'open_px', 'high_px', 'low_px', 'close_px', 'volume']
    for col in expected_cols:
        assert col in hist_df.columns

    assert (hist_df['ticker'] == ticker).all()
    assert pd.api.types.is_datetime64_any_dtype(hist_df['date'])
    hist_fn = f'{ticker.lower().replace("-", "_")}_hist.csv'
    if Path(hist_fn).exists():
        os.remove(hist_fn)
