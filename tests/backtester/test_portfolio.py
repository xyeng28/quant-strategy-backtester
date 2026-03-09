from unittest.mock import patch
import pandas as pd
from src.backtest.portfolio import calc_pnl, calc_returns, calc_posn_and_trades, generate_portfolio


def test_calc_returns_when_valid_initial_cap_should_return_df():
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=3),
        "close_px": [168.3300018310547, 169.57000732421875, 169.05999755859375],
        "open_px": [168.5300018310547, 169.52000732421875, 169.03999755859375],
        "position_shrs": [0.0, 5, 5],
        "trade_cost": [0.0, 0.025, 0.0],
    })
    exp_df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=3),
        "close_px": [168.3300018310547, 169.57000732421875, 169.05999755859375],
        "open_px": [168.5300018310547, 169.52000732421875, 169.03999755859375],
        "position_shrs": [0.0, 5, 5],
        "trade_cost": [0.0, 0.025, 0.0],
        "daily_ret_o2c": [0, 0.0002949504355812285, 0.00011831519337947046],
        "daily_pnl": [0.0, -0.025, 0.10000000000005116],
    })
    result_df = calc_returns(df)
    pd.testing.assert_frame_equal(result_df, exp_df)


def test_calc_pnl_when_valid_should_return_df():
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=3),
        "daily_ret_o2c": [0, 0.00736651506, -0.00300766494],
        "daily_pnl": [0.0, -250.0, 5.767865677247755],
    })
    initial_capital = 10000
    exp_df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=3),
        "daily_ret_o2c": [0, 0.00736651506, -0.00300766494],
        "daily_pnl": [0.0, -250.0, 5.767865677247755],
        "strategy_ret": [0.0, -0.025, 0.0005767865677247755],
        "equity": [10000.0, 9750.0, 9755.767865677248],
        "cum_pnl": [0.0, -250.0, -244.23213432275224],
        "cum_ret_pct": [0.0, -2.500000000000002, -2.442321343227527],
    })
    result_df = calc_pnl(df, initial_capital=initial_capital)
    pd.testing.assert_frame_equal(result_df, exp_df, rtol=1e-8, atol=1e-8)


def test_calc_posn_and_trades_when_valid_should_return_df():
    df = pd.DataFrame({
        "close_px": [100, 102, 101],
        "holding": [1, 1, 0],
        "trade": ["BUY", "HOLD", "SELL"]
    })

    allocation = 0.5
    initial_capital = 1000
    cost_per_shr = 0.1
    result = calc_posn_and_trades(df, allocation, initial_capital, cost_per_shr)

    expected_position = [500, 500, 0]
    expected_shares = [5.0, 5.0, 0.0]
    expected_trade_shrs = [5.0, 0.0, 0.0]
    expected_trade_cost = [0.5, 0.0, 0.0]
    assert result['position'].tolist() == expected_position
    assert result['position_shrs'].tolist() == expected_shares
    assert result['trade_shrs'].tolist() == expected_trade_shrs
    assert result['trade_cost'].tolist() == expected_trade_cost


@patch("src.backtest.portfolio.calc_returns")
@patch("src.backtest.portfolio.calc_pnl")
@patch("src.backtest.portfolio.calc_posn_and_trades")
def test_generate_portfolio_when_valid_should_return_df(mock_calc_posn_and_trades, mock_calc_pnl,
                                                        mock_calc_returns):
    df = pd.DataFrame({
        "close_px": [100, 102, 101],
        "holding": [1, 1, 0],
        "trade": ["BUY", "HOLD", "SELL"]
    })
    execution_params = {
        'initial_capital': 100000,
        'allocation': 0.5,
        'cost_per_shr': 0.005
    }
    generate_portfolio(df, execution_params)

    mock_calc_posn_and_trades.assert_called_once()
    mock_calc_pnl.assert_called_once()
    mock_calc_returns.assert_called_once()
