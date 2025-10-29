"""
Data Layer Demonstration - Loading, Validation, and Caching

Demonstrates the data layer workflow for market data:
1. Generate synthetic CDX, VIX, and ETF market data
2. Save data to Parquet files in data/raw/
3. Load data with automatic schema validation:
   - CDX index spreads (validate_cdx_schema)
   - VIX volatility levels (validate_vix_schema)
   - ETF prices (validate_etf_schema)
4. Demonstrate caching behavior (second fetch uses cache)
5. Display summary statistics and data quality metrics

Output: Validated DataFrames with DatetimeIndex and quality metrics

Key Features:
  - Type-safe loading with DatetimeIndex enforcement
  - Schema validation (required columns, data types)
  - Business logic checks (spread/price bounds)
  - Transparent caching for repeated fetches
  - Clean separation of data layer from models layer
"""

import logging

from macrocredit.data.sample_data import generate_full_sample_sources
from macrocredit.data import (
    fetch_cdx,
    fetch_vix,
    fetch_etf,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run data layer demonstration."""
    logger.info("Starting data layer demonstration")

    # Generate sample data and get FileSource configs
    logger.info("Generating sample dataset...")
    sources = generate_full_sample_sources(
        output_dir="data/raw",
        start_date="2023-01-01",
        periods=252,
        seed=42,
    )

    logger.info("Sample data sources created:")
    for data_type, source in sources.items():
        logger.info("  %s: %s", data_type, source.path)

    # Fetch individual data sources
    logger.info("\nFetching data sources individually...")

    cdx_ig = fetch_cdx(sources["cdx"], index_name="CDX_IG_5Y")
    logger.info("CDX IG fetched: %d rows, spread_mean=%.2f", len(cdx_ig), cdx_ig["spread"].mean())

    vix = fetch_vix(sources["vix"])
    logger.info("VIX fetched: %d rows, vix_mean=%.2f", len(vix), vix["close"].mean())

    hyg = fetch_etf(sources["etf"], ticker="HYG")
    logger.info("HYG fetched: %d rows, price_mean=%.2f", len(hyg), hyg["close"].mean())

    # Demonstrate caching by fetching again
    logger.info("\nDemonstrating cache functionality...")
    cdx_ig_cached = fetch_cdx(sources["cdx"], index_name="CDX_IG_5Y")
    logger.info("CDX IG from cache: %d rows", len(cdx_ig_cached))

    # Display summary statistics
    logger.info("\nData Quality Summary:")
    logger.info("CDX IG: %d rows, date_range=%s to %s",
                len(cdx_ig),
                cdx_ig.index.min().date(),
                cdx_ig.index.max().date())
    logger.info("  spread: mean=%.2f, min=%.2f, max=%.2f",
                cdx_ig["spread"].mean(),
                cdx_ig["spread"].min(),
                cdx_ig["spread"].max())

    logger.info("VIX: %d rows, date_range=%s to %s",
                len(vix),
                vix.index.min().date(),
                vix.index.max().date())
    logger.info("  close: mean=%.2f, min=%.2f, max=%.2f",
                vix["close"].mean(),
                vix["close"].min(),
                vix["close"].max())

    logger.info("HYG ETF: %d rows, date_range=%s to %s",
                len(hyg),
                hyg.index.min().date(),
                hyg.index.max().date())
    logger.info("  close: mean=%.2f, min=%.2f, max=%.2f",
                hyg["close"].mean(),
                hyg["close"].min(),
                hyg["close"].max())

    # Validate data integrity
    logger.info("\nData Integrity Checks:")
    logger.info("CDX missing values: %d", cdx_ig.isna().sum().sum())
    logger.info("VIX missing values: %d", vix.isna().sum().sum())
    logger.info("HYG missing values: %d", hyg.isna().sum().sum())

    logger.info("\nData layer demonstration complete!")


if __name__ == "__main__":
    main()
