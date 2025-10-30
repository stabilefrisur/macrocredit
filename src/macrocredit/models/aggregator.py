"""Signal aggregation logic for combining multiple signals into composite positioning score.
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def aggregate_signals(
    signals: dict[str, pd.Series],
    weights: dict[str, float],
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
    weights : dict[str, float]
        Mapping from signal names to weights (must sum to 1.0).
        All keys must exist in signals dict.

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
    >>> weights = {"basis": 0.6, "momentum": 0.4}
    >>> composite = aggregate_signals(signals, weights)
    """
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
