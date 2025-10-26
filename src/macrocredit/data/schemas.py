"""
Data schemas and validation rules for market data.

Defines expected column names, types, and constraints for each data source.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CDXSchema:
    """Schema for CDX index data."""

    date_col: str = "date"
    spread_col: str = "spread"
    index_col: str = "index"  # e.g., "CDX_IG_5Y"
    tenor_col: str = "tenor"  # e.g., "5Y", "10Y"
    series_col: str = "series"  # CDX series number

    required_cols: tuple[str, ...] = ("date", "spread", "index")
    optional_cols: tuple[str, ...] = ("tenor", "series", "volume", "bid", "ask")

    # Validation constraints
    min_spread: float = 0.0  # Spreads in basis points
    max_spread: float = 10000.0  # 100% spread cap


@dataclass(frozen=True)
class VIXSchema:
    """Schema for VIX volatility index data."""

    date_col: str = "date"
    close_col: str = "close"
    high_col: str = "high"
    low_col: str = "low"
    open_col: str = "open"

    required_cols: tuple[str, ...] = ("date", "close")
    optional_cols: tuple[str, ...] = ("open", "high", "low", "volume")

    # Validation constraints
    min_vix: float = 0.0
    max_vix: float = 200.0  # Extreme stress cap


@dataclass(frozen=True)
class ETFSchema:
    """Schema for credit ETF data (HYG, LQD)."""

    date_col: str = "date"
    close_col: str = "close"
    ticker_col: str = "ticker"
    volume_col: str = "volume"

    required_cols: tuple[str, ...] = ("date", "close", "ticker")
    optional_cols: tuple[str, ...] = ("open", "high", "low", "volume", "adjusted_close")

    # Validation constraints
    min_price: float = 0.0
    max_price: float = 10000.0  # Sanity check


# Schema registry for runtime lookup
SCHEMAS: dict[str, Any] = {
    "cdx": CDXSchema(),
    "vix": VIXSchema(),
    "etf": ETFSchema(),
}
