from src.backtester.backtester import backtest_sma_macd_rsi

if __name__ == '__main__':
    start_date = "2022-01-01"
    end_date = "2026-01-29"
    ticker = 'QQQM'
    initial_capital = 100000
    allocation = 0.5  # 50% of capital
    cost_per_shr = 0.005
    backtest_sma_macd_rsi(start_date, end_date, ticker, allocation, initial_capital, cost_per_shr)
