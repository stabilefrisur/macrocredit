"""
Configuration dataclasses for signal generation and aggregation.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SignalConfig:
    """
    Configuration parameters for individual signal computation.

    Attributes
    ----------
    lookback : int
        Rolling window size for normalization and statistics.
    min_periods : int
        Minimum observations required for valid calculation.
    """

    lookback: int = 20
    min_periods: int = 10


@dataclass(frozen=True)
class AggregatorConfig:
    """
    Configuration for combining multiple signals into composite score.

    Attributes
    ----------
    cdx_etf_basis_weight : float
        Weight for CDX-ETF basis signal (0.0 to 1.0).
    cdx_vix_gap_weight : float
        Weight for CDX-VIX gap signal (0.0 to 1.0).
    spread_momentum_weight : float
        Weight for spread momentum signal (0.0 to 1.0).
    threshold : float
        Absolute z-score threshold for triggering positions.
    """

    cdx_etf_basis_weight: float = 0.35
    cdx_vix_gap_weight: float = 0.35
    spread_momentum_weight: float = 0.30
    threshold: float = 1.0

    def __post_init__(self) -> None:
        """Validate weights sum approximately to 1.0."""
        total = self.cdx_etf_basis_weight + self.cdx_vix_gap_weight + self.spread_momentum_weight
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Weights must sum to 1.0, got {total:.3f}")
        if self.threshold <= 0:
            raise ValueError("Threshold must be positive")
