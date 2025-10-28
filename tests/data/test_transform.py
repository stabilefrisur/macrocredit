"""Tests for data transformation functionality."""

import pandas as pd
import pytest
import numpy as np

from macrocredit.data.transform import (
    compute_spread_changes,
    compute_returns,
    align_multiple_series,
    resample_to_daily,
    compute_rolling_zscore,
)


def test_compute_spread_changes_diff() -> None:
    """Test computing spread changes using diff method."""
    spread = pd.Series(
        [100.0, 105.0, 102.0, 110.0, 108.0],
        index=pd.date_range("2024-01-01", periods=5),
    )

    changes = compute_spread_changes(spread, window=1, method="diff")

    assert len(changes) == 5
    assert pd.isna(changes.iloc[0])
    assert changes.iloc[1] == 5.0
    assert changes.iloc[2] == -3.0


def test_compute_spread_changes_pct() -> None:
    """Test computing spread changes using pct method."""
    spread = pd.Series(
        [100.0, 110.0, 121.0],
        index=pd.date_range("2024-01-01", periods=3),
    )

    changes = compute_spread_changes(spread, window=1, method="pct")

    assert len(changes) == 3
    assert pd.isna(changes.iloc[0])
    assert abs(changes.iloc[1] - 0.10) < 1e-6
    assert abs(changes.iloc[2] - 0.10) < 1e-6


def test_compute_spread_changes_multiday() -> None:
    """Test computing spread changes with multi-day window."""
    spread = pd.Series(
        [100.0, 105.0, 102.0, 110.0, 108.0],
        index=pd.date_range("2024-01-01", periods=5),
    )

    changes = compute_spread_changes(spread, window=2, method="diff")

    assert len(changes) == 5
    assert pd.isna(changes.iloc[0])
    assert pd.isna(changes.iloc[1])
    assert changes.iloc[2] == 2.0  # 102 - 100


def test_compute_spread_changes_invalid_method() -> None:
    """Test that invalid method raises ValueError."""
    spread = pd.Series([100.0, 105.0], index=pd.date_range("2024-01-01", periods=2))

    with pytest.raises(ValueError, match="Unknown method"):
        compute_spread_changes(spread, method="invalid")


def test_compute_returns_simple() -> None:
    """Test computing simple returns."""
    prices = pd.Series(
        [100.0, 110.0, 121.0],
        index=pd.date_range("2024-01-01", periods=3),
    )

    returns = compute_returns(prices, window=1, log_returns=False)

    assert len(returns) == 3
    assert pd.isna(returns.iloc[0])
    assert abs(returns.iloc[1] - 0.10) < 1e-6
    assert abs(returns.iloc[2] - 0.10) < 1e-6


def test_compute_returns_log() -> None:
    """Test computing log returns."""
    prices = pd.Series(
        [100.0, 110.0, 121.0],
        index=pd.date_range("2024-01-01", periods=3),
    )

    returns = compute_returns(prices, window=1, log_returns=True)

    assert len(returns) == 3
    assert pd.isna(returns.iloc[0])
    # log(110/100) ≈ 0.0953
    assert abs(returns.iloc[1] - np.log(1.1)) < 1e-6


def test_align_multiple_series_inner() -> None:
    """Test aligning multiple series with inner join."""
    s1 = pd.Series(
        [1.0, 2.0, 3.0],
        index=pd.date_range("2024-01-01", periods=3),
    )
    s2 = pd.Series(
        [10.0, 20.0, 30.0],
        index=pd.date_range("2024-01-02", periods=3),
    )

    aligned = align_multiple_series(s1, s2, method="inner")

    assert len(aligned) == 2
    assert len(aligned[0]) == 2  # Only 01-02 and 01-03 overlap
    assert len(aligned[1]) == 2


def test_align_multiple_series_outer() -> None:
    """Test aligning multiple series with outer join."""
    s1 = pd.Series(
        [1.0, 2.0, 3.0],
        index=pd.date_range("2024-01-01", periods=3),
    )
    s2 = pd.Series(
        [10.0, 20.0, 30.0],
        index=pd.date_range("2024-01-02", periods=3),
    )

    aligned = align_multiple_series(s1, s2, method="outer")

    assert len(aligned) == 2
    assert len(aligned[0]) == 4  # Union of dates (01-01 to 01-04)
    assert len(aligned[1]) == 4


def test_align_multiple_series_ffill() -> None:
    """Test aligning multiple series with forward fill."""
    s1 = pd.Series(
        [1.0, 2.0, 3.0],
        index=pd.date_range("2024-01-01", periods=3),
    )
    s2 = pd.Series(
        [10.0, 20.0],
        index=pd.date_range("2024-01-02", periods=2),
    )

    aligned = align_multiple_series(s1, s2, method="outer", fill_method="ffill")

    assert len(aligned) == 2
    assert aligned[1].iloc[-1] == 20.0  # Forward filled


def test_resample_to_daily_last() -> None:
    """Test resampling to daily frequency using last value."""
    # Create hourly data
    df = pd.DataFrame(
        {
            "value": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        },
        index=pd.date_range("2024-01-01", periods=6, freq="4h"),
    )

    resampled = resample_to_daily(df, agg_method="last")

    assert len(resampled) <= 2  # Should collapse to 1-2 days
    # Last value of first day should be used


def test_resample_to_daily_mean() -> None:
    """Test resampling to daily frequency using mean."""
    df = pd.DataFrame(
        {
            "value": [1.0, 2.0, 3.0, 4.0],
        },
        index=pd.date_range("2024-01-01", periods=4, freq="6h"),
    )

    resampled = resample_to_daily(df, agg_method="mean")

    assert len(resampled) == 1
    assert resampled["value"].iloc[0] == 2.5


def test_compute_rolling_zscore() -> None:
    """Test computing rolling z-score."""
    series = pd.Series(
        [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0],
        index=pd.date_range("2024-01-01", periods=10),
    )

    zscore = compute_rolling_zscore(series, window=5)

    assert len(zscore) == 10
    # First 4 values should be NaN (insufficient data)
    assert pd.isna(zscore.iloc[:4]).all()
    # Later values should be close to 0 for linear trend
    # (due to rolling window following the trend)


def test_compute_rolling_zscore_constant() -> None:
    """Test z-score with constant series (zero std)."""
    series = pd.Series(
        [10.0] * 10,
        index=pd.date_range("2024-01-01", periods=10),
    )

    zscore = compute_rolling_zscore(series, window=5)

    # Should handle zero std gracefully
    assert len(zscore) == 10
    # Z-scores should be NaN when std is zero
    assert pd.isna(zscore.iloc[4:]).all()


def test_align_single_series(caplog: pytest.LogCaptureFixture) -> None:
    """Test that aligning single series returns it unchanged."""
    s1 = pd.Series([1.0, 2.0, 3.0], index=pd.date_range("2024-01-01", periods=3))

    aligned = align_multiple_series(s1)

    assert len(aligned) == 1
    assert "less than 2 series" in caplog.text.lower()

