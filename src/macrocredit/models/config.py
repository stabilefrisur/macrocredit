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

    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if self.lookback <= 0:
            raise ValueError(f"lookback must be positive, got {self.lookback}")
        if self.min_periods <= 0:
            raise ValueError(f"min_periods must be positive, got {self.min_periods}")
        if self.min_periods > self.lookback:
            raise ValueError(
                f"min_periods ({self.min_periods}) cannot exceed lookback ({self.lookback})"
            )


@dataclass(frozen=True)
class AggregatorConfig:
    """
    Configuration for combining multiple signals into composite score.

    Attributes
    ----------
    signal_weights : dict[str, float]
        Mapping from signal names to weights (must sum to 1.0).
        Example: {"cdx_etf_basis": 0.4, "cdx_vix_gap": 0.4, "spread_momentum": 0.2}
    """

    signal_weights: dict[str, float]

    def __post_init__(self) -> None:
        """Validate signal weights configuration."""
        if not self.signal_weights:
            raise ValueError("signal_weights cannot be empty")
        
        if any(w < 0 for w in self.signal_weights.values()):
            raise ValueError("All weights must be non-negative")
        
        total = sum(self.signal_weights.values())
        if not (0.999 <= total <= 1.001):
            raise ValueError(
                f"Signal weights must sum to 1.0, got {total:.6f}. "
                f"Weights: {self.signal_weights}"
            )
