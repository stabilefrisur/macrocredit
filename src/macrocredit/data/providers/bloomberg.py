"""
Bloomberg Terminal/API data provider.

Fetches market data using Bloomberg's Python API via xbbg wrapper.
Requires active Bloomberg Terminal session.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


# Bloomberg field mappings for different instrument types
BLOOMBERG_FIELDS = {
    "cdx": ["PX_LAST", "BID", "ASK", "PX_VOLUME"],  # CDX spread and volume
    "vix": ["PX_LAST", "PX_OPEN", "PX_HIGH", "PX_LOW", "PX_VOLUME"],  # VIX OHLCV
    "etf": ["PX_LAST", "PX_OPEN", "PX_HIGH", "PX_LOW", "PX_VOLUME"],  # ETF OHLCV
}

# Mapping from Bloomberg field names to schema column names
FIELD_MAPPING = {
    "cdx": {
        "PX_LAST": "spread",
        "BID": "bid",
        "ASK": "ask",
        "PX_VOLUME": "volume",
    },
    "vix": {
        "PX_LAST": "close",
        "PX_OPEN": "open",
        "PX_HIGH": "high",
        "PX_LOW": "low",
        "PX_VOLUME": "volume",
    },
    "etf": {
        "PX_LAST": "close",
        "PX_OPEN": "open",
        "PX_HIGH": "high",
        "PX_LOW": "low",
        "PX_VOLUME": "volume",
    },
}


def fetch_from_bloomberg(
    ticker: str,
    instrument: str,
    start_date: str | None = None,
    end_date: str | None = None,
    **params: Any,
) -> pd.DataFrame:
    """
    Fetch historical data from Bloomberg Terminal via xbbg wrapper.

    Parameters
    ----------
    ticker : str
        Bloomberg ticker (e.g., 'CDX.NA.IG.5Y Index', 'VIX Index', 'HYG US Equity').
    instrument : str
        Instrument type for field mapping ('cdx', 'vix', 'etf').
    start_date : str or None, default None
        Start date in YYYY-MM-DD format. Defaults to 5 years ago.
    end_date : str or None, default None
        End date in YYYY-MM-DD format. Defaults to today.
    **params : Any
        Additional Bloomberg request parameters passed to xbbg.

    Returns
    -------
    pd.DataFrame
        Historical data with DatetimeIndex and schema-compatible columns.

    Raises
    ------
    ImportError
        If xbbg is not installed.
    ValueError
        If ticker format is invalid or instrument type is unknown.
    RuntimeError
        If Bloomberg request fails or returns empty data.

    Notes
    -----
    Requires active Bloomberg Terminal session. Connection is handled
    automatically by xbbg wrapper.

    Returned DataFrame columns are mapped to project schemas:
    - CDX: spread, bid, ask, volume, index, tenor
    - VIX: close, open, high, low, volume
    - ETF: close, open, high, low, volume, ticker

    Example tickers:
    - CDX: 'CDX.NA.IG.5Y Index'
    - VIX: 'VIX Index'
    - ETFs: 'HYG US Equity', 'LQD US Equity'
    """
    # Validate instrument type
    if instrument not in BLOOMBERG_FIELDS:
        raise ValueError(
            f"Unknown instrument type: {instrument}. "
            f"Must be one of {list(BLOOMBERG_FIELDS.keys())}"
        )

    # Default to 5-year lookback if dates not provided
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if start_date is None:
        start_dt = datetime.now() - timedelta(days=5 * 365)
        start_date = start_dt.strftime("%Y-%m-%d")

    # Convert dates to Bloomberg format (YYYYMMDD)
    bbg_start = start_date.replace("-", "")
    bbg_end = end_date.replace("-", "")

    logger.info(
        "Fetching %s from Bloomberg: ticker=%s, dates=%s to %s",
        instrument,
        ticker,
        start_date,
        end_date,
    )

    # Import xbbg wrapper
    try:
        from xbbg import blp
    except ImportError:
        raise ImportError(
            "xbbg not installed. "
            "Install with: uv pip install --optional bloomberg"
        )

    # Fetch historical data using xbbg
    fields = BLOOMBERG_FIELDS[instrument]
    try:
        df = blp.bdh(
            tickers=ticker,
            flds=fields,
            start_date=bbg_start,
            end_date=bbg_end,
            **params,
        )
    except Exception as e:
        logger.error("Bloomberg request failed: %s", str(e))
        raise RuntimeError(f"Failed to fetch data from Bloomberg: {e}") from e

    # Check if response is empty
    if df is None or df.empty:
        raise RuntimeError(
            f"Bloomberg returned empty data for {ticker}. "
            "Check ticker format and data availability."
        )

    logger.debug("Fetched %d rows from Bloomberg", len(df))

    # Map Bloomberg field names to schema columns
    df = _map_bloomberg_fields(df, instrument, ticker)

    # Add metadata columns (index, tenor, ticker)
    df = _add_metadata_columns(df, instrument, ticker)

    logger.info("Successfully fetched %d rows with columns: %s", len(df), list(df.columns))

    return df


def _map_bloomberg_fields(
    df: pd.DataFrame,
    instrument: str,
    ticker: str,
) -> pd.DataFrame:
    """
    Map Bloomberg field names to schema-expected column names.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame from xbbg with Bloomberg field names.
    instrument : str
        Instrument type for field mapping.
    ticker : str
        Bloomberg ticker (used for multi-ticker responses).

    Returns
    -------
    pd.DataFrame
        DataFrame with renamed columns matching project schemas.

    Notes
    -----
    xbbg returns multi-index columns for multiple tickers: (ticker, field).
    For single ticker requests, we flatten to just field names.
    """
    # Handle xbbg multi-index columns: (ticker, field)
    if isinstance(df.columns, pd.MultiIndex):
        # Flatten by taking second level (field names)
        df.columns = df.columns.get_level_values(1)

    # Rename columns according to mapping
    field_map = FIELD_MAPPING[instrument]
    df = df.rename(columns=field_map)

    logger.debug("Mapped fields: %s -> %s", list(field_map.keys()), list(field_map.values()))

    return df


def _add_metadata_columns(
    df: pd.DataFrame,
    instrument: str,
    ticker: str,
) -> pd.DataFrame:
    """
    Add metadata columns required by schemas.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with mapped field columns.
    instrument : str
        Instrument type ('cdx', 'vix', 'etf').
    ticker : str
        Bloomberg ticker string to parse for metadata.

    Returns
    -------
    pd.DataFrame
        DataFrame with added metadata columns.

    Raises
    ------
    ValueError
        If ticker format cannot be parsed.

    Notes
    -----
    Extracts metadata from ticker strings:
    - CDX: 'CDX.NA.IG.5Y Index' -> index='CDX_IG', tenor='5Y'
    - ETF: 'HYG US Equity' -> ticker='HYG'
    - VIX: No metadata needed
    """
    if instrument == "cdx":
        # Parse CDX ticker: 'CDX.NA.IG.5Y Index' or 'CDX.NA.HY.5Y Index'
        parts = ticker.split(".")
        if len(parts) < 4 or not ticker.endswith(" Index"):
            raise ValueError(
                f"Invalid CDX ticker format: {ticker}. "
                "Expected format: 'CDX.NA.{{IG|HY|XO}}.{{tenor}} Index'"
            )

        index_type = parts[2]  # IG, HY, XO
        tenor_part = parts[3].split()[0]  # '5Y' from '5Y Index'

        df["index"] = f"CDX_{index_type}"
        df["tenor"] = tenor_part

        logger.debug("Added CDX metadata: index=%s, tenor=%s", df["index"].iloc[0], df["tenor"].iloc[0])

    elif instrument == "etf":
        # Parse ETF ticker: 'HYG US Equity' or 'LQD US Equity'
        parts = ticker.split()
        if len(parts) < 2 or parts[-1] != "Equity":
            raise ValueError(
                f"Invalid ETF ticker format: {ticker}. "
                "Expected format: '{{ticker}} US Equity'"
            )

        etf_ticker = parts[0]
        df["ticker"] = etf_ticker

        logger.debug("Added ETF metadata: ticker=%s", etf_ticker)

    # VIX doesn't need metadata columns
    elif instrument == "vix":
        pass

    return df
