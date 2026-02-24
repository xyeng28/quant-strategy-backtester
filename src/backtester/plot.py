import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import pandas as pd
from src.constants import PROJECT_ROOT


def plot_sma(df: pd.DataFrame, ticker: str, fast_sma_period: int, slow_sma_period: int) -> None:
    print(f'Plotting SMA {fast_sma_period} & {slow_sma_period} for {ticker}')
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['sma_fast'], label='sma fast', color='blue')
    plt.plot(df['date'], df['sma_slow'], label='sma slow', color='grey')
    plt.title(f"{ticker} SMA {fast_sma_period}/{slow_sma_period}")
    plt.legend()
    plt.show()

def plot_macd(macd_df: pd.DataFrame, ticker: str) -> None:
    print(f'Plotting MACD for {ticker}')
    plt.figure(figsize=(12, 6))
    plt.plot(macd_df.index, macd_df['macd'], label='macd', color='blue')
    plt.plot(macd_df.index, macd_df['macd_signal'], label='macd_signal', color='grey')
    plt.bar(macd_df.index, macd_df['macd_histogram'], label='macd_histogram', color='lightblue')
    plt.title(f"{ticker} MACD")
    plt.legend()
    plt.show()

def plot_rsi(df: pd.DataFrame, ticker: str, rsi_period) -> None:
    print(f'Plotting RSI for {ticker} with rsi_period {rsi_period}')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    ax1.plot(df['date'], df['close_px'], label=f'{ticker} Close', color='blue')
    ax1.set_title(f'{ticker} Close Price')
    ax1.legend()
    ax1.grid(True)

    ax2.plot(df['date'], df['rsi'], label='RSI', color='orange')
    ax2.axhline(80, color='red', linestyle='--', label='Overbought (80)')
    ax2.axhline(20, color='purple', linestyle='--', label='Oversold (20)')
    ax2.set_title(f'RSI {rsi_period}')
    ax2.legend()
    ax2.grid(True)

    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()

def plot_equity_curve(df: pd.DataFrame, ticker: str, initial_capital: float) -> None:
    # Cumulative PnL / Equity Curve
    print(f'Plotting Equity Curve for {ticker} with initial capital {initial_capital}')
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['cum_pnl'], label='Equity Curve', color='blue')
    plt.axhline(initial_capital, color='orange', linestyle='--', label='Initial Capital')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value ($)')
    plt.title(f'{ticker} Strategy Equity Curve')
    plt.grid(True)
    plt.gca().yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
    plt.legend()
    plt.show()
    plt.savefig(f'{PROJECT_ROOT}/results/equity/{ticker.lower().replace("-", "_")}_equity_curve.png', dpi=300)

