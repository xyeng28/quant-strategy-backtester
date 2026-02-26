from unittest.mock import patch
import pandas as pd
from src.backtester.portfolio import calc_pnl, calc_returns, calc_posn_and_trades, generate_portfolio


def test_calc_pnl_when_valid_initial_cap_should_return_df():
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=3),
        "close_px": [168.3300018310547, 169.57000732421875, 169.05999755859375],
        "position": [0.0, 5, 5],
        "trade_cost": [0.0, 0.025, 0.0],
    })
    initial_capital = 10000
    exp_df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=3),
        "close_px": [168.3300018310547, 169.57000732421875, 169.05999755859375],
        "position": [0.0, 5, 5],
        "trade_cost": [0.0, 0.025, 0.0],
        "daily_ret_c2c": [0, 0.00736651506, -0.00300766494],
        "daily_pnl": [0, -0.025, -0.0150383247],
        "cum_pnl": [10000, 9999.975, 9999.93496168]
    })
    result_df = calc_pnl(df, initial_capital=initial_capital)
    pd.testing.assert_frame_equal(result_df, exp_df)


def test_calc_returns_when_valid_should_return_df():
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=3),
        "daily_ret_c2c": [0, 0.00736651506, -0.00300766494],
        "cum_pnl": [10000, 9999.975, 9999.93496168],
    })
    initial_capital = 10000
    exp_df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=3),
        "daily_ret_c2c": [0, 0.00736651506, -0.00300766494],
        "cum_pnl": [10000, 9999.975, 9999.93496168],
        "cum_ret": [1, 1.00736651506, 1.00433669411],
        "cum_ret_pct": [0, -0.00024999999, -0.0006503832]
    })
    result_df = calc_returns(df, initial_capital=initial_capital)
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


@patch("src.backtester.portfolio.calc_returns")
@patch("src.backtester.portfolio.calc_pnl")
@patch("src.backtester.portfolio.calc_posn_and_trades")
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
