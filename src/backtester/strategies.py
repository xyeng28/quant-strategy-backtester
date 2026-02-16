import pandas as pd
from src.backtester.indicators import sma
from src.backtester.indicators import macd
from src.backtester.indicators import rsi

def confirm_signal(df: pd.DataFrame, signal_col: str, lookahead_days: int) -> pd.Series:
    """Returns a boolean series where True if signal happens within the next lookahead days."""
    return df[signal_col].rolling(lookahead_days, min_periods=1).max().astype(bool)

def generate_signals_sma_macd_rsi(df:pd.DataFrame):
    df['holding'] = 0
    df['days_in_position'] = 0
    df['trade'] = ''

    # Step 3: track holding and days in position
    in_position = False
    days_in_position = 0
    holding_period = 5
    # display(df[df['long_entry']][['date', 'long_entry','long_exit','holding','days_in_position']])

    for i in range(len(df)):
        # Enter if entry signal and currently flat
        if df['long_entry'].iat[i] and not in_position:
            #         print(f'i:{i} Buy Trigger')
            days_in_position = 1
            in_position = True
            # df['holding'].iat[i] = 1
            # df['trade'].iat[i] = 'BUY'
            df.loc[i, 'holding'] = 1
            df.loc[i, 'trade'] = 'BUY'
        # Already holding
        elif in_position and df['long_exit'].iat[i] and days_in_position < holding_period:
            #         print(f'i:{i} Sell Trigger')
            in_position = False
            days_in_position = 0
            df.loc[i, 'holding'] = 0
            df.loc[i, 'trade'] = 'SELL'
        elif in_position and days_in_position == holding_period:
            #         print(f'i:{i} Sell Trigger')
            in_position = False
            days_in_position = 0
            df.loc[i, 'holding'] = 0
            df.loc[i, 'trade'] = 'SELL'
        elif in_position:
            days_in_position += 1
            df.loc[i, 'holding'] = 1
            df.loc[i, 'trade'] = 'HOLD'
        df.loc[i, 'days_in_position'] = days_in_position
        # df['days_in_position'].iat[i] = days_in_position
    #     print(f'i:{i}, in_position:{in_position}, days_in_position:{row["days_in_position"]}')

    # display(df[['date', 'long_entry','long_exit','holding','days_in_position']])
    print(
        df[df['days_in_position'] >= 1][['date', 'long_entry', 'long_exit', 'holding', 'days_in_position', 'trade']])
    return df

def sma_macd_rsi(df:pd.DataFrame, strategy_params:dict):
    close_px = df['close_px']
    df[f'sma_fast'] = sma(close_px, strategy_params['sma_fast_period'])
    df[f'sma_slow'] = sma(close_px, strategy_params['sma_slow_period'])
    print(df)
    macd_df = macd(close_px, fast_period=strategy_params['macd_fast_period'], slow_period=strategy_params['macd_slow_period'], signal_period=strategy_params['macd_signal_period'])
    print(f'macd_df:{macd_df}')
    df = pd.concat([df, macd_df], axis=1)
    print(df)
    df['rsi'] = rsi(df['close_px'], strategy_params['rsi_period'])
    print(df)

    df['sma_cross_long'] = df['sma_fast'] > df['sma_slow']
    df['rsi_long_signal'] = df['rsi'] > 50
    df['macd_cross_long'] = (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))

    # df['sma_cross_long_entry'] = df['sma_cross_long'].rolling(strategy_params['lookahead_days'], min_periods=1).max().astype(bool)
    # df['macd_cross_long_entry'] = df['macd_cross_long'].rolling(strategy_params['lookahead_days'], min_periods=1).max().astype(bool)
    df['sma_cross_long_entry'] = confirm_signal(df, 'sma_cross_long', strategy_params['lookahead_days'])
    df['macd_cross_long_entry'] = confirm_signal(df, 'macd_cross_long', strategy_params['lookahead_days'])
    df['long_entry'] = df['rsi_long_signal'] & (df['sma_cross_long_entry'] | df['macd_cross_long_entry'])

    # display(df[df['macd_cross_long_entry']==True])
    df['long_entry'] = df['rsi_long_signal'] & (df['sma_cross_long_entry'] | df['macd_cross_long_entry'])
    # display(df)
    print(df.columns)

    entry_df = df.copy()
    entry_df = entry_df[entry_df['long_entry'] == True]
    print(
        entry_df[['date', 'ticker', 'close_px', 'rsi_long_signal', 'sma_cross_long', 'macd_cross_long', 'long_entry']])
    # print(f'entry_dates:{entry_df["date"].unique().tolist()}')

    df['long_exit'] = (df['sma_cross_long'] == False) | (df['macd_cross_long'] == False)
    # df = df.drop('sma_cross_short',axis=1)
    # display(df)

    exit_df = df.copy()
    exit_df = exit_df[exit_df['long_exit'] == True]
    print(
        exit_df[['date', 'ticker', 'close_px', 'rsi_long_signal', 'sma_cross_long', 'macd_cross_long', 'long_exit']])
    df = generate_signals_sma_macd_rsi(df)
    return df










