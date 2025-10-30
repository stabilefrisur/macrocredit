"""
Models layer for systematic credit strategies.

This module provides signal generation and strategy logic for the CDX overlay pilot.
"""

from .signals import (
    compute_cdx_etf_basis,
    compute_cdx_vix_gap,
    compute_spread_momentum,
)
from .aggregator import aggregate_signals
from .config import SignalConfig, AggregatorConfig
from .registry import SignalRegistry, SignalMetadata
from .catalog import compute_registered_signals

__all__ = [
    "compute_cdx_etf_basis",
    "compute_cdx_vix_gap",
    "compute_spread_momentum",
    "aggregate_signals",
    "SignalConfig",
    "AggregatorConfig",
    "SignalRegistry",
    "SignalMetadata",
    "compute_registered_signals",
]
