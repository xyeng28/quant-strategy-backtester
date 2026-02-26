## Quant Strategy Backtester
Systematic Backtesting of SMA, MACD and RSI Strategies

## Overview
This project implements and evaluates three classic technical trading strategies on daily data:
- Simple Moving Average (SMA crossover)
- Moving Average Convergence Divergence (MACD)
- Relative Strength Index (RSI)

The goal is to build a backtesting framework for single-asset, long-only systematic strategies with transaction cost modeling.


### This project focuses on:
- Clean signal generation
- Proper execution timing
- Fee modeling
- Performance evaluation
- Strategy comparison

### ⚠️ Work in Progress (WIP)
Planned features:
- Logging
- Pylint & Pep8 reformatting of file
- Docstrings & documentation

## Data
- Daily OHLCV data (focus on close prices)
- Source: yfinance
- Asset: Indexes Eg. SPY, QQQM
- Time period: 4-5 years of historical data from 2022-01-01

No external datasets are redistributed in this repository.


## Backtesting Assumptions

To avoid common biases:
- Signals are generated using information available at time t (close prices)
- Trades are executed at t+1 (next-day execution)
- Long-only (no short selling)
- Full capital allocation when in position
- Fixed transaction fee: Assume 0.005 USD per share for simplicity
- No slippage modeled
- No leverage

## Strategy Definitions
Time Frame: Daily\
RSI(7) - 7 periods\
SMA(8) & SMA(20)\
MACD(12,26,9)

#### Entry Condition
Signal:
- If RSI(7) > 50
- Wait for x candles for either trend conditions to become true (confirmation)

Confirmation:
- SMA(8) > SMA(20) (Bullish crossover) -> Long
- MACD line crosses over the signal line (Uptrend) -> Long


#### Exit Conditions:
x = 5 (holding period)\

Exit condition 1:
- If SMA cross down or MACD cross down happens within x days, then sell position

Exit Condition 2:
- If SMA cross down or MACD cross down does not happen within x days, we exit after x days (holding period).


## Performance Metrics
- Total return
- Sharpe ratio
- Maximum drawdown
- Total PnL
- Number of trades
- Win Rate
- Average gain / loss per trade
- Indicator plots, Equity curves are included in the notebook

### Project Structure
```
.
├── data/
├── strategies/
├── src/
├── backtester/
        ├── backtester.py
        ├── strategies.py
        ├── indicators.py
        ├── portfolio.py
        ├── plots.py
    ├── metrics/
        ├── performance.py
        ├── trade.py
├── notebooks/
└── README.md
```

backtester/ – core simulation engine\
strategies/ – signal generation logic\
metrics/ – performance evaluation\
notebooks/ – research and visualisation

## Key Considerations
- This project is for research and educational purposes.
- No parameter optimisation or walk-forward testing is included in the base implementation.
- Results are sensitive to transaction costs and execution assumptions.

## Future Improvements
- Mean Reversion Strategies

## Disclaimer
- This repository does not constitute financial advice.
- All results are based on historical data and may not reflect future performance.
