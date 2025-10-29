"""
Data source configuration for pluggable data providers.

Defines source types (file, Bloomberg, API) and factory for provider resolution.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Any

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FileSource:
    """
    File-based data source (Parquet or CSV).

    Attributes
    ----------
    path : Path
        Path to the data file.
    """

    path: Path

    def __post_init__(self) -> None:
        """Convert path to Path object if string provided."""
        if isinstance(self.path, str):
            object.__setattr__(self, "path", Path(self.path))


@dataclass(frozen=True)
class BloombergSource:
    """
    Bloomberg Terminal/API data source.

    Attributes
    ----------
    host : str
        Bloomberg API host address.
    port : int
        Bloomberg API port.
    """

    host: str = "localhost"
    port: int = 8194


@dataclass(frozen=True)
class APISource:
    """
    Generic REST API data source.

    Attributes
    ----------
    endpoint : str
        API endpoint URL.
    params : dict[str, Any]
        Additional request parameters.
    """

    endpoint: str
    params: dict[str, Any] | None = None


# Union type for all data sources
DataSource = FileSource | BloombergSource | APISource


class DataProvider(Protocol):
    """
    Protocol for data provider implementations.

    All providers must implement fetch method with standardized signature.
    """

    def fetch(
        self,
        instrument: str,
        start_date: str | None = None,
        end_date: str | None = None,
        **params: Any,
    ) -> pd.DataFrame:
        """
        Fetch data for specified instrument and date range.

        Parameters
        ----------
        instrument : str
            Instrument identifier (e.g., 'CDX.NA.IG.5Y', 'VIX', 'HYG').
        start_date : str or None
            Start date in ISO format (YYYY-MM-DD).
        end_date : str or None
            End date in ISO format (YYYY-MM-DD).
        **params : Any
            Provider-specific parameters.

        Returns
        -------
        pd.DataFrame
            Data with DatetimeIndex.
        """
        ...


def resolve_provider(source: DataSource) -> str:
    """
    Resolve data source to provider type identifier.

    Parameters
    ----------
    source : DataSource
        Data source configuration.

    Returns
    -------
    str
        Provider type: 'file', 'bloomberg', or 'api'.

    Examples
    --------
    >>> resolve_provider(FileSource("data.parquet"))
    'file'
    >>> resolve_provider(BloombergSource())
    'bloomberg'
    """
    if isinstance(source, FileSource):
        return "file"
    elif isinstance(source, BloombergSource):
        return "bloomberg"
    elif isinstance(source, APISource):
        return "api"
    else:
        raise ValueError(f"Unknown source type: {type(source)}")
