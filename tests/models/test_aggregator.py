"""
Unit tests for signal aggregation logic.
"""

import numpy as np
import pandas as pd
import pytest

from macrocredit.models.aggregator import aggregate_signals
from macrocredit.models.config import AggregatorConfig


@pytest.fixture
def sample_signals() -> tuple[pd.Series, pd.Series, pd.Series]:
    """Generate three synthetic z-score normalized signals."""
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    np.random.seed(42)

    basis = pd.Series(np.random.randn(100), index=dates)
    gap = pd.Series(np.random.randn(100), index=dates)
    momentum = pd.Series(np.random.randn(100), index=dates)

    return basis, gap, momentum


def test_aggregate_signals_returns_series(
    sample_signals: tuple[pd.Series, pd.Series, pd.Series],
) -> None:
    """Test that aggregation returns a pandas Series."""
    basis, gap, momentum = sample_signals
    result = aggregate_signals(basis, gap, momentum)

    assert isinstance(result, pd.Series)
    assert len(result) == len(basis)


def test_aggregate_signals_custom_config(
    sample_signals: tuple[pd.Series, pd.Series, pd.Series],
) -> None:
    """Test aggregation with custom weights."""
    basis, gap, momentum = sample_signals

    config = AggregatorConfig(
        cdx_etf_basis_weight=0.5,
        cdx_vix_gap_weight=0.3,
        spread_momentum_weight=0.2,
        threshold=1.5,
    )

    result = aggregate_signals(basis, gap, momentum, config)
    assert isinstance(result, pd.Series)
    assert len(result) == len(basis)


def test_aggregate_signals_weighted_average(
    sample_signals: tuple[pd.Series, pd.Series, pd.Series],
) -> None:
    """Test that aggregation computes correct weighted average."""
    dates = pd.date_range("2024-01-01", periods=3, freq="D")
    basis = pd.Series([1.0, 2.0, 3.0], index=dates)
    gap = pd.Series([2.0, 3.0, 4.0], index=dates)
    momentum = pd.Series([3.0, 4.0, 5.0], index=dates)

    config = AggregatorConfig(
        cdx_etf_basis_weight=0.5,
        cdx_vix_gap_weight=0.3,
        spread_momentum_weight=0.2,
        threshold=1.0,
    )

    result = aggregate_signals(basis, gap, momentum, config)

    # Manual calculation for first value: 1.0*0.5 + 2.0*0.3 + 3.0*0.2 = 1.7
    expected_first = 1.0 * 0.5 + 2.0 * 0.3 + 3.0 * 0.2
    assert abs(result.iloc[0] - expected_first) < 1e-10


def test_aggregate_signals_handles_nans() -> None:
    """Test that aggregation handles NaN values correctly."""
    dates = pd.date_range("2024-01-01", periods=5, freq="D")

    basis = pd.Series([1.0, np.nan, 2.0, 3.0, 4.0], index=dates)
    gap = pd.Series([2.0, 3.0, np.nan, 4.0, 5.0], index=dates)
    momentum = pd.Series([3.0, 4.0, 5.0, np.nan, 6.0], index=dates)

    result = aggregate_signals(basis, gap, momentum)

    # NaN in any input should produce NaN in output
    assert result.isna().sum() == 3
    # Only first and last should be valid
    assert result.notna().sum() == 2


def test_aggregate_signals_deterministic(
    sample_signals: tuple[pd.Series, pd.Series, pd.Series],
) -> None:
    """Test that aggregation produces deterministic results."""
    basis, gap, momentum = sample_signals
    config = AggregatorConfig(
        cdx_etf_basis_weight=0.4,
        cdx_vix_gap_weight=0.35,
        spread_momentum_weight=0.25,
        threshold=1.2,
    )

    result1 = aggregate_signals(basis, gap, momentum, config)
    result2 = aggregate_signals(basis, gap, momentum, config)

    pd.testing.assert_series_equal(result1, result2)


def test_aggregator_config_weight_validation() -> None:
    """Test that AggregatorConfig validates weight sum."""
    # Valid weights (sum to 1.0)
    config = AggregatorConfig(
        cdx_etf_basis_weight=0.33,
        cdx_vix_gap_weight=0.33,
        spread_momentum_weight=0.34,
        threshold=1.0,
    )
    assert config is not None

    # Invalid weights (sum != 1.0)
    with pytest.raises(ValueError, match="Weights must sum to 1.0"):
        AggregatorConfig(
            cdx_etf_basis_weight=0.5,
            cdx_vix_gap_weight=0.5,
            spread_momentum_weight=0.5,
            threshold=1.0,
        )


def test_aggregator_config_threshold_validation() -> None:
    """Test that AggregatorConfig validates threshold."""
    # Invalid threshold (non-positive)
    with pytest.raises(ValueError, match="Threshold must be positive"):
        AggregatorConfig(
            cdx_etf_basis_weight=0.33,
            cdx_vix_gap_weight=0.33,
            spread_momentum_weight=0.34,
            threshold=0.0,
        )

    with pytest.raises(ValueError, match="Threshold must be positive"):
        AggregatorConfig(
            cdx_etf_basis_weight=0.33,
            cdx_vix_gap_weight=0.33,
            spread_momentum_weight=0.34,
            threshold=-1.0,
        )
