"""
Data transformation utilities for market data processing.

Provides functions for computing returns, spread changes, alignment, and resampling.
All functions preserve DatetimeIndex and handle missing data appropriately.
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def compute_spread_changes(
    spread: pd.Series,
    window: int = 1,
    method: str = "diff",
) -> pd.Series:
    """
    Compute spread changes for CDX data.

    Parameters
    ----------
    spread : pd.Series
        CDX spread levels with DatetimeIndex.
    window : int, default 1
        Lookback period for change calculation.
    method : str, default "diff"
        Calculation method: "diff" for absolute change, "pct" for percentage change.

    Returns
    -------
    pd.Series
        Spread changes with same index as input.

    Notes
    -----
    - "diff" returns basis point changes
    - "pct" returns fractional changes (not percentage points)
    - Useful for momentum and mean-reversion signals
    """
    logger.debug(
        "Computing spread changes: window=%d, method=%s, n_obs=%d",
        window,
        method,
        len(spread),
    )

    if method == "diff":
        changes = spread.diff(window)
    elif method == "pct":
        changes = spread.pct_change(window)
    else:
        raise ValueError(f"Unknown method: {method}. Use 'diff' or 'pct'")

    logger.debug("Computed %d non-null changes", changes.notna().sum())
    return changes


def compute_returns(
    prices: pd.Series,
    window: int = 1,
    log_returns: bool = False,
) -> pd.Series:
    """
    Compute returns for price data (VIX, ETF).

    Parameters
    ----------
    prices : pd.Series
        Price levels with DatetimeIndex.
    window : int, default 1
        Lookback period for return calculation.
    log_returns : bool, default False
        If True, compute log returns; otherwise simple returns.

    Returns
    -------
    pd.Series
        Returns with same index as input.

    Notes
    -----
    - Simple returns: (P_t / P_{t-k}) - 1
    - Log returns: ln(P_t / P_{t-k})
    - Log returns are approximately equal to simple returns for small changes
    """
    logger.debug(
        "Computing returns: window=%d, log=%s, n_obs=%d",
        window,
        log_returns,
        len(prices),
    )

    if log_returns:
        returns = (prices / prices.shift(window)).apply(np.log)
    else:
        returns = prices.pct_change(window)

    logger.debug("Computed %d non-null returns", returns.notna().sum())
    return returns


def align_multiple_series(
    *series: pd.Series,
    method: str = "inner",
    fill_method: str | None = None,
) -> list[pd.Series]:
    """
    Align multiple time series to common date index.

    Parameters
    ----------
    *series : pd.Series
        Variable number of Series to align.
    method : str, default "inner"
        Alignment method: "inner" (intersection) or "outer" (union).
    fill_method : str | None, optional
        Forward fill method for missing data: "ffill", "bfill", or None.

    Returns
    -------
    list[pd.Series]
        List of aligned Series with common index.

    Notes
    -----
    - "inner" keeps only dates present in all series
    - "outer" keeps all dates from any series
    - fill_method can reduce data loss but may introduce look-ahead bias
    """
    logger.debug(
        "Aligning %d series: method=%s, fill_method=%s",
        len(series),
        method,
        fill_method,
    )

    if len(series) < 2:
        logger.warning("Less than 2 series provided, returning unchanged")
        return list(series)

    # Create DataFrame for alignment
    df = pd.concat(series, axis=1, join=method)

    # Apply fill method if requested
    if fill_method == "ffill":
        df = df.ffill()
    elif fill_method == "bfill":
        df = df.bfill()
    elif fill_method is not None:
        raise ValueError(f"Unknown fill_method: {fill_method}. Use 'ffill' or 'bfill'")

    # Convert back to list of Series
    aligned = [df.iloc[:, i] for i in range(len(series))]

    logger.debug(
        "Aligned to %d common dates: original_lengths=%s",
        len(aligned[0]),
        [len(s) for s in series],
    )
    return aligned


def resample_to_daily(
    df: pd.DataFrame,
    agg_method: str | dict[str, str] = "last",
) -> pd.DataFrame:
    """
    Resample data to daily frequency.

    Parameters
    ----------
    df : pd.DataFrame
        Data with DatetimeIndex to resample.
    agg_method : str | dict[str, str], default "last"
        Aggregation method: "last", "first", "mean", or dict mapping columns to methods.

    Returns
    -------
    pd.DataFrame
        Resampled data with daily frequency.

    Notes
    -----
    - Useful for handling intraday data or irregular timestamps
    - "last" takes end-of-day value (typical for price/spread data)
    - "mean" averages within day (useful for volatility)
    """
    logger.debug(
        "Resampling to daily: original_freq=%s, n_rows=%d",
        df.index.inferred_freq,
        len(df),
    )

    if isinstance(agg_method, str):
        resampled = df.resample("D").agg(agg_method)
    else:
        resampled = df.resample("D").agg(agg_method)

    # Drop rows with all NaN
    resampled = resampled.dropna(how="all")

    logger.debug("Resampled to %d daily observations", len(resampled))
    return resampled


def compute_rolling_zscore(
    series: pd.Series,
    window: int = 20,
    min_periods: int | None = None,
) -> pd.Series:
    """
    Compute rolling z-score normalization.

    Parameters
    ----------
    series : pd.Series
        Input time series with DatetimeIndex.
    window : int, default 20
        Rolling window size in observations.
    min_periods : int | None, optional
        Minimum observations required. Defaults to window.

    Returns
    -------
    pd.Series
        Z-score normalized series: (x - μ) / σ

    Notes
    -----
    - Useful for signal standardization
    - Z-score of 0 means series is at rolling mean
    - Z-score of ±2 indicates 2 standard deviations from mean
    """
    if min_periods is None:
        min_periods = window

    logger.debug(
        "Computing rolling z-score: window=%d, min_periods=%d, n_obs=%d",
        window,
        min_periods,
        len(series),
    )

    rolling_mean = series.rolling(window=window, min_periods=min_periods).mean()
    rolling_std = series.rolling(window=window, min_periods=min_periods).std()

    # Avoid division by zero
    zscore = (series - rolling_mean) / rolling_std.replace(0, float("nan"))

    logger.debug("Computed %d non-null z-scores", zscore.notna().sum())
    return zscore
