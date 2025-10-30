"""Signal aggregation logic for combining multiple signals into composite positioning score.
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def compute_equal_weights(signal_names: list[str]) -> dict[str, float]:
    """
    Generate equal-weight dictionary for signal aggregation.

    Parameters
    ----------
    signal_names : list[str]
        Names of signals to weight equally.

    Returns
    -------
    dict[str, float]
        Mapping from signal names to equal weights (each = 1/N).

    Raises
    ------
    ValueError
        If signal_names is empty.

    Examples
    --------
    >>> compute_equal_weights(["basis", "momentum", "gap"])
    {"basis": 0.333..., "momentum": 0.333..., "gap": 0.333...}
    """
    if not signal_names:
        raise ValueError("signal_names cannot be empty")

    weight = 1.0 / len(signal_names)
    return {name: weight for name in signal_names}


def aggregate_signals(
    signals: dict[str, pd.Series],
    weights: dict[str, float] | None = None,
) -> pd.Series:
    """
    Combine individual signals into weighted composite positioning score.

    The composite score represents net directional bias:
    - Positive values suggest long credit risk (buy CDX, sell protection)
    - Negative values suggest short credit risk (sell CDX, buy protection)

    Parameters
    ----------
    signals : dict[str, pd.Series]
        Mapping from signal names to z-score normalized signal series.
        Example: {"cdx_etf_basis": basis_series, "cdx_vix_gap": gap_series}
    weights : dict[str, float] | None, default None
        Mapping from signal names to weights (must sum to 1.0).
        All keys must exist in signals dict.
        If None, equal weights are computed automatically (1/N for N signals).

    Returns
    -------
    pd.Series
        Composite positioning score aligned to common index.

    Raises
    ------
    KeyError
        If any weight key does not have a corresponding signal.

    Notes
    -----
    - All input signals must be z-score normalized for comparability.
    - All signals follow convention: positive = long credit risk.
    - Missing values in any signal result in NaN for that date.
    - The composite score is NOT re-normalized to preserve interpretability.
    - Typical operating range is -3 to +3 (z-score units).

    Examples
    --------
    >>> signals = {"basis": basis_series, "momentum": mom_series}
    >>> # Equal weights (default)
    >>> composite = aggregate_signals(signals)
    >>> # Custom weights
    >>> weights = {"basis": 0.6, "momentum": 0.4}
    >>> composite = aggregate_signals(signals, weights)
    """
    # Use equal weights if not provided
    if weights is None:
        weights = compute_equal_weights(list(signals.keys()))
        logger.debug("Using equal weights for %d signals", len(weights))

    # Validate all weights have corresponding signals
    missing_signals = set(weights.keys()) - set(signals.keys())
    if missing_signals:
        raise KeyError(
            f"Signals missing for weights: {sorted(missing_signals)}. "
            f"Available signals: {sorted(signals.keys())}"
        )

    logger.info(
        "Aggregating %d signals: %s",
        len(weights),
        ", ".join(f"{name}={weight:.2f}" for name, weight in sorted(weights.items())),
    )

    # Align all signals to common index
    aligned = pd.DataFrame(signals)

    # Compute weighted average
    composite = pd.Series(0.0, index=aligned.index)
    for signal_name, weight in weights.items():
        composite += aligned[signal_name] * weight

    valid_count = composite.notna().sum()
    mean_score = composite.mean()
    std_score = composite.std()

    logger.info(
        "Composite signal: valid_obs=%d, mean=%.3f, std=%.3f",
        valid_count,
        mean_score,
        std_score,
    )

    return composite
