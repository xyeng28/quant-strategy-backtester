import pandas as pd
import numpy as np
import matplotlib.dates as mdates
from src.backtester.plot import plot_sma, plot_macd, plot_rsi, plot_equity_curve
from unittest.mock import patch
from matplotlib import pyplot as plt

def test_plot_sma_when_valid_should_run_with_lines():
    df = pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=5),
        'sma_fast': [1, 2, 3, 4, 5],
        'sma_slow': [1.5, 2.5, 3.5, 4.5, 5.5],
    })
    ticker = "AAPL"
    fast_period = 3
    slow_period = 5

    fig, ax = plt.subplots()
    with patch('matplotlib.pyplot.show') as mock_show:
        plt.figure = lambda *args, **kwargs: fig
        plot_sma(df, ticker, fast_period, slow_period)
    lines = ax.get_lines()
    assert len(lines) == 2
    labels = [line.get_label() for line in lines]
    assert "sma fast" in labels
    assert "sma slow" in labels
    mock_show.assert_called_once()

def test_plot_macd_when_valid_should_run_with_lines_and_bar():
    macd_df = pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=5),
        'macd': [0.1, 0.2, 0.3, 0.2, 0.1],
        'macd_signal': [0.05, 0.15, 0.25, 0.15, 0.05],
        'macd_histogram': [0.05, 0.05, 0.05, 0.05, 0.05]
    })
    ticker = "AAPL"

    with patch('matplotlib.pyplot.show') as mock_show:
        fig, ax = plt.subplots()
        original_figure = plt.figure
        plt.figure = lambda *args, **kwargs: fig

        plot_macd(macd_df, ticker)

        ax = plt.gca()
        line_labels = [line.get_label() for line in ax.get_lines()]
        assert "macd" in line_labels
        assert "macd_signal" in line_labels

        bar_containers = [c for c in ax.containers if hasattr(c, 'get_label')]
        bar_labels = [c.get_label() for c in bar_containers]
        assert "macd_histogram" in bar_labels
        mock_show.assert_called_once()
        plt.figure = original_figure

def test_plot_rsi_when_valid_should_run_with_lines():
    df = pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=5),
        'close_px': [100, 102, 101, 103, 104],
        'rsi': [np.nan, 100, 50, 0, 33.33]
    })
    ticker = "AAPL"
    rsi_period = 3

    with patch('matplotlib.pyplot.show') as mock_show:
        plot_rsi(df, ticker, rsi_period=rsi_period)
        fig = plt.gcf()
        ax1, ax2 = fig.axes

        lines_ax1 = ax1.get_lines()
        labels_ax1 = [line.get_label() for line in lines_ax1]
        assert f"{ticker} Close" in labels_ax1
        assert ax1.get_title() == f"{ticker} Close Price"

        lines_ax2 = ax2.get_lines()
        labels_ax2 = [line.get_label() for line in lines_ax2]
        assert "RSI" in labels_ax2
        assert "Overbought (80)" in labels_ax2
        assert "Oversold (20)" in labels_ax2
        assert ax2.get_title() == f"RSI {rsi_period}"

        assert isinstance(ax2.xaxis.get_major_locator(), mdates.MonthLocator)
        assert isinstance(ax2.xaxis.get_major_formatter(), mdates.DateFormatter)
        mock_show.assert_called_once()

def test_plot_equity_curve_when_valid_should_run_with_lines():
    df = pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=7),
        'cum_pnl': [0, 100, 150, 120, 180, 220, 200]
    })
    ticker = "AAPL"
    initial_capital = 100

    fig, ax = plt.subplots()
    with (patch('matplotlib.pyplot.show') as mock_show,
          patch('matplotlib.pyplot.savefig') as mock_savefig):
        plt.figure = lambda *args, **kwargs: fig
        plot_equity_curve(df, ticker, initial_capital)
    lines = ax.get_lines()
    assert len(lines) == 2
    labels = [line.get_label() for line in lines]
    assert "Equity Curve" in labels
    assert "Initial Capital" in labels
    assert ax.get_title() == 'AAPL Strategy Equity Curve'
    mock_show.assert_called_once()
    mock_savefig.assert_called_once()

