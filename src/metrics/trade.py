import pandas as pd
import numpy as np

def calc_trades(trades_df:pd.DataFrame, strategy_id):
    trades_df['trade_id'] = (trades_df['trade'] == 'BUY').cumsum()
    trades_df.loc[trades_df['trade'] == '', 'trade_id'] = np.nan
    print(trades_df.tail(10)[
                ['date', 'long_entry', 'long_exit', 'position', 'position_shrs', 'trade', 'trade_shrs', 'trade_id']])
    print(trades_df[trades_df['trade_id'].notna()].tail(10)[
                ['date', 'long_entry', 'long_exit', 'position', 'position_shrs', 'trade', 'trade_shrs', 'trade_id']])
    trades_df['strategy_id'] = strategy_id
    # display(trades_df[trades_df['trade_id'].isin([1,2,3,4])][['date', 'long_entry', 'long_exit', 'position', 'position_shrs', 'trade', 'trade_shrs', 'trade_id']])
    return trades_df

def calc_trades_metrics(trades_df:pd.DataFrame, ticker:str, strategy_id:str, metrics_dir:str):
    # Count trades: entries/exits
    entries = trades_df[trades_df['trade'] == 'BUY']['trade'].count()
    exits = trades_df[trades_df['trade'] == 'SELL']['trade'].count()
    print(f'entries: {entries}, exits: {exits}')

    # % of profitable trades
    trade_pnl = trades_df.groupby('trade_id')['daily_pnl'].sum().dropna().reset_index()
    print(f'trade_pnl: \n{trade_pnl}')
    profitable = len(trade_pnl[trade_pnl['daily_pnl'] > 0])
    non_profitable = len(trade_pnl[trade_pnl['daily_pnl'] < 0])
    total_trades = len(trade_pnl)
    pct_profitable = round((profitable / total_trades * 100), 2)
    print(f'Profitable Trades: {profitable}')
    print(f'Non-Profitable Trades: {non_profitable}')
    print(f'Total Trades: {total_trades}')
    print(f'% of profitable trades: {pct_profitable}')

    # Average P&L per trade
    avg_pnl_per_trade = round(trade_pnl['daily_pnl'].mean(), 2)
    print(f'Average PnL per Trade: ${avg_pnl_per_trade}')

    # Win rate = #winning trades / total trades
    trades_metrics_df = pd.DataFrame({
        'strategy_id': [strategy_id],
        'entries': [entries],
        'exits': [exits],
        'profitable_trades': [profitable],
        'non_profitable_trades': [non_profitable],
        'total_trades': [total_trades],
        'pct_profitable': [pct_profitable],
        'avg_pnl_per_trade': [avg_pnl_per_trade],
    })
    print(f'\ntrades_metrics_df:\n{trades_metrics_df}')
    trades_metrics_df.to_csv(f'{metrics_dir}/trades_{strategy_id}_{ticker.lower().replace("-", "_")}.csv', index=False)
    return trades_metrics_df

def get_recent_trades(trades_df:pd.DataFrame, ticker:str, strategy_id:str, metrics_dir:str):
    recent_trades_df = trades_df.tail(10)[
        ['strategy_id', 'date', 'long_entry', 'long_exit', 'position', 'position_shrs', 'trade', 'trade_shrs', 'trade_id']]
    print(f'\nrecent_trades_df:\n{recent_trades_df}')
    recent_trades_df.to_csv(f'{metrics_dir}/recent_trades_{strategy_id}_{ticker.lower().replace("-", "_")}.csv', index=False)
    return recent_trades_df