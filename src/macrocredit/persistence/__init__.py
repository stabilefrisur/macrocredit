"""
Persistence layer for time series data and metadata management.

Provides clean abstractions for Parquet and JSON I/O, with a registry
system to track available datasets.
"""

from .parquet_io import save_parquet, load_parquet, list_parquet_files
from .json_io import save_json, load_json
from .registry import DataRegistry, DatasetEntry

__all__ = [
    "save_parquet",
    "load_parquet",
    "list_parquet_files",
    "save_json",
    "load_json",
    "DataRegistry",
    "DatasetEntry",
]
