"""
Data layer for systematic macro credit strategy.

This module handles data fetching, cleaning, and transformation for:
- CDX indices (IG, HY, XO) across tenors
- VIX equity volatility index
- Credit ETFs (HYG, LQD) used for signal generation

All fetch functions produce standardized DataFrames with DatetimeIndex and validated schemas.
Supports multiple data providers: local files, Bloomberg Terminal, APIs.
"""

from .fetch import fetch_cdx, fetch_vix, fetch_etf
from .sources import FileSource, BloombergSource, APISource, DataSource
from .transform import (
    compute_spread_changes,
    compute_returns,
    align_multiple_series,
    resample_to_daily,
    compute_rolling_zscore,
)
from .validation import validate_cdx_schema, validate_vix_schema, validate_etf_schema

__all__ = [
    # Fetch functions
    "fetch_cdx",
    "fetch_vix",
    "fetch_etf",
    # Data sources
    "FileSource",
    "BloombergSource",
    "APISource",
    "DataSource",
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
