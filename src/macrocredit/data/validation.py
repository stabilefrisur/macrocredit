"""
Data validation utilities for market data quality checks.

Validates schema compliance, data types, and business logic constraints.
"""

import logging

import pandas as pd

from .schemas import CDXSchema, VIXSchema, ETFSchema

logger = logging.getLogger(__name__)


def validate_cdx_schema(df: pd.DataFrame, schema: CDXSchema = CDXSchema()) -> pd.DataFrame:
    """
    Validate CDX index data against expected schema.

    Parameters
    ----------
    df : pd.DataFrame
        Raw CDX data to validate.
    schema : CDXSchema, default CDXSchema()
        Schema definition with column names and constraints.

    Returns
    -------
    pd.DataFrame
        Validated DataFrame with DatetimeIndex.

    Raises
    ------
    ValueError
        If required columns are missing or data violates constraints.

    Notes
    -----
    - Converts date column to DatetimeIndex
    - Validates spread values are within bounds
    - Checks for duplicate dates per index
    """
    logger.info("Validating CDX schema: %d rows", len(df))

    # Check required columns (except date if already indexed)
    required_cols = list(schema.required_cols)
    if isinstance(df.index, pd.DatetimeIndex):
        # Already has DatetimeIndex, don't require date column
        required_cols = [col for col in required_cols if col != schema.date_col]

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Validate spread bounds
    if not df[schema.spread_col].between(schema.min_spread, schema.max_spread).all():
        invalid = df[
            ~df[schema.spread_col].between(schema.min_spread, schema.max_spread)
        ]
        logger.warning(
            "Found %d invalid spread values outside [%.1f, %.1f]",
            len(invalid),
            schema.min_spread,
            schema.max_spread,
        )
        raise ValueError(f"Spread values outside valid range: {invalid.head()}")

    # Convert date to index
    if not isinstance(df.index, pd.DatetimeIndex):
        df = df.copy()
        df[schema.date_col] = pd.to_datetime(df[schema.date_col])
        df = df.set_index(schema.date_col)

    # Check for duplicates
    if df.index.duplicated().any():
        n_dups = df.index.duplicated().sum()
        logger.warning("Found %d duplicate dates", n_dups)

    # Sort by date
    df = df.sort_index()

    logger.debug("CDX validation passed: date_range=%s to %s", df.index.min(), df.index.max())
    return df


def validate_vix_schema(df: pd.DataFrame, schema: VIXSchema = VIXSchema()) -> pd.DataFrame:
    """
    Validate VIX volatility data against expected schema.

    Parameters
    ----------
    df : pd.DataFrame
        Raw VIX data to validate.
    schema : VIXSchema, default VIXSchema()
        Schema definition with column names and constraints.

    Returns
    -------
    pd.DataFrame
        Validated DataFrame with DatetimeIndex.

    Raises
    ------
    ValueError
        If required columns are missing or data violates constraints.
    """
    logger.info("Validating VIX schema: %d rows", len(df))

    # Check required columns (except date if already indexed)
    required_cols = list(schema.required_cols)
    if isinstance(df.index, pd.DatetimeIndex):
        # Already has DatetimeIndex, don't require date column
        required_cols = [col for col in required_cols if col != schema.date_col]

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Validate VIX bounds
    if not df[schema.close_col].between(schema.min_vix, schema.max_vix).all():
        invalid = df[~df[schema.close_col].between(schema.min_vix, schema.max_vix)]
        logger.warning(
            "Found %d invalid VIX values outside [%.1f, %.1f]",
            len(invalid),
            schema.min_vix,
            schema.max_vix,
        )
        raise ValueError(f"VIX values outside valid range: {invalid.head()}")

    # Convert date to index
    if not isinstance(df.index, pd.DatetimeIndex):
        df = df.copy()
        df[schema.date_col] = pd.to_datetime(df[schema.date_col])
        df = df.set_index(schema.date_col)

    # Check for duplicates
    if df.index.duplicated().any():
        n_dups = df.index.duplicated().sum()
        logger.warning("Found %d duplicate dates", n_dups)
        df = df[~df.index.duplicated(keep="first")]

    # Sort by date
    df = df.sort_index()

    logger.debug("VIX validation passed: date_range=%s to %s", df.index.min(), df.index.max())
    return df


def validate_etf_schema(df: pd.DataFrame, schema: ETFSchema = ETFSchema()) -> pd.DataFrame:
    """
    Validate credit ETF data against expected schema.

    Parameters
    ----------
    df : pd.DataFrame
        Raw ETF data to validate.
    schema : ETFSchema, default ETFSchema()
        Schema definition with column names and constraints.

    Returns
    -------
    pd.DataFrame
        Validated DataFrame with DatetimeIndex.

    Raises
    ------
    ValueError
        If required columns are missing or data violates constraints.
    """
    logger.info("Validating ETF schema: %d rows", len(df))

    # Check required columns (except date if already indexed)
    required_cols = list(schema.required_cols)
    if isinstance(df.index, pd.DatetimeIndex):
        # Already has DatetimeIndex, don't require date column
        required_cols = [col for col in required_cols if col != schema.date_col]

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Validate price bounds
    if not df[schema.close_col].between(schema.min_price, schema.max_price).all():
        invalid = df[~df[schema.close_col].between(schema.min_price, schema.max_price)]
        logger.warning(
            "Found %d invalid price values outside [%.1f, %.1f]",
            len(invalid),
            schema.min_price,
            schema.max_price,
        )
        raise ValueError(f"Price values outside valid range: {invalid.head()}")

    # Convert date to index
    if not isinstance(df.index, pd.DatetimeIndex):
        df = df.copy()
        df[schema.date_col] = pd.to_datetime(df[schema.date_col])
        df = df.set_index(schema.date_col)

    # Check for duplicates per ticker
    if schema.ticker_col in df.columns:
        for ticker in df[schema.ticker_col].unique():
            ticker_df = df[df[schema.ticker_col] == ticker]
            if ticker_df.index.duplicated().any():
                n_dups = ticker_df.index.duplicated().sum()
                logger.warning("Found %d duplicate dates for ticker %s", n_dups, ticker)

    # Sort by date
    df = df.sort_index()

    logger.debug("ETF validation passed: date_range=%s to %s", df.index.min(), df.index.max())
    return df
