"""
Unit tests for backtest engine.
"""

import numpy as np
import pandas as pd
import pytest

from aponyx.backtest import (
    BacktestConfig,
    run_backtest,
    compute_performance_metrics,
)


@pytest.fixture
def sample_signal_and_spread() -> tuple[pd.Series, pd.Series]:
    """Generate synthetic signal and spread data for testing."""
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    np.random.seed(42)

    # Create signal with clear regime changes
    signal = pd.Series(
        np.concatenate(
            [
                np.full(20, 0.5),  # Neutral
                np.full(15, 2.0),  # Strong long
                np.full(20, 0.3),  # Neutral
                np.full(15, -2.0),  # Strong short
                np.full(30, 0.2),  # Neutral
            ]
        ),
        index=dates,
    )

    # Spread that trends opposite to position (for P&L testing)
    spread = pd.Series(
        100 + np.cumsum(np.random.randn(100) * 0.5),
        index=dates,
    )

    return signal, spread


def test_backtest_config_validation() -> None:
    """Test that config validation catches invalid parameters."""
    # Valid config should work
    BacktestConfig(entry_threshold=1.5, exit_threshold=0.5)

    # Entry <= exit should raise
    with pytest.raises(ValueError, match="entry_threshold.*must be >"):
        BacktestConfig(entry_threshold=1.0, exit_threshold=1.0)

    # Negative position size should raise
    with pytest.raises(ValueError, match="position_size must be positive"):
        BacktestConfig(position_size=-10.0)

    # Negative transaction cost should raise
    with pytest.raises(ValueError, match="transaction_cost_bps must be non-negative"):
        BacktestConfig(transaction_cost_bps=-1.0)


def test_run_backtest_returns_result(
    sample_signal_and_spread: tuple[pd.Series, pd.Series],
) -> None:
    """Test that backtest returns properly structured result."""
    signal, spread = sample_signal_and_spread
    result = run_backtest(signal, spread)

    # Check structure
    assert hasattr(result, "positions")
    assert hasattr(result, "pnl")
    assert hasattr(result, "metadata")

    # Check positions DataFrame
    assert isinstance(result.positions, pd.DataFrame)
    assert "signal" in result.positions.columns
    assert "position" in result.positions.columns
    assert "days_held" in result.positions.columns
    assert "spread" in result.positions.columns

    # Check P&L DataFrame
    assert isinstance(result.pnl, pd.DataFrame)
    assert "spread_pnl" in result.pnl.columns
    assert "cost" in result.pnl.columns
    assert "net_pnl" in result.pnl.columns
    assert "cumulative_pnl" in result.pnl.columns

    # Check metadata
    assert "config" in result.metadata
    assert "summary" in result.metadata


def test_run_backtest_generates_positions(
    sample_signal_and_spread: tuple[pd.Series, pd.Series],
) -> None:
    """Test that backtest generates positions based on thresholds."""
    signal, spread = sample_signal_and_spread
    config = BacktestConfig(entry_threshold=1.5, exit_threshold=0.5)
    result = run_backtest(signal, spread, config)

    # Should have some long positions (signal = 2.0)
    assert (result.positions["position"] == 1).any()

    # Should have some short positions (signal = -2.0)
    assert (result.positions["position"] == -1).any()

    # Should have neutral periods (signal below threshold)
    assert (result.positions["position"] == 0).any()


def test_run_backtest_tracks_holding_period(
    sample_signal_and_spread: tuple[pd.Series, pd.Series],
) -> None:
    """Test that backtest correctly tracks days held."""
    signal, spread = sample_signal_and_spread
    result = run_backtest(signal, spread)

    # When in position, days_held should increment
    in_position = result.positions[result.positions["position"] != 0]
    if len(in_position) > 1:
        # Days held should increase during position
        consecutive_positions = in_position[in_position.index.to_series().diff() == pd.Timedelta(days=1)]
        if len(consecutive_positions) > 0:
            assert (consecutive_positions["days_held"] > 0).any()


def test_run_backtest_applies_transaction_costs(
    sample_signal_and_spread: tuple[pd.Series, pd.Series],
) -> None:
    """Test that transaction costs are applied on trades."""
    signal, spread = sample_signal_and_spread
    config = BacktestConfig(transaction_cost_bps=2.0, position_size=10.0)
    result = run_backtest(signal, spread, config)

    # Total costs should be positive (costs incurred)
    total_costs = result.pnl["cost"].sum()
    assert total_costs > 0

    # Costs should only occur on trade entry/exit
    trades = result.positions["position"].diff().fillna(0) != 0
    n_trades = trades.sum()
    if n_trades > 0:
        assert result.pnl["cost"].gt(0).sum() <= n_trades


def test_run_backtest_calculates_pnl(
    sample_signal_and_spread: tuple[pd.Series, pd.Series],
) -> None:
    """Test that P&L calculation is reasonable."""
    signal, spread = sample_signal_and_spread
    result = run_backtest(signal, spread)

    # Net P&L should be spread P&L minus costs
    expected_net = result.pnl["spread_pnl"] - result.pnl["cost"]
    pd.testing.assert_series_equal(
        result.pnl["net_pnl"], expected_net, check_names=False
    )

    # Cumulative P&L should be cumulative sum of net P&L
    expected_cum = result.pnl["net_pnl"].cumsum()
    pd.testing.assert_series_equal(
        result.pnl["cumulative_pnl"], expected_cum, check_names=False
    )


def test_compute_performance_metrics_structure() -> None:
    """Test that performance metrics returns all expected fields."""
    # Create simple synthetic backtest result
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    pnl_df = pd.DataFrame(
        {
            "net_pnl": np.random.randn(100) * 100,
            "cumulative_pnl": np.cumsum(np.random.randn(100) * 100),
        },
        index=dates,
    )
    positions_df = pd.DataFrame(
        {
            "position": np.random.choice([0, 1, -1], size=100),
            "days_held": np.random.randint(0, 10, size=100),
        },
        index=dates,
    )

    metrics = compute_performance_metrics(pnl_df, positions_df)

    # Check all fields exist
    assert hasattr(metrics, "sharpe_ratio")
    assert hasattr(metrics, "sortino_ratio")
    assert hasattr(metrics, "max_drawdown")
    assert hasattr(metrics, "calmar_ratio")
    assert hasattr(metrics, "total_return")
    assert hasattr(metrics, "annualized_return")
    assert hasattr(metrics, "annualized_volatility")
    assert hasattr(metrics, "hit_rate")
    assert hasattr(metrics, "avg_win")
    assert hasattr(metrics, "avg_loss")
    assert hasattr(metrics, "win_loss_ratio")
    assert hasattr(metrics, "n_trades")
    assert hasattr(metrics, "avg_holding_days")


def test_compute_performance_metrics_values(
    sample_signal_and_spread: tuple[pd.Series, pd.Series],
) -> None:
    """Test that performance metrics have reasonable values."""
    signal, spread = sample_signal_and_spread
    result = run_backtest(signal, spread)
    metrics = compute_performance_metrics(result.pnl, result.positions)

    # Hit rate should be between 0 and 1
    assert 0.0 <= metrics.hit_rate <= 1.0

    # Max drawdown should be negative or zero
    assert metrics.max_drawdown <= 0

    # Number of trades should be non-negative integer
    assert metrics.n_trades >= 0
    assert isinstance(metrics.n_trades, int)

    # Average holding days should be non-negative
    assert metrics.avg_holding_days >= 0


def test_backtest_metadata_logging(
    sample_signal_and_spread: tuple[pd.Series, pd.Series],
) -> None:
    """Test that backtest logs complete metadata."""
    signal, spread = sample_signal_and_spread
    config = BacktestConfig(entry_threshold=2.0, position_size=15.0)
    result = run_backtest(signal, spread, config)

    # Check config is logged
    assert result.metadata["config"]["entry_threshold"] == 2.0
    assert result.metadata["config"]["position_size"] == 15.0

    # Check summary statistics exist
    assert "n_trades" in result.metadata["summary"]
    assert "total_pnl" in result.metadata["summary"]
    assert "start_date" in result.metadata["summary"]
    assert "end_date" in result.metadata["summary"]


def test_backtest_with_max_holding_days(
    sample_signal_and_spread: tuple[pd.Series, pd.Series],
) -> None:
    """Test that max holding days constraint is enforced."""
    signal, spread = sample_signal_and_spread
    config = BacktestConfig(entry_threshold=1.5, max_holding_days=5)
    result = run_backtest(signal, spread, config)

    # No position should be held longer than max_holding_days
    in_position = result.positions[result.positions["position"] != 0]
    if len(in_position) > 0:
        assert in_position["days_held"].max() <= config.max_holding_days


def test_run_backtest_validates_index_types() -> None:
    """Test that backtest validates input index types."""
    # Create signal and spread with non-datetime indices
    signal = pd.Series([1.0, 2.0, 3.0], index=[0, 1, 2])
    spread = pd.Series([100.0, 101.0, 102.0], index=[0, 1, 2])

    # Should raise ValueError for non-DatetimeIndex
    with pytest.raises(ValueError, match="composite_signal must have DatetimeIndex"):
        run_backtest(signal, spread)

    # Test with valid signal but invalid spread
    dates = pd.date_range("2024-01-01", periods=3, freq="D")
    signal_valid = pd.Series([1.0, 2.0, 3.0], index=dates)
    
    with pytest.raises(ValueError, match="spread must have DatetimeIndex"):
        run_backtest(signal_valid, spread)
