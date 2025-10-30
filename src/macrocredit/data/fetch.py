"""
Unified data fetching interface with provider abstraction.

Fetch functions handle data acquisition from any source (file, Bloomberg, API)
with automatic validation and optional caching.
"""

import logging
from typing import Any

import pandas as pd

from ..config import DATA_DIR, CACHE_ENABLED, CACHE_TTL_DAYS, DEFAULT_DATA_SOURCES
from ..persistence.registry import DataRegistry, REGISTRY_PATH
from .cache import get_cached_data, save_to_cache
from .sources import DataSource, FileSource, BloombergSource, resolve_provider
from .providers.file import fetch_from_file
from .providers.bloomberg import fetch_from_bloomberg
from .validation import validate_cdx_schema, validate_vix_schema, validate_etf_schema

logger = logging.getLogger(__name__)


def _get_provider_fetch_function(source: DataSource):
    """
    Get fetch function for data source.

    Parameters
    ----------
    source : DataSource
        Data source configuration.

    Returns
    -------
    Callable
        Provider fetch function.
    """
    provider_type = resolve_provider(source)

    if provider_type == "file":
        return fetch_from_file
    elif provider_type == "bloomberg":
        return fetch_from_bloomberg
    else:
        raise ValueError(f"Unsupported provider: {provider_type}")


def fetch_cdx(
    source: DataSource | None = None,
    index_name: str | None = None,
    tenor: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    use_cache: bool = CACHE_ENABLED,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """
    Fetch CDX index spread data from configured source.

    Parameters
    ----------
    source : DataSource or None
        Data source. If None, uses default from config.
    index_name : str or None
        Filter to specific index (e.g., "CDX_IG", "CDX_HY").
    tenor : str or None
        Filter to specific tenor (e.g., "5Y", "10Y").
    start_date : str or None
        Start date in YYYY-MM-DD format.
    end_date : str or None
        End date in YYYY-MM-DD format.
    use_cache : bool, default CACHE_ENABLED
        Whether to use cache.
    force_refresh : bool, default False
        Force fetch from source, bypassing cache.

    Returns
    -------
    pd.DataFrame
        Validated CDX data with DatetimeIndex and columns:
        - spread: CDX spread in basis points
        - index: Index identifier (if present)
        - tenor: Tenor identifier (if present)

    Examples
    --------
    >>> from macrocredit.data import fetch_cdx, FileSource
    >>> df = fetch_cdx(FileSource("data/raw/cdx.parquet"), tenor="5Y")
    """
    source = source or DEFAULT_DATA_SOURCES.get("cdx")
    if source is None:
        raise ValueError("No source provided and no default configured for CDX")

    instrument = "cdx"
    cache_dir = DATA_DIR / "cache"

    # Check cache first
    if use_cache and not force_refresh:
        cached = get_cached_data(
            source,
            instrument,
            cache_dir,
            start_date=start_date,
            end_date=end_date,
            ttl_days=CACHE_TTL_DAYS.get(instrument),
            index_name=index_name,
            tenor=tenor,
        )
        if cached is not None:
            df = cached
            # Apply filters if needed
            if index_name is not None and "index" in df.columns:
                df = df[df["index"] == index_name]
            if tenor is not None and "tenor" in df.columns:
                df = df[df["tenor"] == tenor]
            return df

    # Fetch from source
    logger.info("Fetching CDX from %s", resolve_provider(source))
    fetch_fn = _get_provider_fetch_function(source)

    if isinstance(source, FileSource):
        df = fetch_fn(
            file_path=source.path,
            instrument=instrument,
            start_date=start_date,
            end_date=end_date,
        )
    elif isinstance(source, BloombergSource):
        # Construct Bloomberg ticker from filters
        ticker = _build_cdx_ticker(index_name, tenor)
        df = fetch_fn(
            ticker=ticker,
            instrument=instrument,
            start_date=start_date,
            end_date=end_date,
            host=source.host,
            port=source.port,
        )
    else:
        raise ValueError(f"Unsupported source type: {type(source)}")

    # Validate schema
    df = validate_cdx_schema(df)

    # Apply filters
    if index_name is not None:
        if "index" not in df.columns:
            raise ValueError("Cannot filter by index_name: 'index' column not found")
        df = df[df["index"] == index_name]
        logger.debug("Filtered to index=%s: %d rows", index_name, len(df))

    if tenor is not None:
        if "tenor" not in df.columns:
            raise ValueError("Cannot filter by tenor: 'tenor' column not found")
        df = df[df["tenor"] == tenor]
        logger.debug("Filtered to tenor=%s: %d rows", tenor, len(df))

    # Cache if enabled
    if use_cache:
        registry = DataRegistry(REGISTRY_PATH, DATA_DIR)
        save_to_cache(
            df,
            source,
            instrument,
            cache_dir,
            registry=registry,
            start_date=start_date,
            end_date=end_date,
            index_name=index_name,
            tenor=tenor,
        )

    logger.info("Fetched CDX data: %d rows, %s to %s", len(df), df.index.min(), df.index.max())
    return df


def fetch_vix(
    source: DataSource | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    use_cache: bool = CACHE_ENABLED,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """
    Fetch VIX volatility index data from configured source.

    Parameters
    ----------
    source : DataSource or None
        Data source. If None, uses default from config.
    start_date : str or None
        Start date in YYYY-MM-DD format.
    end_date : str or None
        End date in YYYY-MM-DD format.
    use_cache : bool, default CACHE_ENABLED
        Whether to use cache.
    force_refresh : bool, default False
        Force fetch from source, bypassing cache.

    Returns
    -------
    pd.DataFrame
        Validated VIX data with DatetimeIndex and columns:
        - close: VIX closing level

    Examples
    --------
    >>> from macrocredit.data import fetch_vix, FileSource
    >>> df = fetch_vix(FileSource("data/raw/vix.parquet"))
    """
    source = source or DEFAULT_DATA_SOURCES.get("vix")
    if source is None:
        raise ValueError("No source provided and no default configured for VIX")

    instrument = "vix"
    cache_dir = DATA_DIR / "cache"

    # Check cache first
    if use_cache and not force_refresh:
        cached = get_cached_data(
            source,
            instrument,
            cache_dir,
            start_date=start_date,
            end_date=end_date,
            ttl_days=CACHE_TTL_DAYS.get(instrument),
        )
        if cached is not None:
            return cached

    # Fetch from source
    logger.info("Fetching VIX from %s", resolve_provider(source))
    fetch_fn = _get_provider_fetch_function(source)

    if isinstance(source, FileSource):
        df = fetch_fn(
            file_path=source.path,
            instrument=instrument,
            start_date=start_date,
            end_date=end_date,
        )
    elif isinstance(source, BloombergSource):
        df = fetch_fn(
            ticker="VIX Index",
            instrument=instrument,
            start_date=start_date,
            end_date=end_date,
            host=source.host,
            port=source.port,
        )
    else:
        raise ValueError(f"Unsupported source type: {type(source)}")

    # Validate schema
    df = validate_vix_schema(df)

    # Cache if enabled
    if use_cache:
        registry = DataRegistry(REGISTRY_PATH, DATA_DIR)
        save_to_cache(
            df,
            source,
            instrument,
            cache_dir,
            registry=registry,
            start_date=start_date,
            end_date=end_date,
        )

    logger.info("Fetched VIX data: %d rows, %s to %s", len(df), df.index.min(), df.index.max())
    return df


def fetch_etf(
    source: DataSource | None = None,
    ticker: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    use_cache: bool = CACHE_ENABLED,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """
    Fetch credit ETF price data from configured source.

    Parameters
    ----------
    source : DataSource or None
        Data source. If None, uses default from config.
    ticker : str or None
        Filter to specific ticker (e.g., "HYG", "LQD").
    start_date : str or None
        Start date in YYYY-MM-DD format.
    end_date : str or None
        End date in YYYY-MM-DD format.
    use_cache : bool, default CACHE_ENABLED
        Whether to use cache.
    force_refresh : bool, default False
        Force fetch from source, bypassing cache.

    Returns
    -------
    pd.DataFrame
        Validated ETF data with DatetimeIndex and columns:
        - close: Closing price
        - ticker: ETF ticker symbol (if present)

    Examples
    --------
    >>> from macrocredit.data import fetch_etf, FileSource
    >>> df = fetch_etf(FileSource("data/raw/etf.parquet"), ticker="HYG")
    """
    source = source or DEFAULT_DATA_SOURCES.get("etf")
    if source is None:
        raise ValueError("No source provided and no default configured for ETF")

    instrument = "etf"
    cache_dir = DATA_DIR / "cache"

    # Check cache first
    if use_cache and not force_refresh:
        cached = get_cached_data(
            source,
            instrument,
            cache_dir,
            start_date=start_date,
            end_date=end_date,
            ttl_days=CACHE_TTL_DAYS.get(instrument),
            ticker=ticker,
        )
        if cached is not None:
            df = cached
            if ticker is not None and "ticker" in df.columns:
                df = df[df["ticker"] == ticker]
            return df

    # Fetch from source
    logger.info("Fetching ETF from %s", resolve_provider(source))
    fetch_fn = _get_provider_fetch_function(source)

    if isinstance(source, FileSource):
        df = fetch_fn(
            file_path=source.path,
            instrument=instrument,
            start_date=start_date,
            end_date=end_date,
        )
    elif isinstance(source, BloombergSource):
        if ticker is None:
            raise ValueError("ticker required for Bloomberg ETF fetch")
        df = fetch_fn(
            ticker=f"{ticker} US Equity",
            instrument=instrument,
            start_date=start_date,
            end_date=end_date,
            host=source.host,
            port=source.port,
        )
    else:
        raise ValueError(f"Unsupported source type: {type(source)}")

    # Validate schema
    df = validate_etf_schema(df)

    # Apply ticker filter
    if ticker is not None:
        if "ticker" not in df.columns:
            raise ValueError("Cannot filter by ticker: 'ticker' column not found")
        df = df[df["ticker"] == ticker]
        logger.debug("Filtered to ticker=%s: %d rows", ticker, len(df))

    # Cache if enabled
    if use_cache:
        registry = DataRegistry(REGISTRY_PATH, DATA_DIR)
        save_to_cache(
            df,
            source,
            instrument,
            cache_dir,
            registry=registry,
            start_date=start_date,
            end_date=end_date,
            ticker=ticker,
        )

    logger.info("Fetched ETF data: %d rows, %s to %s", len(df), df.index.min(), df.index.max())
    return df


def _build_cdx_ticker(index_name: str | None, tenor: str | None) -> str:
    """
    Construct Bloomberg ticker from CDX index and tenor.

    Parameters
    ----------
    index_name : str or None
        Index name (e.g., "CDX_IG", "CDX_HY").
    tenor : str or None
        Tenor (e.g., "5Y", "10Y").

    Returns
    -------
    str
        Bloomberg ticker.
    """
    if index_name is None or tenor is None:
        raise ValueError("index_name and tenor required for Bloomberg CDX fetch")

    # Example: CDX_IG_5Y -> "CDX.NA.IG.5Y Index"
    parts = index_name.split("_")
    if len(parts) >= 2:
        index_type = parts[1]  # IG, HY, XO
        ticker = f"CDX.NA.{index_type}.{tenor} Index"
    else:
        ticker = f"{index_name}.{tenor} Index"

    return ticker
