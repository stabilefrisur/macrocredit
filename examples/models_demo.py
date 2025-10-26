"""
Demonstration of the models layer for CDX overlay strategy.

This script shows how to:
1. Generate synthetic market data
2. Compute individual signals
3. Aggregate signals into composite score
4. Generate positioning recommendations
"""

import logging
import numpy as np
import pandas as pd

from macrocredit.models import (
    compute_cdx_etf_basis,
    compute_cdx_vix_gap,
    compute_spread_momentum,
    aggregate_signals,
    SignalConfig,
    AggregatorConfig,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def generate_synthetic_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generate synthetic market data for demonstration.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        CDX, VIX, and ETF dataframes with realistic synthetic data.
    """
    logger.info("Generating synthetic market data")

    dates = pd.date_range("2024-01-01", periods=252, freq="D")
    np.random.seed(42)

    # CDX IG 5Y spreads (random walk with drift)
    cdx_spreads = 100 + np.cumsum(np.random.randn(252) * 2)
    cdx_df = pd.DataFrame({"spread": cdx_spreads}, index=dates)

    # VIX levels (mean-reverting around 15)
    vix_levels = 15 + np.cumsum(np.random.randn(252) * 0.8)
    vix_levels = np.clip(vix_levels, 10, 80)  # Realistic bounds
    vix_df = pd.DataFrame({"close": vix_levels}, index=dates)

    # ETF spread-equivalent (correlated with CDX but with flow noise)
    etf_spreads = cdx_spreads + np.random.randn(252) * 5
    etf_df = pd.DataFrame({"close": etf_spreads}, index=dates)

    logger.info(
        "Generated %d days of data: CDX mean=%.1f, VIX mean=%.1f, ETF mean=%.1f",
        len(dates),
        cdx_spreads.mean(),
        vix_levels.mean(),
        etf_spreads.mean(),
    )

    return cdx_df, vix_df, etf_df


def compute_signals(
    cdx_df: pd.DataFrame,
    vix_df: pd.DataFrame,
    etf_df: pd.DataFrame,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Compute individual strategy signals.

    Parameters
    ----------
    cdx_df : pd.DataFrame
        CDX spread data.
    vix_df : pd.DataFrame
        VIX volatility data.
    etf_df : pd.DataFrame
        ETF spread-equivalent data.

    Returns
    -------
    tuple[pd.Series, pd.Series, pd.Series]
        Basis, gap, and momentum signals.
    """
    logger.info("Computing individual signals")

    config = SignalConfig(lookback=20, min_periods=10)

    basis = compute_cdx_etf_basis(cdx_df, etf_df, config)
    gap = compute_cdx_vix_gap(cdx_df, vix_df, config)
    momentum = compute_spread_momentum(cdx_df, config)

    logger.info(
        "Signal statistics: basis_valid=%d, gap_valid=%d, mom_valid=%d",
        basis.notna().sum(),
        gap.notna().sum(),
        momentum.notna().sum(),
    )

    return basis, gap, momentum


def generate_positions(
    composite: pd.Series,
    threshold: float = 1.0,
) -> pd.DataFrame:
    """
    Convert composite signal to position recommendations.

    Parameters
    ----------
    composite : pd.Series
        Composite positioning score.
    threshold : float
        Z-score threshold for position triggers.

    Returns
    -------
    pd.DataFrame
        Position recommendations with signal levels.
    """
    logger.info("Generating position recommendations with threshold=%.2f", threshold)

    def classify_position(score: float) -> str:
        if pd.isna(score):
            return "no_signal"
        if score > threshold:
            return "short_credit"
        if score < -threshold:
            return "long_credit"
        return "neutral"

    positions = composite.apply(classify_position)

    result = pd.DataFrame(
        {
            "signal_score": composite,
            "position": positions,
        }
    )

    # Position distribution
    pos_counts = result["position"].value_counts()
    logger.info("Position distribution:\n%s", pos_counts)

    return result


def main() -> None:
    """Run the models layer demonstration."""
    logger.info("=== Models Layer Demo ===")

    # Generate synthetic data
    cdx_df, vix_df, etf_df = generate_synthetic_data()

    # Compute individual signals
    basis, gap, momentum = compute_signals(cdx_df, vix_df, etf_df)

    # Aggregate signals
    agg_config = AggregatorConfig(
        cdx_etf_basis_weight=0.35,
        cdx_vix_gap_weight=0.35,
        spread_momentum_weight=0.30,
        threshold=1.5,
    )

    composite = aggregate_signals(basis, gap, momentum, agg_config)

    # Generate positions
    positions = generate_positions(composite, threshold=agg_config.threshold)

    # Display sample results
    logger.info("\n=== Sample Results (Last 10 Days) ===")
    print(positions.tail(10).to_string())

    # Summary statistics
    valid_signals = composite.dropna()
    logger.info(
        "\n=== Composite Signal Summary ===\n"
        "Valid observations: %d\n"
        "Mean: %.3f\n"
        "Std: %.3f\n"
        "Min: %.3f\n"
        "Max: %.3f",
        len(valid_signals),
        valid_signals.mean(),
        valid_signals.std(),
        valid_signals.min(),
        valid_signals.max(),
    )

    logger.info("=== Demo Complete ===")


if __name__ == "__main__":
    main()
