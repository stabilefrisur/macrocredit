"""
Models Layer Demonstration - Single Signal Workflow

Demonstrates individual signal generation workflow:
1. Generate synthetic CDX and ETF market data (252 trading days)
2. Compute cdx_etf_basis signal with configurable parameters
3. Analyze signal statistics and characteristics
4. Generate position recommendations from signal

The cdx_etf_basis signal identifies relative value opportunities between
credit index (CDX) and credit ETF markets by measuring basis divergence.

Output: Signal statistics, position distribution, and sample recommendations

Note: Signals follow the convention:
  - Positive values → Long credit risk (buy CDX/sell protection)
  - Negative values → Short credit risk (sell CDX/buy protection)
"""

import logging
from pathlib import Path
import pandas as pd

from example_data import generate_example_data
from macrocredit.models import (
    compute_cdx_etf_basis,
    SignalConfig,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the models layer demonstration."""
    logger.info("=== Models Layer Demo (Single Signal) ===")

    # Generate synthetic data
    logger.info("\n=== Generating Market Data ===")
    cdx_df, vix_df, etf_df = generate_example_data(periods=252)
    logger.info("Generated %d days of data", len(cdx_df))

    # Compute cdx_etf_basis signal
    logger.info("\n=== Computing cdx_etf_basis Signal ===")
    signal_config = SignalConfig(lookback=20, min_periods=10)
    
    signal = compute_cdx_etf_basis(cdx_df, etf_df, signal_config)
    
    # Display signal statistics
    logger.info("\n=== Signal Statistics ===")
    valid = signal.dropna()
    logger.info(
        "cdx_etf_basis: valid=%d, mean=%.3f, std=%.3f, range=[%.3f, %.3f]",
        len(valid),
        valid.mean(),
        valid.std(),
        valid.min(),
        valid.max(),
    )

    # Generate positions
    threshold = 1.5
    logger.info("\n=== Generating Positions (threshold=%.2f) ===", threshold)

    def classify_position(score: float) -> str:
        if pd.isna(score):
            return "no_signal"
        if score > threshold:
            return "long_credit"
        if score < -threshold:
            return "short_credit"
        return "neutral"

    positions = signal.apply(classify_position)
    
    result = pd.DataFrame(
        {
            "signal_score": signal,
            "position": positions,
        }
    )

    # Position distribution
    pos_counts = result["position"].value_counts()
    logger.info("Position distribution:\n%s", pos_counts)

    # Display sample results
    logger.info("\n=== Sample Results (Last 10 Days) ===")
    print(result.tail(10).to_string())

    # Summary statistics
    logger.info(
        "\n=== Signal Summary ===\n"
        "Valid observations: %d\n"
        "Mean: %.3f\n"
        "Std: %.3f\n"
        "Min: %.3f\n"
        "Max: %.3f",
        len(valid),
        valid.mean(),
        valid.std(),
        valid.min(),
        valid.max(),
    )

    logger.info("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
