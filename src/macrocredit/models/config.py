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

    Supports both equal-weight and custom-weight aggregation strategies.

    Attributes
    ----------
    signal_weights : dict[str, float] | None
        Mapping from signal names to weights (must sum to 1.0).
        If None, equal weights are computed from signal_names.
        Example: {"cdx_etf_basis": 0.4, "cdx_vix_gap": 0.4, "spread_momentum": 0.2}
    signal_names : list[str] | None
        Signal names for equal-weight computation when signal_weights is None.
        Ignored if signal_weights is provided.

    Notes
    -----
    Either signal_weights or signal_names must be provided.
    If both are provided, signal_weights takes precedence.
    """

    signal_weights: dict[str, float] | None = None
    signal_names: list[str] | None = None

    def __post_init__(self) -> None:
        """Validate and normalize signal weights configuration."""
        from .aggregator import compute_equal_weights

        # Must provide either weights or names
        if self.signal_weights is None and self.signal_names is None:
            raise ValueError("Must provide either signal_weights or signal_names")

        # Compute equal weights if not provided
        if self.signal_weights is None:
            if not self.signal_names:
                raise ValueError("signal_names cannot be empty when signal_weights is None")
            # Use object.__setattr__ to modify frozen dataclass
            weights = compute_equal_weights(self.signal_names)
            object.__setattr__(self, "signal_weights", weights)
        else:
            # Validate custom weights
            if not self.signal_weights:
                raise ValueError("signal_weights cannot be empty dict")

            if any(w < 0 for w in self.signal_weights.values()):
                raise ValueError("All weights must be non-negative")

            total = sum(self.signal_weights.values())
            if not (0.999 <= total <= 1.001):
                raise ValueError(
                    f"Signal weights must sum to 1.0, got {total:.6f}. "
                    f"Weights: {self.signal_weights}"
                )
