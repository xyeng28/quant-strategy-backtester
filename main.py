from src.backtester.backtester import backtest_sma_macd_rsi

if __name__ == '__main__':
    start_date = "2022-01-01"
    end_date = "2026-01-29"
    ticker = 'QQQM'
    execution_params = {
        'initial_capital': 100000,
        'allocation': 0.5, # 50% of capital,
        'cost_per_shr': 0.005
    }
    strategy_params = {
        "sma_fast_period": 8,
        "sma_slow_period": 20,
        "macd_fast_period": 12,
        "macd_slow_period": 26,
        "macd_signal_period": 9,
        "rsi_period": 7,
        "lookahead_days": 5
    }
    backtest_sma_macd_rsi(start_date, end_date, ticker, strategy_params, execution_params)
