"""
Models Layer Demonstration - Signal Generation and Aggregation

Demonstrates the complete signal generation workflow:
1. Generate synthetic CDX, VIX, and ETF market data (252 trading days)
2. Compute three individual signals:
   - CDX-ETF basis: Arbitrage signal from cash-derivative spread
   - CDX-VIX gap: Cross-asset risk sentiment divergence
   - Spread momentum: Short-term trend in credit spreads
3. Aggregate signals with custom weights into composite score
4. Generate position recommendations from composite score

Output: Signal statistics, position distribution, and sample recommendations

Note: All signals follow the convention:
  - Positive values → Long credit risk (buy CDX/sell protection)
  - Negative values → Short credit risk (sell CDX/buy protection)
"""

import logging
import pandas as pd

from example_data import generate_example_data
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
        # Signal convention: positive = long credit risk (buy CDX)
        #                    negative = short credit risk (sell CDX)
        if score > threshold:
            return "long_credit"
        if score < -threshold:
            return "short_credit"
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
    cdx_df, vix_df, etf_df = generate_example_data(periods=252)

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
