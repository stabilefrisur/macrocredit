"""
Configuration for backtest engine.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BacktestConfig:
    """
    Backtest parameters and trading constraints.

    Attributes
    ----------
    entry_threshold : float
        Composite signal threshold for entering positions.
        Absolute value above this triggers trades.
    exit_threshold : float
        Composite signal threshold for exiting positions.
        Helps avoid whipsaw by requiring signal decay.
    position_size : float
        Notional position size in millions (e.g., 10.0 = $10MM).
    transaction_cost_bps : float
        Round-trip transaction cost in basis points.
        Typical CDX costs: 0.5-2.0 bps depending on liquidity.
    max_holding_days : int | None
        Maximum days to hold a position before forced exit.
        None means no time limit.
    dv01_per_million : float
        DV01 per $1MM notional for risk calculations.
        Typical CDX IG 5Y: ~4500-5000.

    Notes
    -----
    - entry_threshold > exit_threshold creates hysteresis to reduce turnover.
    - Position sizing is deliberately simple for the pilot (binary on/off).
    - Transaction costs are applied symmetrically on entry and exit.
    """

    entry_threshold: float = 1.5
    exit_threshold: float = 0.75
    position_size: float = 10.0
    transaction_cost_bps: float = 1.0
    max_holding_days: int | None = None
    dv01_per_million: float = 4750.0

    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if self.entry_threshold <= self.exit_threshold:
            raise ValueError(
                f"entry_threshold ({self.entry_threshold}) must be > "
                f"exit_threshold ({self.exit_threshold})"
            )
        if self.position_size <= 0:
            raise ValueError(f"position_size must be positive, got {self.position_size}")
        if self.transaction_cost_bps < 0:
            raise ValueError(
                f"transaction_cost_bps must be non-negative, got {self.transaction_cost_bps}"
            )
