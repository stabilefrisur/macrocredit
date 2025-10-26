"""
Demonstration of data layer functionality.

Generates sample data, loads it, transforms it, and shows usage patterns.
"""

import logging
from pathlib import Path

from macrocredit.data.sample_data import generate_full_sample_dataset
from macrocredit.data import (
    load_cdx_data,
    load_vix_data,
    load_etf_data,
    load_all_data,
    compute_spread_changes,
    compute_returns,
    align_multiple_series,
    compute_rolling_zscore,
)
from macrocredit.persistence import save_parquet

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run data layer demonstration."""
    logger.info("Starting data layer demonstration")

    # Generate sample data
    logger.info("Generating sample dataset...")
    file_paths = generate_full_sample_dataset(
        output_dir="data/raw",
        start_date="2023-01-01",
        periods=252,
        seed=42,
    )

    logger.info("Sample data files created:")
    for data_type, path in file_paths.items():
        logger.info("  %s: %s", data_type, path)

    # Load individual data sources
    logger.info("\nLoading data sources individually...")

    cdx_ig = load_cdx_data(file_paths["cdx"], index_name="CDX_IG_5Y")
    logger.info("CDX IG loaded: %d rows, spread_mean=%.2f", len(cdx_ig), cdx_ig["spread"].mean())

    vix = load_vix_data(file_paths["vix"])
    logger.info("VIX loaded: %d rows, vix_mean=%.2f", len(vix), vix["close"].mean())

    hyg = load_etf_data(file_paths["etf"], ticker="HYG")
    logger.info("HYG loaded: %d rows, price_mean=%.2f", len(hyg), hyg["close"].mean())

    # Load all data at once
    logger.info("\nLoading all data at once...")
    data = load_all_data(
        cdx_path=file_paths["cdx"],
        vix_path=file_paths["vix"],
        etf_path=file_paths["etf"],
    )
    logger.info("All data loaded: cdx=%d, vix=%d, etf=%d",
                len(data["cdx"]), len(data["vix"]), len(data["etf"]))

    # Demonstrate transformations
    logger.info("\nDemonstrating transformations...")

    # Compute spread changes
    spread_changes = compute_spread_changes(cdx_ig["spread"], window=1, method="diff")
    logger.info("Spread changes computed: mean=%.2f bp", spread_changes.mean())

    # Compute VIX returns
    vix_returns = compute_returns(vix["close"], window=1, log_returns=False)
    logger.info("VIX returns computed: mean=%.4f", vix_returns.mean())

    # Compute ETF returns
    hyg_returns = compute_returns(hyg["close"], window=1, log_returns=False)
    logger.info("HYG returns computed: mean=%.4f", hyg_returns.mean())

    # Align multiple series
    logger.info("\nAligning multiple series...")
    cdx_spread_aligned, vix_close_aligned = align_multiple_series(
        cdx_ig["spread"],
        vix["close"],
        method="inner",
    )
    logger.info("Aligned series: %d common dates", len(cdx_spread_aligned))

    # Compute rolling z-scores for signal normalization
    logger.info("\nComputing rolling z-scores...")
    spread_zscore = compute_rolling_zscore(spread_changes, window=20)
    logger.info("Spread z-score: mean=%.2f, std=%.2f",
                spread_zscore.mean(), spread_zscore.std())

    vix_zscore = compute_rolling_zscore(vix_returns, window=20)
    logger.info("VIX z-score: mean=%.2f, std=%.2f",
                vix_zscore.mean(), vix_zscore.std())

    # Save processed data
    logger.info("\nSaving processed data...")
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Combine processed signals
    import pandas as pd
    processed = pd.DataFrame({
        "spread": cdx_spread_aligned,
        "spread_change": spread_changes.reindex(cdx_spread_aligned.index),
        "spread_zscore": spread_zscore.reindex(cdx_spread_aligned.index),
        "vix": vix_close_aligned,
        "vix_return": vix_returns.reindex(vix_close_aligned.index),
        "vix_zscore": vix_zscore.reindex(vix_close_aligned.index),
    })

    output_path = processed_dir / "aligned_signals.parquet"
    save_parquet(processed, output_path)
    logger.info("Processed data saved to: %s", output_path)

    # Summary statistics
    logger.info("\nSummary statistics:")
    logger.info("Dataset period: %s to %s",
                processed.index.min().date(),
                processed.index.max().date())
    logger.info("Total observations: %d", len(processed))
    logger.info("Missing values: %d", processed.isna().sum().sum())

    logger.info("\nData layer demonstration complete!")


if __name__ == "__main__":
    main()
