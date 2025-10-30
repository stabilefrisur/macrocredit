"""
Models Layer Demonstration - Signal Registry Pattern

Demonstrates the scalable signal generation workflow using registry pattern:
1. Load signal catalog from JSON
2. Generate synthetic CDX, VIX, and ETF market data (252 trading days)
3. Compute all enabled signals using registry orchestration
4. Aggregate signals dynamically with configurable weights
5. Generate position recommendations from composite score

The registry pattern enables:
- Adding new signals without changing code (just update catalog JSON)
- Enabling/disabling signals for experimentation
- Dynamic signal composition with arbitrary weights
- Centralized signal metadata and documentation

Output: Signal statistics, position distribution, and sample recommendations

Note: All signals follow the convention:
  - Positive values → Long credit risk (buy CDX/sell protection)
  - Negative values → Short credit risk (sell CDX/buy protection)
"""

import logging
from pathlib import Path
import pandas as pd

from example_data import generate_example_data
from macrocredit.models import (
    SignalRegistry,
    SignalConfig,
    AggregatorConfig,
    compute_registered_signals,
    aggregate_signals,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the models layer demonstration."""
    logger.info("=== Models Layer Demo (Registry Pattern) ===")

    # Load signal registry from catalog (path relative to project root)
    catalog_path = Path(__file__).parent.parent / "src/macrocredit/models/signal_catalog.json"
    registry = SignalRegistry(catalog_path)
    
    logger.info("\n=== Signal Catalog ===")
    enabled_signals = registry.get_enabled()
    for name, metadata in enabled_signals.items():
        logger.info(
            "Signal: %s\n  %s",
            name,
            metadata.description,
        )

    # Generate synthetic data
    logger.info("\n=== Generating Market Data ===")
    cdx_df, vix_df, etf_df = generate_example_data(periods=252)
    
    market_data = {
        "cdx": cdx_df,
        "vix": vix_df,
        "etf": etf_df,
    }

    # Compute all registered signals
    logger.info("\n=== Computing Signals ===")
    signal_config = SignalConfig(lookback=20, min_periods=10)
    signals = compute_registered_signals(registry, market_data, signal_config)
    
    # Display signal statistics
    logger.info("\n=== Individual Signal Statistics ===")
    for name, signal in signals.items():
        valid = signal.dropna()
        logger.info(
            "%s: valid=%d, mean=%.3f, std=%.3f, range=[%.3f, %.3f]",
            name,
            len(valid),
            valid.mean(),
            valid.std(),
            valid.min(),
            valid.max(),
        )

    # Demonstrate equal-weight aggregation (default)
    logger.info("\n=== Equal-Weight Aggregation (Default) ===")
    signal_names = list(enabled_signals.keys())
    logger.info("Using equal weights for %d signals: %s", len(signal_names), signal_names)
    
    # Create aggregator config with equal weights
    agg_config = AggregatorConfig(signal_names=signal_names)
    logger.info("Computed weights: %s", agg_config.signal_weights)
    
    # Aggregate signals (can omit weights parameter for equal-weight)
    composite = aggregate_signals(signals)

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

    # Display sample results
    logger.info("\n=== Sample Results (Last 10 Days) ===")
    print(result.tail(10).to_string())

    # Summary statistics
    valid_composite = composite.dropna()
    logger.info(
        "\n=== Composite Signal Summary ===\n"
        "Valid observations: %d\n"
        "Mean: %.3f\n"
        "Std: %.3f\n"
        "Min: %.3f\n"
        "Max: %.3f",
        len(valid_composite),
        valid_composite.mean(),
        valid_composite.std(),
        valid_composite.min(),
        valid_composite.max(),
    )

    # Demonstrate custom weight experiment
    logger.info("\n=== Custom Weight Experiment ===")
    custom_weights = {
        "cdx_etf_basis": 0.50,
        "cdx_vix_gap": 0.30,
        "spread_momentum": 0.20,
    }
    logger.info("Testing custom weights: %s", custom_weights)
    
    custom_composite = aggregate_signals(signals, custom_weights)
    custom_valid = custom_composite.dropna()
    
    logger.info(
        "Custom composite: mean=%.3f, std=%.3f",
        custom_valid.mean(),
        custom_valid.std(),
    )

    logger.info("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
