"""Example usage of the persistence layer."""

import logging
import pandas as pd
import numpy as np
from datetime import datetime

from macrocredit.persistence import (
    save_parquet,
    load_parquet,
    save_json,
    load_json,
    DataRegistry,
)
from macrocredit.config import DATA_DIR, REGISTRY_PATH


# Configure logging for the demo
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)


def create_sample_data() -> None:
    """
    Create sample market data files for demonstration.

    Generates synthetic CDX spread, VIX, and ETF data and saves to Parquet.
    """
    print("Creating sample market data...")

    # Generate date range
    dates = pd.date_range("2024-01-01", "2024-10-25", freq="B")  # Business days

    # CDX IG 5Y spreads
    cdx_ig_5y = pd.DataFrame(
        {
            "spread": 70 + np.random.normal(0, 5, len(dates)).cumsum() * 0.5,
            "volume": np.random.randint(1000, 5000, len(dates)),
        },
        index=dates,
    )
    save_parquet(cdx_ig_5y, DATA_DIR / "raw" / "cdx_ig_5y.parquet")
    print(f"  ✓ Saved CDX IG 5Y: {len(cdx_ig_5y)} rows")

    # CDX HY 5Y spreads
    cdx_hy_5y = pd.DataFrame(
        {
            "spread": 350 + np.random.normal(0, 20, len(dates)).cumsum() * 0.8,
            "volume": np.random.randint(500, 2000, len(dates)),
        },
        index=dates,
    )
    save_parquet(cdx_hy_5y, DATA_DIR / "raw" / "cdx_hy_5y.parquet")
    print(f"  ✓ Saved CDX HY 5Y: {len(cdx_hy_5y)} rows")

    # VIX index
    vix = pd.DataFrame(
        {
            "close": 15 + np.random.normal(0, 3, len(dates)).cumsum() * 0.3,
            "volume": np.random.randint(50000, 200000, len(dates)),
        },
        index=dates,
    )
    save_parquet(vix, DATA_DIR / "raw" / "vix.parquet")
    print(f"  ✓ Saved VIX: {len(vix)} rows")

    # HYG ETF
    hyg = pd.DataFrame(
        {
            "close": 80 + np.random.normal(0, 0.5, len(dates)).cumsum() * 0.1,
            "volume": np.random.randint(5000000, 15000000, len(dates)),
        },
        index=dates,
    )
    save_parquet(hyg, DATA_DIR / "raw" / "hyg_etf.parquet")
    print(f"  ✓ Saved HYG ETF: {len(hyg)} rows")


def register_datasets() -> None:
    """
    Register all datasets in the central registry.

    Creates a DataRegistry and registers all available market data files
    with appropriate metadata.
    """
    print("\nRegistering datasets...")

    registry = DataRegistry(REGISTRY_PATH, DATA_DIR)

    # Register CDX instruments
    registry.register_dataset(
        name="cdx_ig_5y",
        file_path=DATA_DIR / "raw" / "cdx_ig_5y.parquet",
        instrument="CDX.NA.IG",
        tenor="5Y",
        metadata={"source": "synthetic", "frequency": "daily"},
    )

    registry.register_dataset(
        name="cdx_hy_5y",
        file_path=DATA_DIR / "raw" / "cdx_hy_5y.parquet",
        instrument="CDX.NA.HY",
        tenor="5Y",
        metadata={"source": "synthetic", "frequency": "daily"},
    )

    # Register market data
    registry.register_dataset(
        name="vix",
        file_path=DATA_DIR / "raw" / "vix.parquet",
        instrument="VIX",
        metadata={"source": "synthetic", "frequency": "daily"},
    )

    registry.register_dataset(
        name="hyg_etf",
        file_path=DATA_DIR / "raw" / "hyg_etf.parquet",
        instrument="HYG",
        metadata={"source": "synthetic", "frequency": "daily", "type": "ETF"},
    )

    print(f"  ✓ Registered {len(registry.list_datasets())} datasets")


def demonstrate_registry_usage() -> None:
    """Demonstrate registry query and filtering capabilities."""
    print("\nDemonstrating registry queries...")

    registry = DataRegistry(REGISTRY_PATH, DATA_DIR)

    # List all datasets
    all_datasets = registry.list_datasets()
    print(f"  Total datasets: {len(all_datasets)}")

    # Filter by CDX instruments
    cdx_datasets = [d for d in all_datasets if "cdx" in d]
    print(f"  CDX instruments: {cdx_datasets}")

    # Get detailed info
    info = registry.get_dataset_info("cdx_ig_5y")
    print(f"\n  CDX IG 5Y details:")
    print(f"    Date range: {info['start_date'][:10]} to {info['end_date'][:10]}")
    print(f"    Rows: {info['row_count']}")
    print(f"    Tenor: {info['tenor']}")


def demonstrate_data_loading() -> None:
    """Demonstrate data loading with filters."""
    print("\nDemonstrating data loading...")

    # Load full dataset
    cdx_ig = load_parquet(DATA_DIR / "raw" / "cdx_ig_5y.parquet")
    print(f"  Loaded full CDX IG dataset: {len(cdx_ig)} rows")

    # Load with date filter
    recent = load_parquet(
        DATA_DIR / "raw" / "cdx_ig_5y.parquet",
        start_date=pd.Timestamp("2024-10-01"),
    )
    print(f"  Loaded recent data (Oct 2024): {len(recent)} rows")

    # Load specific columns
    spreads_only = load_parquet(
        DATA_DIR / "raw" / "cdx_ig_5y.parquet",
        columns=["spread"],
    )
    print(f"  Loaded spread column only: {spreads_only.columns.tolist()}")


def save_run_metadata() -> None:
    """Save example run metadata to JSON."""
    print("\nSaving run metadata...")

    metadata = {
        "run_id": "demo_20241025",
        "timestamp": datetime.now(),
        "parameters": {
            "momentum_window": 5,
            "volatility_window": 20,
            "instruments": ["CDX.IG.5Y", "CDX.HY.5Y"],
        },
        "data_version": "0.1.0",
        "output_path": DATA_DIR / "processed" / "signals.parquet",
    }

    output_path = save_json(metadata, DATA_DIR / "logs" / "run_metadata.json")
    print(f"  ✓ Saved metadata to {output_path}")

    # Load it back
    loaded = load_json(output_path)
    print(f"  ✓ Verified: Run ID = {loaded['run_id']}")


def main() -> None:
    """Run all persistence layer demonstrations."""
    print("=" * 60)
    print("Persistence Layer Demo")
    print("=" * 60)

    create_sample_data()
    register_datasets()
    demonstrate_registry_usage()
    demonstrate_data_loading()
    save_run_metadata()

    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
