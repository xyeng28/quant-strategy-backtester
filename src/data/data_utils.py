import pandas as pd
from src.data.yfinance_utils import fetch_ticker_hist

def get_tickers() -> list:
    tickers = list(pd.read_csv('data/tickers.csv')['symbol'].dropna().unique())
    return tickers

def dl_ticker_hist(ticker, sd:str, ed:str) -> pd.DataFrame:
    raw_hist = fetch_ticker_hist(ticker, sd, ed)
    hist_df = raw_hist.copy()
    px_flds = ['close', 'high', 'low', 'open']
    hist_df.columns = hist_df.columns.droplevel(level=1).str.lower()
    hist_df.columns = [c + '_px' if c in px_flds else c for c in hist_df.columns]
    hist_df.index.name = 'date'
    hist_df = hist_df.reset_index()

    hist_df.insert(loc=1, column='ticker', value=ticker)
    print(hist_df.columns)
    print(hist_df)
    hist_df['date'] = pd.to_datetime(hist_df['date'])
    hist_fn = f'{ticker.lower().replace("-", "_")}_hist.csv'
    hist_df.to_csv(hist_fn, index=False)
    return hist_df


