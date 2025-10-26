"""
Data layer for systematic macro credit strategy.

This module handles data loading, cleaning, and transformation for:
- CDX indices (IG, HY, XO) across tenors
- VIX equity volatility index
- Credit ETFs (HYG, LQD) used for signal generation

All loaders produce standardized DataFrames with DatetimeIndex and validated schemas.
"""

from .loader import load_cdx_data, load_vix_data, load_etf_data, load_all_data
from .transform import (
    compute_spread_changes,
    compute_returns,
    align_multiple_series,
    resample_to_daily,
    compute_rolling_zscore,
)
from .validation import validate_cdx_schema, validate_vix_schema, validate_etf_schema

__all__ = [
    # Loaders
    "load_cdx_data",
    "load_vix_data",
    "load_etf_data",
    "load_all_data",
    # Transforms
    "compute_spread_changes",
    "compute_returns",
    "align_multiple_series",
    "resample_to_daily",
    "compute_rolling_zscore",
    # Validation
    "validate_cdx_schema",
    "validate_vix_schema",
    "validate_etf_schema",
]
