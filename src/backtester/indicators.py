import pandas as pd

def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window).mean()

def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def macd(series: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> pd.DataFrame:
    ema_fast = ema(series, fast_period)
    ema_slow = ema(series, slow_period)
    print(f'ema_fast:\n{ema_fast}')
    print(f'ema_slow:\n{ema_slow}')
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal_period)
    histogram = macd_line - signal_line
    return pd.DataFrame({
        'macd':macd_line,
        'macd_signal':signal_line,
        'macd_histogram':histogram
    }, index=series.index)

def rsi(series: pd.Series, period: int = 7) -> pd.DataFrame:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    # print(rs)
    return 100 - (100/(1+rs))








