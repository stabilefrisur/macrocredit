"""
Unit tests for signal aggregation logic.
"""

import numpy as np
import pandas as pd
import pytest

from macrocredit.models.aggregator import aggregate_signals
from macrocredit.models.config import AggregatorConfig, SignalConfig


@pytest.fixture
def sample_signals_dict() -> dict[str, pd.Series]:
    """Generate three synthetic z-score normalized signals as dict."""
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    np.random.seed(42)

    return {
        "cdx_etf_basis": pd.Series(np.random.randn(100), index=dates),
        "cdx_vix_gap": pd.Series(np.random.randn(100), index=dates),
        "spread_momentum": pd.Series(np.random.randn(100), index=dates),
    }


@pytest.fixture
def sample_weights() -> dict[str, float]:
    """Default signal weights."""
    return {
        "cdx_etf_basis": 0.35,
        "cdx_vix_gap": 0.35,
        "spread_momentum": 0.30,
    }


def test_aggregate_signals_returns_series(
    sample_signals_dict: dict[str, pd.Series],
    sample_weights: dict[str, float],
) -> None:
    """Test that aggregation returns a pandas Series."""
    result = aggregate_signals(sample_signals_dict, sample_weights)

    assert isinstance(result, pd.Series)
    assert len(result) == 100


def test_aggregate_signals_custom_weights(
    sample_signals_dict: dict[str, pd.Series],
) -> None:
    """Test aggregation with custom weights."""
    weights = {
        "cdx_etf_basis": 0.5,
        "cdx_vix_gap": 0.3,
        "spread_momentum": 0.2,
    }

    result = aggregate_signals(sample_signals_dict, weights)
    assert isinstance(result, pd.Series)
    assert len(result) == 100


def test_aggregate_signals_weighted_average() -> None:
    """Test that aggregation computes correct weighted average."""
    dates = pd.date_range("2024-01-01", periods=3, freq="D")
    
    signals = {
        "signal_a": pd.Series([1.0, 2.0, 3.0], index=dates),
        "signal_b": pd.Series([2.0, 3.0, 4.0], index=dates),
        "signal_c": pd.Series([3.0, 4.0, 5.0], index=dates),
    }
    
    weights = {
        "signal_a": 0.5,
        "signal_b": 0.3,
        "signal_c": 0.2,
    }

    result = aggregate_signals(signals, weights)

    # Manual calculation for first value: 1.0*0.5 + 2.0*0.3 + 3.0*0.2 = 1.7
    expected_first = 1.0 * 0.5 + 2.0 * 0.3 + 3.0 * 0.2
    assert abs(result.iloc[0] - expected_first) < 1e-10


def test_aggregate_signals_handles_nans() -> None:
    """Test that aggregation handles NaN values correctly."""
    dates = pd.date_range("2024-01-01", periods=5, freq="D")

    signals = {
        "signal_a": pd.Series([1.0, np.nan, 2.0, 3.0, 4.0], index=dates),
        "signal_b": pd.Series([2.0, 3.0, np.nan, 4.0, 5.0], index=dates),
        "signal_c": pd.Series([3.0, 4.0, 5.0, np.nan, 6.0], index=dates),
    }
    
    weights = {
        "signal_a": 0.33,
        "signal_b": 0.33,
        "signal_c": 0.34,
    }

    result = aggregate_signals(signals, weights)

    # NaN in any input should produce NaN in output
    assert result.isna().sum() == 3
    # Only first and last should be valid
    assert result.notna().sum() == 2


def test_aggregate_signals_deterministic(
    sample_signals_dict: dict[str, pd.Series],
) -> None:
    """Test that aggregation produces deterministic results."""
    weights = {
        "cdx_etf_basis": 0.4,
        "cdx_vix_gap": 0.35,
        "spread_momentum": 0.25,
    }

    result1 = aggregate_signals(sample_signals_dict, weights)
    result2 = aggregate_signals(sample_signals_dict, weights)

    pd.testing.assert_series_equal(result1, result2)


def test_aggregate_signals_missing_signal_raises_error(
    sample_signals_dict: dict[str, pd.Series],
) -> None:
    """Test that missing signal in signals dict raises KeyError."""
    weights = {
        "cdx_etf_basis": 0.5,
        "cdx_vix_gap": 0.3,
        "nonexistent_signal": 0.2,  # This signal doesn't exist
    }

    with pytest.raises(KeyError, match="Signals missing for weights"):
        aggregate_signals(sample_signals_dict, weights)


def test_aggregate_signals_two_signals() -> None:
    """Test aggregation with only two signals."""
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    
    signals = {
        "signal_a": pd.Series(np.random.randn(10), index=dates),
        "signal_b": pd.Series(np.random.randn(10), index=dates),
    }
    
    weights = {
        "signal_a": 0.6,
        "signal_b": 0.4,
    }

    result = aggregate_signals(signals, weights)
    assert isinstance(result, pd.Series)
    assert len(result) == 10


def test_aggregate_signals_five_signals() -> None:
    """Test aggregation with five signals (future expansion scenario)."""
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    
    signals = {
        "signal_1": pd.Series(np.random.randn(10), index=dates),
        "signal_2": pd.Series(np.random.randn(10), index=dates),
        "signal_3": pd.Series(np.random.randn(10), index=dates),
        "signal_4": pd.Series(np.random.randn(10), index=dates),
        "signal_5": pd.Series(np.random.randn(10), index=dates),
    }
    
    weights = {
        "signal_1": 0.20,
        "signal_2": 0.20,
        "signal_3": 0.20,
        "signal_4": 0.20,
        "signal_5": 0.20,
    }

    result = aggregate_signals(signals, weights)
    assert isinstance(result, pd.Series)
    assert len(result) == 10


def test_aggregator_config_weight_validation() -> None:
    """Test that AggregatorConfig validates weight sum."""
    # Valid weights (sum to 1.0)
    config = AggregatorConfig(
        signal_weights={
            "signal_a": 0.33,
            "signal_b": 0.33,
            "signal_c": 0.34,
        }
    )
    assert config is not None

    # Invalid weights (sum != 1.0)
    with pytest.raises(ValueError, match="Signal weights must sum to 1.0"):
        AggregatorConfig(
            signal_weights={
                "signal_a": 0.5,
                "signal_b": 0.5,
                "signal_c": 0.5,
            }
        )


def test_aggregator_config_empty_weights_validation() -> None:
    """Test that AggregatorConfig rejects empty weights."""
    with pytest.raises(ValueError, match="signal_weights cannot be empty"):
        AggregatorConfig(signal_weights={})


def test_aggregator_config_negative_weight_validation() -> None:
    """Test that AggregatorConfig rejects negative weights."""
    with pytest.raises(ValueError, match="All weights must be non-negative"):
        AggregatorConfig(
            signal_weights={
                "signal_a": 0.6,
                "signal_b": 0.5,
                "signal_c": -0.1,
            }
        )


def test_signal_config_validation() -> None:
    """Test that SignalConfig validates parameters."""
    # Valid config
    config = SignalConfig(lookback=20, min_periods=10)
    assert config is not None

    # Invalid lookback (non-positive)
    with pytest.raises(ValueError, match="lookback must be positive"):
        SignalConfig(lookback=0, min_periods=5)

    with pytest.raises(ValueError, match="lookback must be positive"):
        SignalConfig(lookback=-10, min_periods=5)

    # Invalid min_periods (non-positive)
    with pytest.raises(ValueError, match="min_periods must be positive"):
        SignalConfig(lookback=20, min_periods=0)

    with pytest.raises(ValueError, match="min_periods must be positive"):
        SignalConfig(lookback=20, min_periods=-5)

    # Invalid min_periods > lookback
    with pytest.raises(ValueError, match="min_periods.*cannot exceed lookback"):
        SignalConfig(lookback=10, min_periods=15)

