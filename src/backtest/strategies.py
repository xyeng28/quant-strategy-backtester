import numpy as np
import pandas as pd
from src.backtest.indicators import sma
from src.backtest.indicators import macd
from src.backtest.indicators import rsi
from src.statistics.statistics import compute_z_score


def cross_up(series_fast: pd.Series, series_slow: pd.Series) -> pd.Series:
    return (series_fast > series_slow) & (series_fast.shift(1) <= series_slow.shift(1))


def confirm_signal_lb(df: pd.DataFrame, signal_col: str, lookback_days: int = 5) -> pd.Series:
    """Returns a boolean series where True if signal happened within the previous lookback days."""
    return df[signal_col].rolling(lookback_days, min_periods=1).max().astype(bool)


def generate_signals_sma_macd_rsi(df: pd.DataFrame, holding_period: int = 5):
    """
    Generates holding, trades and days in position
    :param df:
    :param holding_period:
    :return:
    """
    in_position = False
    days_in_position = 0
    holdings = [0] * len(df)
    trades = [''] * len(df)
    days_in_posn_list = [0] * len(df)

    for i in range(len(df)):
        # Enter if entry signal and currently flat
        if df['entry'].iat[i] and not in_position:
            days_in_position = 1
            in_position = True
            holdings[i] = 1
            trades[i] = 'BUY'
        # To exit upon exit signal
        elif in_position and df['exit'].iat[i] and days_in_position < holding_period:
            in_position = False
            days_in_position = 0
            holdings[i] = 0
            trades[i] = 'SELL'
        # To sell days_in_position reaches holding period
        elif in_position and days_in_position == holding_period:
            in_position = False
            days_in_position = 0
            holdings[i] = 0
            trades[i] = 'SELL'
        # To hold
        elif in_position:
            days_in_position += 1
            holdings[i] = 1
            trades[i] = 'HOLD'
        days_in_posn_list[i] = days_in_position
    #     print(f'i:{i}, in_position:{in_position}, days_in_position:{row["days_in_position"]}')
    df['holding'] = holdings
    df['trade'] = trades
    df['days_in_position'] = days_in_posn_list
    # print(df[['date', 'entry','exit','holding','days_in_position']])
    return df


def sma_macd_rsi(df: pd.DataFrame, strategy_params: dict) -> pd.DataFrame:
    close_px = df['close_px']
    df[f'sma_fast'] = sma(close_px, strategy_params['sma_fast_period'])
    df[f'sma_slow'] = sma(close_px, strategy_params['sma_slow_period'])

    macd_df = macd(close_px, fast_period=strategy_params['macd_fast_period'],
                   slow_period=strategy_params['macd_slow_period'], signal_period=strategy_params['macd_signal_period'])
    print(f'macd_df:{macd_df}')
    df = pd.concat([df, macd_df], axis=1)
    df['rsi'] = rsi(df['close_px'], strategy_params['rsi_period'])

    df['sma_cross_long'] = cross_up(df['sma_fast'], df['sma_slow'])
    df['macd_cross_long'] = cross_up(df['macd'], df['macd_signal'])
    df['rsi_long_signal'] = df['rsi'] > 50 & (df['rsi'].shift(1) <= 50)

    df['rsi_recent'] = confirm_signal_lb(df, 'rsi_long_signal', strategy_params['lookback_days'])
    df['entry'] = df['rsi_recent'] & (df['sma_cross_long'] | df['macd_cross_long'])
    df['exit'] = (df['sma_cross_long'] == False) | (df['macd_cross_long'] == False)

    print(df.columns)
    print(df)
    df = generate_signals_sma_macd_rsi(df, holding_period=5)
    return df

def pca_signal(residuals: np.ndarray, index: pd.Index, cols: list) -> pd.DataFrame:
    signal = -compute_z_score(residuals)
    print(f'signal:{signal}')
    signal_df = pd.DataFrame(signal, index=index, columns=cols)
    # print(f'signal_df:{signal_df}')
    # print(f'signal_df:{type(signal_df)}')
    return signal_df

def pca_strategy(residuals: np.ndarray, index: pd.Index, cols: list) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    signal positive -> buy pressure
    signal negative -> sell pressure
    upper = 1 (long underpriced) and lower = -1 (short overpriced) means trade when signal is +-1 std dev away from the mean
     #
    :param residuals:
    :param index:
    :param cols:
    :return:
    """
    print(f'index:{index}')
    print(f'cols:{cols}')
    signal_df = pca_signal(residuals, index, cols)
    weights_df = signal_df.div(signal_df.abs().sum(axis=1), axis=0)

    upper = 1.0
    lower = -1.0
    holding_df = pd.DataFrame(
        np.where(signal_df < lower, 1,
                 np.where(signal_df > upper, -1, 0)),
        index=signal_df.index,
        columns=signal_df.columns
    )

    trade_df = pd.DataFrame("", index=holding_df.index, columns=holding_df.columns)
    trade_df[holding_df.diff() > 0] = "BUY"
    trade_df[holding_df.diff() < 0] = "SELL"
    return signal_df, holding_df, weights_df, trade_df

def regression_signal(returns_df: pd.DataFrame, y_pred) -> pd.DataFrame:
    """
    y_pred is the predicted returns of the y. Eg. Wheat. If pred return > 0 -> expect price to go up.
    If pred return < 0 -> expect price to go down.
    :param returns_df:
    :param principal_components:
    :return:
    """
    returns_df['y_pred'] = y_pred
    returns_df['signal'] = 0
    returns_df.loc[returns_df['y_pred'] > 0, 'signal'] = 1
    returns_df.loc[returns_df['y_pred'] > 0, 'side'] = 'LONG'
    returns_df.loc[returns_df['y_pred'] < 0, 'signal'] = -1
    returns_df.loc[returns_df['y_pred'] < 0, 'side'] = 'SHORT'
    return returns_df



