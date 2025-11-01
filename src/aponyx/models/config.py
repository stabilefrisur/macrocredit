"""
Configuration dataclasses for signal generation.
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
