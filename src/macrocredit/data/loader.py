"""
Data loaders for CDX, VIX, and ETF market data.

Handles Parquet and CSV ingestion with automatic schema validation and cleaning.
Uses the persistence layer for standardized I/O operations.
"""

import logging
from pathlib import Path

import pandas as pd

from ..persistence.parquet_io import load_parquet
from .validation import validate_cdx_schema, validate_vix_schema, validate_etf_schema

logger = logging.getLogger(__name__)


def load_cdx_data(
    file_path: str | Path,
    index_name: str | None = None,
    tenor: str | None = None,
) -> pd.DataFrame:
    """
    Load CDX index spread data from Parquet or CSV.

    Parameters
    ----------
    file_path : str | Path
        Path to CDX data file (Parquet or CSV).
    index_name : str | None, optional
        Filter to specific index (e.g., "CDX_IG", "CDX_HY").
    tenor : str | None, optional
        Filter to specific tenor (e.g., "5Y", "10Y").

    Returns
    -------
    pd.DataFrame
        Validated CDX data with DatetimeIndex and columns:
        - spread: CDX spread in basis points
        - index: Index identifier (if present)
        - tenor: Tenor identifier (if present)

    Notes
    -----
    - Automatically detects file format from extension
    - Validates schema and data quality
    - Returns data sorted by date
    """
    file_path = Path(file_path)
    logger.info("Loading CDX data from %s", file_path)

    # Load based on file type
    if file_path.suffix == ".parquet":
        df = load_parquet(file_path)
    elif file_path.suffix == ".csv":
        df = pd.read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

    # Validate schema
    df = validate_cdx_schema(df)

    # Apply filters
    if index_name is not None:
        if "index" not in df.columns:
            raise ValueError("Cannot filter by index_name: 'index' column not found")
        df = df[df["index"] == index_name]
        logger.debug("Filtered to index=%s: %d rows remaining", index_name, len(df))

    if tenor is not None:
        if "tenor" not in df.columns:
            raise ValueError("Cannot filter by tenor: 'tenor' column not found")
        df = df[df["tenor"] == tenor]
        logger.debug("Filtered to tenor=%s: %d rows remaining", tenor, len(df))

    logger.info(
        "Loaded CDX data: %d rows, date_range=%s to %s",
        len(df),
        df.index.min(),
        df.index.max(),
    )
    return df


def load_vix_data(file_path: str | Path) -> pd.DataFrame:
    """
    Load VIX volatility index data from Parquet or CSV.

    Parameters
    ----------
    file_path : str | Path
        Path to VIX data file (Parquet or CSV).

    Returns
    -------
    pd.DataFrame
        Validated VIX data with DatetimeIndex and columns:
        - close: VIX closing level
        - open, high, low: Optional OHLC data

    Notes
    -----
    - VIX represents implied volatility from S&P 500 options
    - Used as equity risk sentiment proxy in cross-asset signals
    """
    file_path = Path(file_path)
    logger.info("Loading VIX data from %s", file_path)

    # Load based on file type
    if file_path.suffix == ".parquet":
        df = load_parquet(file_path)
    elif file_path.suffix == ".csv":
        df = pd.read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

    # Validate schema
    df = validate_vix_schema(df)

    logger.info(
        "Loaded VIX data: %d rows, date_range=%s to %s",
        len(df),
        df.index.min(),
        df.index.max(),
    )
    return df


def load_etf_data(
    file_path: str | Path,
    ticker: str | None = None,
) -> pd.DataFrame:
    """
    Load credit ETF price data from Parquet or CSV.

    Parameters
    ----------
    file_path : str | Path
        Path to ETF data file (Parquet or CSV).
    ticker : str | None, optional
        Filter to specific ticker (e.g., "HYG", "LQD").

    Returns
    -------
    pd.DataFrame
        Validated ETF data with DatetimeIndex and columns:
        - close: Closing price
        - ticker: ETF ticker symbol (if present)
        - volume: Trading volume (if present)

    Notes
    -----
    - ETF data used for signal generation, not direct trading
    - Common tickers: HYG (high yield), LQD (investment grade)
    """
    file_path = Path(file_path)
    logger.info("Loading ETF data from %s", file_path)

    # Load based on file type
    if file_path.suffix == ".parquet":
        df = load_parquet(file_path)
    elif file_path.suffix == ".csv":
        df = pd.read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

    # Validate schema
    df = validate_etf_schema(df)

    # Apply ticker filter
    if ticker is not None:
        if "ticker" not in df.columns:
            raise ValueError("Cannot filter by ticker: 'ticker' column not found")
        df = df[df["ticker"] == ticker]
        logger.debug("Filtered to ticker=%s: %d rows remaining", ticker, len(df))

    logger.info(
        "Loaded ETF data: %d rows, date_range=%s to %s",
        len(df),
        df.index.min(),
        df.index.max(),
    )
    return df


def load_all_data(
    cdx_path: str | Path,
    vix_path: str | Path,
    etf_path: str | Path,
) -> dict[str, pd.DataFrame]:
    """
    Load all market data sources in one call.

    Parameters
    ----------
    cdx_path : str | Path
        Path to CDX data file.
    vix_path : str | Path
        Path to VIX data file.
    etf_path : str | Path
        Path to ETF data file.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary with keys "cdx", "vix", "etf" containing loaded data.

    Notes
    -----
    This is a convenience function for loading all data sources at once.
    Individual loaders can be used for more granular control.
    """
    logger.info("Loading all market data sources")

    data = {
        "cdx": load_cdx_data(cdx_path),
        "vix": load_vix_data(vix_path),
        "etf": load_etf_data(etf_path),
    }

    logger.info("All data loaded successfully")
    return data
