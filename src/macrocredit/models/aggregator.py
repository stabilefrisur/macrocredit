"""
Signal aggregation logic for combining multiple signals into composite positioning score.
"""

import logging
import pandas as pd

from .config import AggregatorConfig

logger = logging.getLogger(__name__)


def aggregate_signals(
    cdx_etf_basis: pd.Series,
    cdx_vix_gap: pd.Series,
    spread_momentum: pd.Series,
    config: AggregatorConfig | None = None,
) -> pd.Series:
    """
    Combine individual signals into weighted composite positioning score.

    The composite score represents net directional bias:
    - Positive values suggest long credit risk (buy CDX, sell protection)
    - Negative values suggest short credit risk (sell CDX, buy protection)
    - Values below threshold suggest neutral positioning

    Parameters
    ----------
    cdx_etf_basis : pd.Series
        CDX-ETF basis signal (z-score normalized).
    cdx_vix_gap : pd.Series
        CDX-VIX gap signal (z-score normalized).
    spread_momentum : pd.Series
        Spread momentum signal (z-score normalized).
    config : AggregatorConfig | None
        Aggregation weights and threshold. Uses defaults if None.

    Returns
    -------
    pd.Series
        Composite positioning score aligned to common index.

    Notes
    -----
    - All input signals must be z-score normalized for comparability.
    - All signals follow convention: positive = long credit risk.
    - Missing values in any signal result in NaN for that date.
    - The composite score is NOT re-normalized to preserve interpretability.
    - Typical operating range is -3 to +3 (z-score units).

    Examples
    --------
    >>> config = AggregatorConfig(cdx_etf_basis_weight=0.4, cdx_vix_gap_weight=0.4,
    ...                          spread_momentum_weight=0.2, threshold=1.5)
    >>> composite = aggregate_signals(basis, gap, mom, config)
    >>> positions = composite.apply(lambda x: 'long_credit' if x > 1.5 else
    ...                             'short_credit' if x < -1.5 else 'neutral')
    """
    if config is None:
        config = AggregatorConfig()

    logger.info(
        "Aggregating signals: basis_weight=%.2f, vix_weight=%.2f, mom_weight=%.2f",
        config.cdx_etf_basis_weight,
        config.cdx_vix_gap_weight,
        config.spread_momentum_weight,
    )

    # Align all signals to common index
    aligned = pd.DataFrame(
        {
            "cdx_etf_basis": cdx_etf_basis,
            "cdx_vix_gap": cdx_vix_gap,
            "spread_momentum": spread_momentum,
        }
    )

    # Compute weighted average
    composite = (
        aligned["cdx_etf_basis"] * config.cdx_etf_basis_weight
        + aligned["cdx_vix_gap"] * config.cdx_vix_gap_weight
        + aligned["spread_momentum"] * config.spread_momentum_weight
    )

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
