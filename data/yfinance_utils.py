import yfinance as yf

def fetch_ticker_hist(ticker, sd:str, ed:str):
    # sd and ed format: 'YYYY-mm-dd'
    return yf.download(ticker, sd, ed)

